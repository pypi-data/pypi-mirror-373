#!/bin/bash


# only run this for ios
if [[ "$CAPACITOR_PLATFORM_NAME" == "ios" ]]; then
    echo after cap sync hook starts ...

    echo Patching native-audio plugin
    sed -i 's/@"www"/@"public"/' \
            ios/capacitor-cordova-ios-plugins/sources/CordovaPluginNativeaudio/NativeAudio.m

    echo Patching pod script
    sed -i 's/source="$(readlink "${source}")"/source="$(readlink -f "${source}")"/g' \
            ios/App/Pods/Target\ Support\ Files/Pods-peek/Pods-peek-frameworks.sh


    echo after cap sync hook ends
fi