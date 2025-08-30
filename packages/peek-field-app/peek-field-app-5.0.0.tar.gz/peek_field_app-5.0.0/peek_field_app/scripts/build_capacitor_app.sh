#!/usr/bin/env bash

set -o nounset
set -o errexit
# TODO
# inspect app version, build version

# parameter defaults
# public version on App Store page
XCODE_APP_VERSION='0.0.0'
# CI job number, internal version for technical purposes
XCODE_BUILD_VERSION='b00000'
# app bundle identifier
XCODE_APP_BUNDLE_IDENTIFIER='com.synerty.peek'
# Apple Developer Team ID
XCODE_DEVELOPEMENT_TEAM_ID='Q55F59LQD3'
# UUID of mobile provisioning profile
XCODE_PROVISIONING_PROFILE_NAME='Synerty iOS Development'

# script default
XCODE_APP_NAME='App'
VERIFY_SIGN=1

# #########################################################################
# DO NOT CHANGE ANYTHING AFTER THIS LINE UNLESS YOU KNOW WHAT YOU ARE DOING
# #########################################################################

XCODE_PROFILE_DIR="${HOME}/Library/MobileDevice/Provisioning Profiles"
SCRIPT_PATH="$(cd "$(dirname $0)"; pwd -P)"
NOW=$(date -u +%Y-%m-%d_%H%M%SUTC)

function parseArguments() {
    # https://stackoverflow.com/a/61055114

    # Example:
    # parseArguments "${@}"
    # echo "${ARG_0}" -> package
    # echo "${ARG_1}" -> install
    # echo "${ARG_PACKAGE}" -> "name with space"
    # echo "${ARG_BUILD}" -> 1 (true)
    # echo "${ARG_ARCHIVE}" -> 1 (true)
    PREVIOUS_ITEM=''
    COUNT=0
    for CURRENT_ITEM in "$@"
    do
    if [[ ${CURRENT_ITEM} == "--"* ]]
    then
        # could
        # set this to empty string and check with [ -z "${ARG_ITEM-x}" ]
        # if it's set, but empty.
        printf -v "ARG_$(formatArgument "${CURRENT_ITEM}")" "%s" "1"
    else
        if [[ $PREVIOUS_ITEM == "--"* ]]
        then
            printf -v "ARG_$(formatArgument "${PREVIOUS_ITEM}")" "%s" \
               "${CURRENT_ITEM}"
        else
            printf -v "ARG_${COUNT}" "%s" "${CURRENT_ITEM}"
        fi
    fi

    PREVIOUS_ITEM="${CURRENT_ITEM}"
    (( COUNT++ ))
    done
}

# Format argument.
function formatArgument() {
    # Capitalize.
    ARGUMENT="$(tr '[:lower:]' '[:upper:]' <<< "${1}")"
    ARGUMENT="${ARGUMENT/--/}" # Remove "--".
    ARGUMENT="${ARGUMENT//-/_}" # Replace "-" with "_".
    echo "${ARGUMENT}"
}

parseArguments "$@"

function printUsage {
    echo "invalid arugments"
    echo "usage:"
    echo "${0} --version 1.2.3 \\"
    echo "    --build-version 12345 \\"
    echo "    --team-id Q55F59LQD3 \\"
    echo "    --bundle-id com.synerty.peek \\"
    echo "    --provision-profile-name 'Synerty iOS Development'"
    echo
    echo "OR"
    echo
    echo "usage:"
    echo "${0} --version 1.2.3 \\"
    echo "    --build-version 12345 \\"
    echo "    --team-id Q55F59LQD3 \\"
    echo "    --bundle-id com.synerty.peek \\"
    echo "    --provision-profile-uuid '12341234-1234-1234-abcd-abce12345678'"
    echo

    exit 1
}

# exit if any of mandatory parameters is missing
[[ -n "${ARG_VERSION+set}" ]] || printUsage
echo "ARG_VERSION $ARG_VERSION"

[[ -n "${ARG_BUILD_VERSION+set}" ]] || printUsage
echo "ARG_BUILD_VERSION $ARG_BUILD_VERSION"

[[ -n "${ARG_TEAM_ID+set}" ]] || printUsage
echo "ARG_TEAM_ID $ARG_TEAM_ID"

[[ -n "${ARG_BUNDLE_ID+set}" ]] || printUsage
echo "ARG_BUNDLE_ID $ARG_BUNDLE_ID"

