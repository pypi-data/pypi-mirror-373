#!/bin/bash

set -euo pipefail

RUN_DIR="$(pwd)"
TEMP_DIR=$(mktemp -d)
WORKING_DIR="$TEMP_DIR/working"

print_usage() {
    cat << EOM
Usage: $(basename $0) [options]

Misc:
    --print-ipa-details     Print IPA details and exit (Requires --ipa)
    --list-certs            List available certificates and exit

Required for and updates:
    --ipa <path>            Input IPA file
    --profile <path>        Provisioning profile path

Optional:
    --display-name <name>   New display name
    --icon <path>           New icon path
    --version <version>     New version number
    --build <number>        New build number
    --color <color hash>    New color, eg #112233
    --help                  Show this help message

Example:
    $(basename $0) --ipa MyApp.ipa \\
        --profile profile.mobileprovision \\
        --display-name "New Name" \\
        --version 1.2.0 --build 123
EOM
}

# Function to list signing certificates
list_certificates() {
    echo "Available signing certificates:"
    echo "-----------------------------"
    security find-identity -v -p codesigning | grep -o '".*"' | tr -d '"'
    echo "-----------------------------"
    echo
}

# Function to get certificate fingerprint from provisioning profile
get_certificate_from_profile() {
    local profile_path="$1"
    local profile_text
    profile_text=$(/usr/bin/security cms -D -i "$profile_path")

    # Get the first certificate from profile and get its fingerprint
    echo "$profile_text" | xmllint --xpath "//data/text()" - 2>/dev/null | \
    while read -r cert_data
    do
        if [ -n "$cert_data" ]
        then
            # Get the fingerprint of the certificate from the profile
            echo "$cert_data" | base64 --decode |
                openssl x509 -inform der -noout -fingerprint |
                cut -d= -f2 |
                sed 's/://g'
            break  # Just need the first one
        fi
    done
}

# Compare entitlements and check for mismatches
verify_entitlements_compatibility() {
    local profile_path="$1"
    local app_path="$2"

    echo "Checking entitlements compatibility..."
    echo "------------"

    # Debug file locations
    echo "Profile path: $(readlink -f "$profile_path")"
    echo "App path: $(readlink -f "$app_path")"

    # Get profile entitlements
    local temp_profile_plist="$TEMP_DIR/profile_ents.plist"
    local temp_binary_plist="$TEMP_DIR/binary_ents.plist"

    # Extract and normalize profile entitlements with error handling
    echo "Extracting profile entitlements..."
    local profile_text
    profile_text=$(/usr/bin/security cms -D -i "$profile_path" 2>/dev/null)
    if [ $? -ne 0 ]
    then
        echo "ERROR: Could not decode provisioning profile at: $profile_path"
        echo "Profile stat: $(ls -l "$profile_path")"
        return 1
    fi

    echo "Profile decoded successfully, extracting entitlements..."
    if ! echo "$profile_text" | \
        /usr/libexec/PlistBuddy -x -c "Print :Entitlements" /dev/stdin | \
        plutil -convert xml1 - -o "$temp_profile_plist" 2>/dev/null
    then
        echo "ERROR: Could not extract entitlements section"
        echo "Available plist keys:"
        echo "$profile_text" | /usr/libexec/PlistBuddy -c "Print" /dev/stdin 2>/dev/null | grep "^    \"" || true
        return 1
    fi

    echo "Extracting binary entitlements..."
    if ! codesign -d --entitlements :- "$app_path" | \
        plutil -convert xml1 - -o "$temp_binary_plist" 2>/dev/null
    then
        echo "ERROR: Could not extract entitlements from binary at: $app_path"
        echo "Binary stat: $(ls -l "$app_path")"
        return 1
    fi
    echo "Binary entitlements extracted successfully"

python - "$temp_profile_plist" "$temp_binary_plist" <<'EOF'
import sys
import plistlib

# Read plists
try:
    with open(sys.argv[1], 'rb') as f:
        profile_ents = plistlib.load(f)
except Exception as e:
    print(f"Warning: Could not read profile entitlements: {e}", file=sys.stderr)
    sys.exit(1)

try:
    with open(sys.argv[2], 'rb') as f:
        binary_ents = plistlib.load(f)
except Exception as e:
    print(f"Warning: Could not read binary entitlements: {e}", file=sys.stderr)
    sys.exit(1)

# Get all unique keys
all_keys = sorted(set(list(profile_ents.keys()) + list(binary_ents.keys())))

def print_comparison_header():
    print("\nEntitlements Comparison:")
    print("=" * 25)
    print(f"{'Entitlement':50s} | {'New':10s} | {'Original':10s}")
    print("-" * 50 + " + " + "-" * 10 + " + " + "-" * 10)

def format_value(value, max_length=10):  # Changed max_length to match column width
    str_value = str(value)
    return str_value[:max_length] + "..." if len(str_value) > max_length else str_value

def format_row(key, p_val, b_val, color):
    return f"{color}{key:50s} | {p_val:10s} | {b_val:10s}\033[0m"

def is_valid_value(value):
    return value in ("---", True, False)

all_keys = set(profile_ents.keys()) | set(binary_ents.keys())
has_mismatch = False

print_comparison_header()

for key in all_keys:
    profile_value = profile_ents.get(key, "---")
    binary_value = binary_ents.get(key, "---")

    # Skip invalid values
    if not (is_valid_value(profile_value) and is_valid_value(binary_value)):
        continue

    # Skip if both missing
    if profile_value == "---" and binary_value == "---":
        continue

    match = profile_value == binary_value

    # Format values for display
    p_val = format_value(profile_value)
    b_val = format_value(binary_value)

    # Use green for matches, red for mismatches
    color = "\033[32m" if match else "\033[31m"
    print(format_row(key, p_val, b_val, color))

    if not match:
        has_mismatch = True

print("=========================")
sys.exit(1 if has_mismatch else 0)
EOF

    local has_mismatch=$?

    if [ $has_mismatch -eq 1 ]
    then
        echo
        echo "WARNING: Entitlements mismatch detected"
        echo "The provisioning profile contains entitlements that are not"
        echo "present in the app binary."
        echo
        echo "This script will overwrite the entitlements in the app binary"
        echo "with the entitlements from the provisioning profile."
        echo
        echo "Please make sure the new identifier (appid) has the same"
        echo "entitlements checked as the original identifier does."
        return 0
    fi

    echo
    echo "SUCCESS Entitlements compatibility check passed"
    echo "------------"
    echo
    return 0
}

