#!/usr/bin/env bash

set -x
set -o errexit

source common.sh
source publish_to_gitlab.sh

infoPlistPath="Payload/*.app/Info.plist"

function checkAppCustomisation() {
  pushd $CI_DEVELOPMENT_SIGNED_APP_PATH
    unzip -qa *.ipa

    echo print app name
    actualAppName=$(/usr/libexec/PlistBuddy -c "print CFBundleDisplayName" $infoPlistPath)
    expectedAppName=$(queryAppSpecNoQuotes ".appName")
    if [[ $actualAppName == $expectedAppName ]]; then
      echo app name PASS ✅
    else
      echo app name FAILED ❌
    fi

    echo print app id
    actualAppId=$(/usr/libexec/PlistBuddy -c "print CFBundleIdentifier" $infoPlistPath)
    expectedAppId=$(queryAppSpecNoQuotes ".appId")
    if [[ $actualAppId == $expectedAppId ]]; then
      echo app id PASS ✅
    else
      echo app id FAILED ❌
    fi

    echo print app version
    actualAppVersion=$(/usr/libexec/PlistBuddy -c "print CFBundleShortVersionString" $infoPlistPath)
    expectedVersion=$(queryAppSpecNoQuotes ".appDotVersion")
    if [[ $actualAppVersion == $expectedVersion ]]; then
      echo app version PASS ✅
    else
      echo app version FAILED ❌
    fi

    echo print app build number
    actualBuildNumber=$(/usr/libexec/PlistBuddy -c "print CFBundleVersion" $infoPlistPath)
    expectedBuildNumber=$CI_BUILD_NUMBER
    if [[ $actualBuildNumber == $expectedBuildNumber ]]; then
      echo app build number PASS ✅
    else
      echo app build number FAILED ❌
    fi
  popd
}

function main() {
  checkAppCustomisation
  publishToGitlab
}

main
