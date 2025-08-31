#!/usr/bin/env bash

set -o nounset
set -o errexit

SCRIPT_PATH="$(cd "$(dirname $0)"; pwd -P)"

# defaults
# 0 = false; 1 = true
ARG_SKIP_BUILD=${ARG_SKIP_BUILD:-0}
ARG_BUILD_DEV=${ARG_BUILD_DEV:-0}
ARG_HEADERLESS=${ARG_HEADERLESS:-0}
ARG_VERSION=${ARG_VERSION:-0.0.0}

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
  ((COUNT=0)) || true
  for CURRENT_ITEM in "$@"
  do
    if [[ ${CURRENT_ITEM} == "--"* ]]; then
      # could set this to empty string and check with [ -z "${ARG_ITEM-x}" ]
      # if it's set, but empty.
      printf -v "ARG_$(formatArgument "${CURRENT_ITEM}")" "%s" "1"
    else
      if [[ $PREVIOUS_ITEM == "--"* ]]; then
        printf -v "ARG_$(formatArgument "${PREVIOUS_ITEM}")" "%s" "${CURRENT_ITEM}"
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

echo 'parameter configured: 0 - not set, 1 - set'
echo 'ARG_SKIP_BUILD: '$ARG_SKIP_BUILD
echo 'ARG_BUILD_DEV: '$ARG_BUILD_DEV
echo 'ARG_HEADERLESS: '$ARG_HEADERLESS
echo 'ARG_VERSION: "'"$ARG_VERSION"'"'
echo

function prepare {
    if [[ $ARG_SKIP_BUILD -eq 0 ]]; then
        if [[ $ARG_BUILD_DEV -eq 1 ]]; then
            echo Building Angular - Peek field app for dev
            ng build
        else
            echo Building Angular - Peek field app for production
            ng build --configuration production --optimization  --common-chunk --vendor-chunk
        fi
    else
        echo Skipped building Angular Peek field app
    fi


    echo Syncing capacitor build
    npx cap sync

    echo Patching native-audio plugin
    #  https://github.com/danielsogl/awesome-cordova-plugins/issues/2685#issuecomment-567261609
    sed -i 's/@"www"/@"public"/' \
        ios/capacitor-cordova-ios-plugins/sources/CordovaPluginNativeaudio/NativeAudio.m


    echo Applying patch
    npx cap copy ios


    if [[ $ARG_HEADERLESS -eq 0 ]]; then
        echo Opening xcode
        npx cap open ios
    fi
}

function main {
    pushd "${SCRIPT_PATH}""/../"
        prepare
    popd

}

main