# Function to validate certificate exists in keychain
validate_certificate() {
    local fingerprint="$1"
    local cert_info

    # Look for this specific certificate fingerprint
    cert_info=$(security find-certificate -a -Z |
        grep -e SHA-1 -e keychain |
        grep -B 1 "$fingerprint" || true)

    if [ -z "$cert_info" ]
    then
        echo "Error: Required certificate not found in any keychain"
        echo "Fingerprint: $fingerprint"
        exit 1
    fi

    # Show which keychain it was found in
    local keychain
    keychain=$(echo "$cert_info" | grep "keychain:" | awk '{print $2}')
    echo "Found certificate in keychain: $keychain"

    export CERTIFICATE_FINGERPRINT="$fingerprint"
}

get_profile_date_for_output_file() {
    local profile_path="$APP_DIR/embedded.mobileprovision"
    local profile_text
    profile_text=$(/usr/bin/security cms -D -i "$APP_DIR/embedded.mobileprovision")

    local DATE
    DATE="$(/usr/libexec/PlistBuddy -c "Print :ExpirationDate" \
        /dev/stdin <<< "$profile_text" 2>/dev/null || true)"

    date -j -f "%a %b %d %H:%M:%S %Z %Y" "$DATE" "+%y%m%d" 2>/dev/null
}

get_profile_bundle_id() {

    local profile_path="$APP_DIR/embedded.mobileprovision"
    local profile_text
    profile_text=$(/usr/bin/security cms -D -i "$APP_DIR/embedded.mobileprovision")

    /usr/libexec/PlistBuddy \
        -c "Print :Entitlements:application-identifier" \
        /dev/stdin <<< "$profile_text" 2>/dev/null |
            sed 's/^[A-Z0-9]*\.//'
}

