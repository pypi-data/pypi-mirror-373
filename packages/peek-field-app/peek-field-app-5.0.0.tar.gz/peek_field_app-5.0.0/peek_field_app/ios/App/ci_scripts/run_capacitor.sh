#!/usr/bin/env bash

#  ci_pre_xcodebuild.sh
#  App
#
#  Created by Louis Lu on 21/09/23.
#
set -x
set -o errexit

source common.sh

function userAngularUpdateBackgroundColor() {
    bgColor=$1

    SCSS="src/_variables.scss"

    pushd $FIELD_APP_PROJECT_PATH
        gsed -i 's/$primary-color:.*/$primary-color: '${bgColor}';/g' $SCSS
    popd

}

function userNativeUpdateAppDisplayName() {
    appDisplayName=$1

    pushd $FIELD_APP_PROJECT_PATH
        plutil -replace CFBundleDisplayName -string "${appDisplayName}" ios/App/App/Info.plist
    popd
}

function userNativeUpdateAppId() {
  appId=$1

  pushd $FIELD_APP_PROJECT_PATH
      plutil -replace CFBundleIdentifier -string "${appId}" ios/App/App/Info.plist
  popd
}

function userAngularUpdateConfigScreenVersion() {
    environmentName=$1
    appDotVersion=$2

    pushd $FIELD_APP_PROJECT_PATH
        if [[ $environmentName != "" ]] && [[ $environmentName != "null" ]]; then
            CONFIG_TS="src/app/pages/config/config.page.ts"

            gsed -iv 's/Peek Config/'$environmentName' Peek Config/g' \
                "${CONFIG_TS}"

            grep "Peek Config" "${CONFIG_TS}"


            CONFIG_HTML="src/app/pages/config/config.page.html"

            gsed -iv 's/Peek Field App/Peek '$appEnvironment' Field App/g' \
                "${CONFIG_HTML}"

            grep "Field App" "${CONFIG_HTML}"
        fi

        VERSION_TS="src/environments/peek-app-environment.ts"

        dateAndCommitRef=$(TZ="${TZ}" date '+%Y%m%d.'${CI_COMMIT:0:8})
        gsed -iv 's/version:.*/version: "'$appDotVersion' b'$CI_BUILD_NUMBER' ('$dateAndCommitRef')",/g' \
            "${VERSION_TS}"

        grep version "${VERSION_TS}"
    popd
}

function userAngularHardcodeConnectionString() {
    host=$1
    useSsl=$2
    httpPort=$3
    websocketPort=$4
    hasConnected=$5

    if [[ $host == "null" ]]; then
        host=""
    fi

    pushd $FIELD_APP_PROJECT_PATH
# important: no indent
cat <<EOF | tee src/@peek/peek_core_device/_private/tuples/server-info-tuple-defaults.ts
export const SERVER_INFO_TUPLE_DEFAULTS = {
    host: '${host}',
    useSsl: ${useSsl},
    httpPort: ${httpPort},
    websocketPort: ${websocketPort},
    hasConnected: ${hasConnected} // Required to be true to override stored settings
};
EOF
    popd
}

function userNativeUpdateAppIcon() {

    iconFilePath=$1

    npm -g install cordova-res

    pushd $FIELD_APP_PROJECT_PATH
        if [[ $iconFilePath != "resources/icon.png" ]]; then
            pushd $CI_PRIMARY_REPOSITORY_PATH
              cp $iconFilePath $FIELD_APP_PROJECT_PATH/resources/icon.png
            popd

            # check if size is 1024x1024
            imgWidth=$(sips -g pixelWidth resources/icon.png | awk '/pixelWidth:/{print $2}')
            imgHeight=$(sips -g pixelHeight resources/icon.png | awk '/pixelHeight:/{print $2}')

            if [[ $imgWidth != 1024 ]] || [[ $imgHeight != 1024 ]]; then
              echo App icon must be 1024x1024
              exit 1
            fi
        fi

        cordova-res ios --skip-config --copy --type icon
    popd
}

function userNativeUpdateAppVersion() {
    appDotVersion=$1

    pushd $FIELD_APP_PROJECT_PATH
        plutil -replace CFBundleShortVersionString -string "${appDotVersion}" ios/App/App/Info.plist
    popd
}

function patchNativeAudioPlugin() {
    pushd $FIELD_APP_PROJECT_PATH
        echo Patching native-audio plugin
        #  https://github.com/danielsogl/awesome-cordova-plugins/issues/2685#issuecomment-567261609
         gsed -i 's/@"www"/@"public"/' ios/capacitor-cordova-ios-plugins/sources/CordovaPluginNativeaudio/NativeAudio.m
    popd
}

function patchPodsFrameworksScript() {
    pushd $FIELD_APP_PROJECT_PATH
        echo Pathching PodsFrameworks script
        # support Peek v3
        gsed -i 's/source="$(readlink "${source}")"/source="$(readlink -f "${source}")"/g' ios/App/Pods/Target\ Support\ Files/Pods-peek/Pods-peek-frameworks.sh || true
        # support Peek v4
        gsed -i 's/source="$(readlink "${source}")"/source="$(readlink -f "${source}")"/g' ios/App/Pods/Target\ Support\ Files/Pods-App/Pods-App-frameworks.sh || true
    popd
}

function runBeforeNgBuildHook() {
    echo runBeforeNgBuildHook

    echo update app background color
    bgColor=$(queryAppSpecNoQuotes ".appearance.backgroundColor")
    userAngularUpdateBackgroundColor $bgColor

    echo update app environment name and version
    environmentName=$(queryAppSpecNoQuotes ".appearance.environmentName")
    appDotVersion=$(queryAppSpecNoQuotes ".appDotVersion")
    userAngularUpdateConfigScreenVersion $environmentName $appDotVersion

    echo update server connection
    host=$(queryAppSpecNoQuotes ".serverConnection.host")
    useSsl=$(queryAppSpecNoQuotes ".serverConnection.useSsl")
    httpPort=$(queryAppSpecNoQuotes ".serverConnection.httpPort")
    websocketPort=$(queryAppSpecNoQuotes ".serverConnection.websocketPort")
    hasConnected=$(queryAppSpecNoQuotes ".serverConnection.hasConnected")
    userAngularHardcodeConnectionString $host $useSsl $httpPort $websocketPort $hasConnected
}

function runBeforeCapCopyHook() {
    echo runBeforeNgBuildHook

    patchNativeAudioPlugin
    patchPodsFrameworksScript
}

function runAfterCapCopyHook() {
    echo runAfterCapCopyHook

    echo update app display name
    appName=$(queryAppSpecNoQuotes ".appName")
    userNativeUpdateAppDisplayName "$appName"

    echo update app id
    appId=$(queryAppSpecNoQuotes ".appId")
    userNativeUpdateAppId "$appId"

    echo update app icon
    iconFilePath=$(queryAppSpecNoQuotes ".appIcon")
    userNativeUpdateAppIcon "$iconFilePath"

    echo update app version number
    appDotVersion=$(queryAppSpecNoQuotes ".appDotVersion")
    userNativeUpdateAppVersion "$appDotVersion"
}