[[ -n "${ARG_PROVISIONING_PROFILE_NAME+set}" ]] \
    || [[ -n "${ARG_PROVISIONING_PROFILE_UUID+set}" ]] \
    || printUsage

# If the UUID is not set, then the name must be, work out the UUID
if [[ -z "${ARG_PROVISIONING_PROFILE_UUID+set}" ]]
then
    echo "$ARG_PROVISIONING_PROFILE_NAME $ARG_PROVISIONING_PROFILE_NAME"
    VAL="<string>${ARG_PROVISIONING_PROFILE_NAME}</string>"
    count=$(cd "${XCODE_PROFILE_DIR}" && \
                cat "${XCODE_PROFILE_DIR}"/*.mobileprovision \
                | grep -c "${VAL}" )

    if [[ "${count}" -ne 1 ]]
    then
        echo "Exactly one provisioning profile expected, we found ${count}"
        echo "Please choose one and use the --provision-profile-uuid argument"
        grep -n "${VAL}" "${XCODE_PROFILE_DIR}"*.mobileprovision
        false
    fi

    ARG_PROVISIONING_PROFILE_UUID=$(cd "${XCODE_PROFILE_DIR}" \
            && grep -l "${VAL}" *.mobileprovision | cut -f1 -d.)
fi

echo "ARG_PROVISIONING_PROFILE_UUID $ARG_PROVISIONING_PROFILE_UUID"

echo

# override defaults by arguments
XCODE_APP_VERSION="${ARG_VERSION}" # e.g. 3.1.2
XCODE_BUILD_VERSION='b'"${ARG_BUILD_VERSION}" # e.g. b12345 - gitlab CI job ID
XCODE_DEVELOPEMENT_TEAM_ID="${ARG_TEAM_ID}"
XCODE_APP_BUNDLE_IDENTIFIER="${ARG_BUNDLE_ID}"
XCODE_PROVISIONING_PROFILE_UUID="${ARG_PROVISIONING_PROFILE_UUID}"

# automatic populated parameters for xcode
export XCODE_SOURCE_FOLDER="${SCRIPT_PATH}"'/../ios/'$XCODE_APP_NAME
# relative to source folder above
XCODE_WORKSPACE=$XCODE_APP_NAME'.xcworkspace'
XCODE_BUILD_CONFIGURATION='Release'
XCODE_SCHEME=$XCODE_APP_NAME
XCODE_ARCHIVE_PATH='../../build/peek_'$XCODE_BUILD_VERSION'_'$XCODE_APP_VERSION'_'$NOW
XCODE_IPA_EXPORT_PATH='../../build/ipa_peek_'$XCODE_BUILD_VERSION'_'$XCODE_APP_VERSION'_'$NOW
XCODE_CACHED_PROVISIONING_PROFILE_PATH="${XCODE_PROFILE_DIR}/${XCODE_PROVISIONING_PROFILE_UUID}.mobileprovision"

# based on https://medium.com/xcblog/xcodebuild-deploy-ios-app-from-command-line-c6defff0d8b8
#  and https://www.jianshu.com/p/3f43370437d2

function buildAngularProject {
    CMD="${SCRIPT_PATH}/prepare_capacitor_ios_app.sh"
    CMD="${CMD} --headerless --version ${XCODE_APP_VERSION}"
    echo "running ${CMD}"
    # shellcheck disable=SC2086
    bash ${CMD}
}

function printProjectBuildOptions {
    echo "=============================="
    echo "====== xcodebuild -list ======"
    echo "=============================="
    xcodebuild -list
}

function printAvailableSDKs() {
    echo "=================================="
    echo "====== xcodebuild -showsdks ======"
    echo "=================================="
    xcodebuild -showsdks
}

function  cleanAndAnalyzeProject {
    echo "======================================"
    echo "====== xcodebuild clean analyze ======"
    echo "======================================"
    xcodebuild clean analyze \
        -quiet \
        -workspace $XCODE_WORKSPACE \
        -scheme $XCODE_SCHEME
}

function buildForRunning {
    xcodebuild build \
        -scheme $XCODE_SCHEME \
        -workspace $XCODE_WORKSPACE
}

function setTargetVersions {
    pushd $XCODE_SOURCE_FOLDER/App/

    # app version
    /usr/libexec/Plistbuddy \
        -c 'Delete CFBundleShortVersionString' Info.plist

    /usr/libexec/Plistbuddy \
        -c "Add CFBundleShortVersionString string ${XCODE_APP_VERSION}"  \
        Info.plist

    # build version
    /usr/libexec/Plistbuddy \
        -c 'Delete CFBundleVersion' Info.plist


    /usr/libexec/PlistBuddy \
        -c "Add CFBundleVersion string $XCODE_BUILD_VERSION" Info.Plist
    popd
}

function archive {
    echo "================================"
    echo "====== xcodebuild archive ======"
    echo "================================"

    xcodebuild archive \
        -quiet \
        -workspace $XCODE_WORKSPACE \
        -scheme $XCODE_SCHEME \
        -configuration $XCODE_BUILD_CONFIGURATION \
        -archivePath $XCODE_ARCHIVE_PATH \
        -allowProvisioningUpdates \
        CODE_SIGN_STYLE="Manual" \
        PROVISIONING_PROFILE_SPECIFIER="${XCODE_PROVISIONING_PROFILE_UUID}" \
        PRODUCT_BUNDLE_IDENTIFIER_APP="${XCODE_APP_BUNDLE_IDENTIFIER}" \
        DEVELOPEMENT_TEAM="${XCODE_DEVELOPEMENT_TEAM_ID}" \
        CFBundleShortVersionString="${XCODE_APP_VERSION}" \
        CFBundleVersion="${XCODE_BUILD_VERSION}"
}

function exportIpa {
    echo "==================================="
    echo "====== xcodebuild export ipa ======"
    echo "==================================="

    exportOptionsPlistPath="${XCODE_ARCHIVE_PATH}"".xcarchive/exportOptionsPlist.plist"
    cp $XCODE_SOURCE_FOLDER"/../../scripts/exportOptionsPlist.plist.template" \
        "${exportOptionsPlistPath}"

    _populateExportOptionsPlist $exportOptionsPlistPath

    xcodebuild -exportArchive \
        -quiet \
        -archivePath $XCODE_ARCHIVE_PATH".xcarchive" \
        -exportPath $XCODE_IPA_EXPORT_PATH \
        -exportOptionsPlist "${exportOptionsPlistPath}" \
        PROVISIONING_PROFILE_SPECIFIER="${XCODE_PROVISIONING_PROFILE_UUID}" \
        PRODUCT_BUNDLE_IDENTIFIER_APP="${XCODE_APP_BUNDLE_IDENTIFIER}" \
        DEVELOPEMENT_TEAM="${XCODE_DEVELOPEMENT_TEAM_ID}" \
        CFBundleShortVersionString="${XCODE_APP_VERSION}" \
        CFBundleVersion="${XCODE_BUILD_VERSION}"

    unset exportOptionsPlistPath
}

function inspectArchive() {
    echo "====== inspect archive ======"
    _archiveFolder=$XCODE_ARCHIVE_PATH".xcarchive"
    pushd $_archiveFolder
        infoPlist="Products/Applications/${XCODE_APP_NAME}.app/Info.plist"
        echo "== inspect archive: marked versions in $infoPlist =="
        _inspectInfoPlist $infoPlist

        profileInArchive="Products/Applications/${XCODE_APP_NAME}.app/embedded.mobileprovision"
        echo "== inspect archive: mobileprovision file in $profileInArchive =="
        _inspectProvisioningProfile $profileInArchive

        appFolder=Products/Applications/*.app
        echo "== inspect archive: code signature =="
        _inspectCodeSignature $appFolder
    popd
}

function inspectIpa() {
    echo "====== inspect ipa ======"
    _ipaFolder=$XCODE_IPA_EXPORT_PATH
    extractedIpaFolder='_extracted_ipa'

    pushd $_ipaFolder
        unzip -q -o $XCODE_APP_NAME.ipa -d $extractedIpaFolder

        _appFolder=$extractedIpaFolder/Payload/$XCODE_APP_NAME".app"

        infoPlist=$_appFolder"/Info.plist"
        echo "== inspect archive: marked versions in $profileInArchive =="
        _inspectInfoPlist $infoPlist

        profileInIpa=$_appFolder"/embedded.mobileprovision"
        echo "== inspect ipa file: mobileprovision file in $profileInIpa =="
        _inspectProvisioningProfile $profileInIpa

        echo "== inspect ipa file: code signature =="
        _inspectCodeSignature $_appFolder

        rm -rf $extractedIpaFolder

    popd
}

function _populateExportOptionsPlist {
    __exportOptionsPlistPath=$1

    echo 'populating exportOptionsPlist.plist '"${__exportOptionsPlistPath}"
    # delete bundle id and profile name from template
    /usr/libexec/PlistBuddy \
        -c 'Delete :provisioningProfiles' "${__exportOptionsPlistPath}"

    # update bundle id
    echo "new ipa bundle id: ""${XCODE_APP_BUNDLE_IDENTIFIER}"
    echo "new ipa provisioning profile name: ""${XCODE_PROVISIONING_PROFILE_UUID}"
    /usr/libexec/PlistBuddy -c \
    'Add :provisioningProfiles:'"${XCODE_APP_BUNDLE_IDENTIFIER}"' string '"${XCODE_PROVISIONING_PROFILE_UUID}" \
        "${__exportOptionsPlistPath}"

    # replace team id
    echo "new ipa team id: "$XCODE_DEVELOPEMENT_TEAM_ID
    /usr/libexec/PlistBuddy -c \
        'Set :teamID '$XCODE_DEVELOPEMENT_TEAM_ID $__exportOptionsPlistPath

    unset __exportOptionsPlistPath
}

function _inspectInfoPlist {
    file=$1

    echo "--Info.plist starts--"
    echo
    for key in CFBundleShortVersionString CFBundleVersion
        do
            output=$(/usr/libexec/PlistBuddy -c 'Print :'"${key}" "$file")
            echo $key": "$output

            if [[ $VERIFY_SIGN -eq 1 ]]
            then
                case $key in
                "CFBundleShortVersionString")
                    # app version on app store - public
                    if [[ -z "${output##*$XCODE_APP_VERSION*}" ]]
                    then
                        echo "APP Version - pass"
                    else
                        echo "APP Version - fail"
                        exit 1
                    fi
                    ;;
                "CFBundleVersion")
                    # build version - technical
                    if [[ -z "${output##*$XCODE_BUILD_VERSION*}" ]]
                    then
                        echo "Build Version - pass"
                    else
                        echo "Build Version - fail"
                        exit 1
                    fi
                    ;;
                esac
            fi
            echo
        done
    echo "--Info.plist ends--"
}

function _inspectProvisioningProfile {
    file=$1

    echo "--mobile provisioning profile starts--"
    echo
    for key in TeamName TeamIdentifier ExpirationDate Name
        do
            output=$(/usr/libexec/PlistBuddy \
               -c 'Print '"${key}" /dev/stdin <<< $(security cms -D -i $file))

            echo $key": "$output
            if [[ $VERIFY_SIGN -eq 1 ]]
            then
                case $key in
                "TeamIdentifier")
                    # substring match
                    if [[ -z "${output##*$XCODE_DEVELOPEMENT_TEAM_ID*}" ]]
                    then
                        echo "Team ID verify - pass"
                    else
                        echo "Team ID verify - fail"
                        exit 1
                    fi
                    ;;
                "ExpirationDate")
                    _expire=$(date -jf '%a %b %e %H:%M:%S %Z %Y' "${output}" '+%s')
                    _now=$(date '+%s')
                    if [[ $_expire -ge $_now ]]
                    then
                        echo "Expiration date - pass"
                    else
                        echo "Expiration date - fail"
                        exit 1
                    fi
                    ;;
                "Name")
                    if [[ -z "${output##*$XCODE_PROVISIONING_PROFILE_UUID*}" ]]
                     then
                        echo "Mobileprovision Name - pass"
                    else
                        echo "Mobileprovision Name - fail"
                        exit 1
                    fi
                    ;;
                esac
            fi
            echo
    done
    unset file
    echo "--mobile provisioning profile ends--"
}


function _inspectCodeSignature {
    appFolder=$1

    pushd $appFolder

        codesign -d --extract-certificates .


        echo
        echo "--trust chain starts--"
        echo
        for certFile in codesign*
        do
            openssl x509 -inform DER -in $certFile -noout \
                -subject -issuer -dates
            echo
        done
        echo "--trust chain ends--"
        echo

        echo clean up extracted signatures for inspections
        rm -f codesign*

    popd

}

function main {
    echo '================================='
    echo '======== Build Angular =========='
    echo '================================='
    buildAngularProject

    pushd $XCODE_SOURCE_FOLDER
    echo '============================='
    echo '======== Build iOS =========='
    echo '============================='
        setTargetVersions
        printAvailableSDKs
        printProjectBuildOptions
        cleanAndAnalyzeProject
        archive
        inspectArchive
        exportIpa
        inspectIpa

    popd
}
main