print_provisioning_details() {
    local profile_path="$APP_DIR/embedded.mobileprovision"
    if [ ! -f "$profile_path" ]
    then
        echo "No provisioning profile found"
        return 0
    fi

    echo "Provisioning Profile Details:"

    local profile_text
    profile_text=$(/usr/bin/security cms -D -i "$profile_path")

    echo "  Name: $(/usr/libexec/PlistBuddy -c "Print :Name" /dev/stdin \
        <<< "$profile_text" 2>/dev/null || true)"
    echo "  Bundle Identifier: $(/usr/libexec/PlistBuddy -c "Print :Entitlements:application-identifier" /dev/stdin \
        <<< "$profile_text" 2>/dev/null | sed 's/^[A-Z0-9]*\.//' || true)"
    echo "  Expiration: $(/usr/libexec/PlistBuddy -c "Print :ExpirationDate" \
        /dev/stdin <<< "$profile_text" 2>/dev/null || true)"

    echo "  Certificates:"
    echo "$profile_text" | xmllint --xpath "//data/text()" - 2>/dev/null | \
    while read -r cert_data
    do
        local cert_info
        cert_info=$(echo "$cert_data" | base64 --decode | \
                   openssl x509 -inform der -noout -subject -enddate \
                   2>/dev/null || true)
        if [ -n "$cert_info" ]
        then
            local subject
            subject=$(echo "$cert_info" | grep "subject=" | sed 's/subject= //')
            local expiry
            expiry=$(echo "$cert_info" | grep "notAfter=" | sed 's/notAfter=//')
            echo "    Subject: $subject"
            echo "    Expires: $expiry"
            echo ""
        fi
    done
}

get_version() {
   /usr/libexec/PlistBuddy \
        -c "Print :CFBundleShortVersionString" \
        "$APP_DIR/Info.plist" 2>/dev/null
}

get_build() {
    /usr/libexec/PlistBuddy \
        -c "Print :CFBundleVersion" \
        "$APP_DIR/Info.plist" 2>/dev/null
}

get_bundle_id() {
    /usr/libexec/PlistBuddy \
        -c "Print :CFBundleIdentifier" \
        "$APP_DIR/Info.plist" 2>/dev/null
}

print_ipa_details() {
    echo "IPA Details:"
    echo "------------"
    if ! [ -d "$APP_DIR" ]
    then
        echo "No .app directory found to extract details"
        return 0
    fi

    echo "Bundle ID: $(/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" \
        "$APP_DIR/Info.plist" 2>/dev/null || true)"
    echo "Version: $(/usr/libexec/PlistBuddy \
        -c "Print :CFBundleShortVersionString" \
        "$APP_DIR/Info.plist" 2>/dev/null || true)"

    echo "Build: $(get_build)"

    local display_name
    display_name=$(/usr/libexec/PlistBuddy -c "Print :CFBundleDisplayName" \
        "$APP_DIR/Info.plist" 2>/dev/null || true)
    if [ -z "$display_name" ]
    then
        display_name=$(/usr/libexec/PlistBuddy -c "Print :CFBundleName" \
            "$APP_DIR/Info.plist" 2>/dev/null || true)
    fi
    echo "Display Name: $display_name"

    local signing_info
    signing_info=$(codesign -dvv "$APP_DIR" 2>&1 | grep "Authority" | head -n1)
    if [ -n "$signing_info" ]
    then
        echo "Signing Identity: ${signing_info#*=}"
    fi

    echo ""
    if [ -f "$APP_DIR/embedded.mobileprovision" ]
    then
        print_provisioning_details
    else
        echo "No embedded provisioning profile found"
    fi
    echo "------------"
    echo
}

cleanup_temp_dir() {
    rm -rf "$TEMP_DIR"
}

unzip_ipa() {
    local ipa_file="$INPUT_IPA"
    local temp_dir="$TEMP_DIR"
    local working_dir="$temp_dir/working"

    if [ ! -f "$ipa_file" ]
    then
        echo "Error: IPA file not found: $ipa_file"
        exit 1
    fi

    mkdir -p "$working_dir"

    if ! unzip -q "$ipa_file" -d "$working_dir"
    then
        echo "Error: Failed to unzip IPA file"
        cleanup_temp_dir
        exit 1
    fi

    APP_DIR=$(find "$working_dir/Payload" -name "*.app" -type d)
    export APP_DIR
    if [ -z "$APP_DIR" ]
    then
        echo "Error: Could not find .app directory in IPA"
        cleanup_temp_dir
        exit 1
    fi
}

find_and_replace_in_ng_app_js_files() {

    pushd "$APP_DIR"/public > /dev/null
    local OLD_STR="$1"
    local NEW_STR="$2"
    local ESCAPED_OLD=$(echo "$OLD_STR" | sed 's/\./\\./g')
    local ESCAPED_NEW=$(echo "$NEW_STR" | sed 's/\./\\./g')

    echo "Replacing: ${OLD_STR} with ${NEW_STR}"
    echo "------------"


    # Find matching js/json files and show before
    echo "Before:"
    if ! find . -type f \( -name "*.js" -o -name "*.json" \) -exec grep -l -F "$OLD_STR" {} \; |
            xargs awk \
            "match(\$0, /.{0,50}${ESCAPED_OLD}.{0,50}/) {print substr(\$0, RSTART, RLENGTH)}"
    then
        echo
        echo "WARNING: Could not find string to replace |$OLD_STR|"
        echo
        popd > /dev/null
        return
    fi

    echo

    # Do the replacement
    find . -type f \( -name "*.js" -o -name "*.json" \) -exec grep -l -F "$OLD_STR" {} \; |
    while read -r file
    do
        echo "Replacing in $file"
        gsed -i "s/${ESCAPED_OLD}/${NEW_STR}/g" "$file"
    done

    # Show after
    echo -e "\nAfter:"
    find . -type f \( -name "*.js" -o -name "*.json" \) -exec grep -l -F "$NEW_STR" {} \; |
        xargs awk \
        "match(\$0, /.{0,50}${ESCAPED_NEW}.{0,50}/) {print substr(\$0, RSTART, RLENGTH)}"

    popd > /dev/null
    echo "------------"
    echo
}

update_asset_catalog() {
    local new_icon="$1"
    local app_dir="$2"

    if ! [ -f "$app_dir/Assets.car" ]
    then
        echo "No Assets.car found"
        return 0
    fi

    echo "Updating Assets.car..."
    echo "------------"

    # Create temporary directories for asset catalog and output
    local catalog_base="$TEMP_DIR/AssetCatalog"
    local catalog_dir="$catalog_base/Assets.xcassets"
    local output_dir="$TEMP_DIR/Output"
    mkdir -p "$catalog_dir/AppIcon.appiconset"
    mkdir -p "$output_dir"

    # Create top-level Contents.json
    cat > "$catalog_dir/Contents.json" << 'EOF'
{
  "info" : {
    "version" : 1,
    "author" : "xcode"
  }
}
EOF

    # Create Contents.json for the app icon set
    cat > "$catalog_dir/AppIcon.appiconset/Contents.json" << 'EOF'
{
  "images": [
    {
      "filename": "AppIcon20x20@2x.png",
      "idiom": "iphone",
      "scale": "2x",
      "size": "20x20"
    },
    {
      "filename": "AppIcon20x20@3x.png",
      "idiom": "iphone",
      "scale": "3x",
      "size": "20x20"
    },
    {
      "filename": "AppIcon29x29@2x.png",
      "idiom": "iphone",
      "scale": "2x",
      "size": "29x29"
    },
    {
      "filename": "AppIcon29x29@3x.png",
      "idiom": "iphone",
      "scale": "3x",
      "size": "29x29"
    },
    {
      "filename": "AppIcon40x40@2x.png",
      "idiom": "iphone",
      "scale": "2x",
      "size": "40x40"
    },
    {
      "filename": "AppIcon40x40@3x.png",
      "idiom": "iphone",
      "scale": "3x",
      "size": "40x40"
    },
    {
      "filename": "AppIcon60x60@2x.png",
      "idiom": "iphone",
      "scale": "2x",
      "size": "60x60"
    },
    {
      "filename": "AppIcon60x60@3x.png",
      "idiom": "iphone",
      "scale": "3x",
      "size": "60x60"
    },
    {
      "filename": "AppIcon20x20.png",
      "idiom": "ipad",
      "scale": "1x",
      "size": "20x20"
    },
    {
      "filename": "AppIcon20x20@2x~ipad.png",
      "idiom": "ipad",
      "scale": "2x",
      "size": "20x20"
    },
    {
      "filename": "AppIcon29x29.png",
      "idiom": "ipad",
      "scale": "1x",
      "size": "29x29"
    },
    {
      "filename": "AppIcon29x29@2x~ipad.png",
      "idiom": "ipad",
      "scale": "2x",
      "size": "29x29"
    },
    {
      "filename": "AppIcon40x40.png",
      "idiom": "ipad",
      "scale": "1x",
      "size": "40x40"
    },
    {
      "filename": "AppIcon40x40@2x~ipad.png",
      "idiom": "ipad",
      "scale": "2x",
      "size": "40x40"
    },
    {
      "filename": "AppIcon76x76.png",
      "idiom": "ipad",
      "scale": "1x",
      "size": "76x76"
    },
    {
      "filename": "AppIcon76x76@2x~ipad.png",
      "idiom": "ipad",
      "scale": "2x",
      "size": "76x76"
    },
    {
      "filename": "AppIcon83.5x83.5@2x~ipad.png",
      "idiom": "ipad",
      "scale": "2x",
      "size": "83.5x83.5"
    },
    {
      "filename": "AppIcon1024x1024.png",
      "idiom": "ios-marketing",
      "scale": "1x",
      "size": "1024x1024"
    }
  ],
  "info": {
    "author": "xcode",
    "version": 1
  }
}
EOF

    # Generate all icon sizes
    echo "Generating icon sizes..."

    # iPhone icons
    sips -z 40 40 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon20x20@2x.png" >/dev/null 2>&1 || return 1
    sips -z 60 60 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon20x20@3x.png" >/dev/null 2>&1 || return 1
    sips -z 58 58 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon29x29@2x.png" >/dev/null 2>&1 || return 1
    sips -z 87 87 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon29x29@3x.png" >/dev/null 2>&1 || return 1
    sips -z 80 80 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon40x40@2x.png" >/dev/null 2>&1 || return 1
    sips -z 120 120 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon40x40@3x.png" >/dev/null 2>&1 || return 1
    sips -z 120 120 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon60x60@2x.png" >/dev/null 2>&1 || return 1
    sips -z 180 180 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon60x60@3x.png" >/dev/null 2>&1 || return 1

    # iPad icons
    sips -z 20 20 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon20x20.png" >/dev/null 2>&1 || return 1
    sips -z 40 40 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon20x20@2x~ipad.png" >/dev/null 2>&1 || return 1
    sips -z 29 29 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon29x29.png" >/dev/null 2>&1 || return 1
    sips -z 58 58 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon29x29@2x~ipad.png" >/dev/null 2>&1 || return 1
    sips -z 40 40 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon40x40.png" >/dev/null 2>&1 || return 1
    sips -z 80 80 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon40x40@2x~ipad.png" >/dev/null 2>&1 || return 1
    sips -z 76 76 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon76x76.png" >/dev/null 2>&1 || return 1
    sips -z 152 152 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon76x76@2x~ipad.png" >/dev/null 2>&1 || return 1
    sips -z 167 167 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon83.5x83.5@2x~ipad.png" >/dev/null 2>&1 || return 1

    # App Store icon
    sips -z 1024 1024 "$new_icon" --out "$catalog_dir/AppIcon.appiconset/AppIcon1024x1024.png" >/dev/null 2>&1 || return 1

    # Compile the asset catalog
    echo "Compiling asset catalog..."
    if ! xcrun actool \
        --compile "$output_dir" \
        --platform iphoneos \
        --minimum-deployment-target 12.0 \
        --app-icon AppIcon \
        --output-format human-readable-text \
        --output-partial-info-plist "$output_dir/partial.plist" \
        --enable-on-demand-resources NO \
        --target-device iphone \
        --target-device ipad \
        --development-region en \
        --compress-pngs \
        "$catalog_dir"
    then
        echo "Failed to compile asset catalog"
        cat "$output_dir/partial.plist" 2>/dev/null || true
        return 1
    fi

    # Check if Assets.car and required files were created
    local expected_files=(
        "Assets.car"
        "AppIcon60x60@2x.png"
        "AppIcon76x76@2x~ipad.png"
        "partial.plist"
    )

    for file in "${expected_files[@]}"
    do
        if ! [ -f "$output_dir/$file" ]
        then
            echo "Error: Expected file not created: $file"
            return 1
        fi
    done

    # Get sizes of original and new Assets.car
    local orig_size=0
    local new_size=0
    if [ -f "$app_dir/Assets.car" ]
    then
        orig_size=$(stat -f %z "$app_dir/Assets.car")
    fi
    new_size=$(stat -f %z "$output_dir/Assets.car")
    echo "Original Assets.car size: $orig_size bytes"
    echo "New Assets.car size: $new_size bytes"

    # Replace the original Assets.car
    if ! mv "$output_dir/Assets.car" "$app_dir/Assets.car"
    then
        echo "Failed to replace Assets.car"
        return 1
    fi

    echo "Successfully updated Assets.car"
    echo "------------"
    echo

    return 0
}


update_app_icon() {
    local new_icon="$1"
    local app_dir="$2"
    local success=false

    # Validate input icon
    if ! [ -f "$new_icon" ]
    then
        echo "Error: Icon file not found: $new_icon"
        return 1
    fi

    echo "Updating app icon..."
    echo "------------"

    # Track number of icons updated
    local icons_updated=0
    local icons_failed=0

    # Function to resize and replace an icon
    replace_icon() {
        local source="$1"
        local target="$2"
        local dimensions="$3"

        # Create temporary file for the resized icon
        local temp_icon=$(mktemp).png

        # Resize the icon and ensure squared aspect ratio
        if ! sips -z ${dimensions/x/ } ${dimensions/x/ } "$source" --out "$temp_icon" >/dev/null 2>&1
        then
            echo "Failed to resize icon to $dimensions"
            rm -f "$temp_icon"
            return 1
        fi

        # Replace the target icon
        if ! mv "$temp_icon" "$target"
        then
            echo "Error: Failed to replace icon: $target"
            rm -f "$temp_icon"
            return 1
        fi

        # Update time and date on icon and clear any extended attributes
        touch "$target"
        xattr -c "$target" 2>/dev/null || true

        return 0
    }

    # Get iPhone icon references
    iphone_icons=()
    while read -r name
    do
        [ -n "$name" ] && iphone_icons[${#iphone_icons[@]}]="$name"
    done << EOF
$(/usr/libexec/PlistBuddy -c "Print :CFBundleIcons:CFBundlePrimaryIcon:CFBundleIconFiles" "$app_dir/Info.plist" 2>/dev/null | grep -v "Array {" | grep -v "}" | sed 's/^[[:space:]]*//' || true)
EOF

    # Get iPad icon references
    ipad_icons=()
    while read -r name
    do
        [ -n "$name" ] && ipad_icons[${#ipad_icons[@]}]="$name"
    done << EOF
$(/usr/libexec/PlistBuddy -c "Print :CFBundleIcons~ipad:CFBundlePrimaryIcon:CFBundleIconFiles" "$app_dir/Info.plist" 2>/dev/null | grep -v "Array {" | grep -v "}" | sed 's/^[[:space:]]*//' || true)
EOF

    # Keep track of processed files to avoid duplicates
    processed_files=""

    # Process iPhone icons
    for base_name in "${iphone_icons[@]}"
    do
        for scale in "@2x.png" "@3x.png"
        do
            icon_path="$app_dir/$base_name$scale"

            # Skip if we've already processed this file or if it doesn't exist
            if echo "$processed_files" | grep -q ":$icon_path:" || ! [ -f "$icon_path" ]
            then
                continue
            fi

            processed_files="$processed_files:$icon_path:"

            # Get dimensions from the actual file
            dimensions=$(sips -g pixelHeight -g pixelWidth "$icon_path" |
                       grep -E 'pixel(Height|Width)' |
                       awk '{print $2}' | tr '\n' 'x' |
                       sed 's/x$//')

            echo "Processing icon: $(basename "$icon_path") ($dimensions)"
            if replace_icon "$new_icon" "$icon_path" "$dimensions"
            then
                icons_updated=$((icons_updated + 1))
                success=true
            else
                icons_failed=$((icons_failed + 1))
            fi
        done
    done

    # Process iPad icons
    for base_name in "${ipad_icons[@]}"
    do
        for scale in "@2x~ipad.png"
        do
            icon_path="$app_dir/$base_name$scale"

            # Skip if we've already processed this file or if it doesn't exist
            if echo "$processed_files" | grep -q ":$icon_path:" || ! [ -f "$icon_path" ]
            then
                continue
            fi

            processed_files="$processed_files:$icon_path:"

            # Get dimensions from the actual file
            dimensions=$(sips -g pixelHeight -g pixelWidth "$icon_path" |
                       grep -E 'pixel(Height|Width)' |
                       awk '{print $2}' | tr '\n' 'x' |
                       sed 's/x$//')

            echo "Processing icon: $(basename "$icon_path") ($dimensions)"
            if replace_icon "$new_icon" "$icon_path" "$dimensions"
            then
                icons_updated=$((icons_updated + 1))
                success=true
            else
                icons_failed=$((icons_failed + 1))
            fi
        done
    done

    # Update asset catalog if present
    if [ -f "$app_dir/Assets.car" ]
    then
        if ! update_asset_catalog "$new_icon" "$app_dir"
        then
            echo "Warning: Failed to update asset catalog"
        fi
    fi

    # Check if we found and updated any icons
    if [ $icons_updated -eq 0 ]
    then
        echo "Error: No icons found to update"
        return 1
    fi

    echo "Icon update complete:"
    echo "- Successfully updated: $icons_updated icons"
    if [ $icons_failed -gt 0 ]
    then
        echo "- Failed to update: $icons_failed icons"
    fi

    echo "------------"
    echo

    return $([ $success = true ])
}

# Track if any modifications are requested
MODIFICATIONS_REQUESTED=false

while [[ $# -gt 0 ]]
do
    case "$1" in
        --ipa)
            INPUT_IPA="$2"
            shift 2
            ;;
        --profile)
            PROVISIONING_PROFILE="$2"
            MODIFICATIONS_REQUESTED=true
            shift 2
            ;;
        --display-name)
            NEW_NAME="$2"
            MODIFICATIONS_REQUESTED=true
            shift 2
            ;;
        --icon)
            NEW_ICON="$2"
            MODIFICATIONS_REQUESTED=true
            shift 2
            ;;
        --version)
            NEW_VERSION="$2"
            MODIFICATIONS_REQUESTED=true
            shift 2
            ;;
        --build)
            NEW_BUILD="$2"
            MODIFICATIONS_REQUESTED=true
            shift 2
            ;;
        --color)
            NEW_COLOR="$2"
            MODIFICATIONS_REQUESTED=true
            shift 2
            ;;
        --print-ipa-details)
            OPT_PRINT_IPA_DETAILS=1
            shift 1
            ;;
        --list-certs)
            list_certificates
            exit 0
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

if [ -z "${INPUT_IPA:-}" ]
then
    echo "Error: Missing required argument: --ipa"
    print_usage
    exit 1
fi

if $MODIFICATIONS_REQUESTED && [ -z "${PROVISIONING_PROFILE:-}" ]
then
    echo "Error: Missing required argument: --profile"
    print_usage
    exit 1
fi

# List available certificates for reference
list_certificates

unzip_ipa

OLD_VERSION=$(get_version)
OLD_BUILD=$(get_build)
OLD_BUNDLE_ID=$(get_bundle_id)

echo "Original IPA details:"
print_ipa_details

if ! $MODIFICATIONS_REQUESTED
then
    cleanup_temp_dir "$TEMP_DIR"
    exit 0
fi

# Set NEW_BUILD since modifications were requested
NEW_BUILD=$(date -u "+%y%m%d%H%M")

if [ -n "${NEW_NAME:-}" ]
then
    echo "Updating app name to: $NEW_NAME"
    echo "------------"
    echo
    /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName $NEW_NAME" \
        "$APP_DIR/Info.plist"
    /usr/libexec/PlistBuddy -c "Set :CFBundleName $NEW_NAME" \
        "$APP_DIR/Info.plist"
fi

if [ -n "${NEW_ICON:-}" ]
then
    if ! update_app_icon "$NEW_ICON" "$APP_DIR"
    then
        echo "Error: Failed to update app icon"
        cleanup_temp_dir
        exit 1
    fi
fi

if [ -n "${NEW_VERSION:-}" ]
then
    echo "Updating version to: $NEW_VERSION"
    /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $NEW_VERSION" \
        "$APP_DIR/Info.plist"

    find_and_replace_in_ng_app_js_files "$OLD_VERSION" "$NEW_VERSION"
fi

if [ -n "${NEW_BUILD:-}" ]
then
    echo "Updating build number to: b$NEW_BUILD"
    /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $NEW_BUILD" \
        "$APP_DIR/Info.plist"

    find_and_replace_in_ng_app_js_files " b$OLD_BUILD " " b$NEW_BUILD "
fi

if [ -n "${NEW_COLOR:-}" ]
then
    echo "Updating background color to: $NEW_COLOR"
    find_and_replace_in_ng_app_js_files \
        "background-color:#26abe2;" \
        "background-color:${NEW_COLOR};"
fi


if [ -n "${PROVISIONING_PROFILE:-}" ]
then

    # Verify entitlements compatibility
    if ! verify_entitlements_compatibility "$PROVISIONING_PROFILE" "$APP_DIR"
    then
        cleanup_temp_dir
        exit 1
    fi

    # --- Install Provisioning Profile
    rm -f "$APP_DIR/embedded.mobileprovision" 2>/dev/null
    cp "$PROVISIONING_PROFILE" "$APP_DIR/embedded.mobileprovision"

    # --- Update Bundle ID
    NEW_BUNDLE_ID=$(get_profile_bundle_id)

    if [ -z "$NEW_BUNDLE_ID" ]
    then
        echo "Error: Could not extract bundle ID from provisioning profile"
        cleanup_temp_dir
        exit 1
    fi

    echo "Setting bundle ID from profile: $NEW_BUNDLE_ID"
    /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier $NEW_BUNDLE_ID" \
        "$APP_DIR/Info.plist"

    # --- Codesign Binaries
    # Get the certificate fingerprint from the provisioning profile
    CERTIFICATE_FINGERPRINT=$(get_certificate_from_profile "$PROVISIONING_PROFILE")

    if [ -z "$CERTIFICATE_FINGERPRINT" ]
    then
       echo "Error: Could not extract certificate from provisioning profile"
       cleanup_temp_dir
       exit 1
    fi

    echo "Using certificate with fingerprint: $CERTIFICATE_FINGERPRINT"
    validate_certificate "$CERTIFICATE_FINGERPRINT"

    # Extract entitlements from provisioning profile
    echo "Extracting entitlements from provisioning profile"
    ENTITLEMENTS_FILE="$TEMP_DIR/entitlements.plist"
    security cms -D -i "$PROVISIONING_PROFILE" | \
       plutil -extract Entitlements xml1 -o "$ENTITLEMENTS_FILE" -

    rm -rf "$APP_DIR/_CodeSignature" 2>/dev/null

    if [ -d "$APP_DIR/PlugIns" ]
    then
       find "$APP_DIR/PlugIns" -type d -name "*.appex" | \
       while read -r plugin
       do
           echo "Signing plugin: $plugin"
           codesign --force --sign "$CERTIFICATE_FINGERPRINT" \
               --entitlements "$ENTITLEMENTS_FILE" "$plugin"
       done
    fi

    find "$APP_DIR" -name "*.bundle" -type d | \
    while read -r bundle
    do
       echo "Signing bundle: $bundle"
       codesign --force --sign "$CERTIFICATE_FINGERPRINT" \
           --entitlements "$ENTITLEMENTS_FILE" "$bundle"
    done

    if [ -d "$APP_DIR/Frameworks" ]
    then
       find "$APP_DIR/Frameworks" -name "*.framework" -o -name "*.dylib" | \
       while read -r framework
       do
           echo "Signing framework: $framework"
           codesign --force --sign "$CERTIFICATE_FINGERPRINT" \
               --entitlements "$ENTITLEMENTS_FILE" "$framework" \
               2>&1 | grep -v 'replacing existing signature' || true
       done
    fi

    echo "Signing app: $(basename $APP_DIR)"
    codesign --force --sign "$CERTIFICATE_FINGERPRINT" \
       --entitlements "$ENTITLEMENTS_FILE" "$APP_DIR" \
       2>&1 | grep -v 'replacing existing signature' || true

fi


OUT_V="_v$(get_version)"
OUT_B="_b$(get_build)"
OUT_EXP="_exp$(get_profile_date_for_output_file)"

OUTPUT_BASE="$(get_bundle_id)${OUT_V}${OUT_B}${OUT_EXP}"
OUTPUT_IPA="${OUTPUT_BASE}.ipa"
OUTPUT_TXT="${OUTPUT_BASE}.txt"

echo
echo "Modified IPA details:"
print_ipa_details | tee "${RUN_DIR}/${OUTPUT_TXT}"

echo "Verifying signature..."
if ! codesign --verify -vvv --deep "$APP_DIR"
then
    echo "❌  ERROR: Could not verify codesigning" >&2
    cleanup_temp_dir
    exit 1
fi

pushd "$WORKING_DIR" > /dev/null
zip -qr "$TEMP_DIR/updated.ipa" "Payload"
popd > /dev/null

mv "$TEMP_DIR/updated.ipa" "${RUN_DIR}/$OUTPUT_IPA"


cleanup_temp_dir

echo
echo "Successfully resigned IPA: $OUTPUT_IPA"
echo