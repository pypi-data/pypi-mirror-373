#!/usr/bin/env bash

#  ci_post_clone.sh
#  App
#
#  Created by Louis Lu on 15/09/23.
#
set -x
set -o errexit

source common.sh
source run_capacitor.sh

function provisionForCapacitor() {
    brew analytics off

    # install gnu-sed
    brew install --quiet gnu-sed
    rm ${HOME}/bin/sed || true
    mkdir -p ${HOME}/bin
    ln -s `which gsed` ${HOME}/bin/sed

    # install jq
    brew install --quiet jq

    # install cocoapods
    brew install --quiet cocoapods

    # install nodejs
    nodeFile="node-v${NODE_VER}-darwin-${ARCH}.tar.gz"
    curl -qO "https://nodejs.org/dist/v${NODE_VER}/$nodeFile"

    gunzip -c ${nodeFile} | tar xopf -
    mkdir -p ${NODE_DIR}
    mv node-v${NODE_VER}-darwin-${ARCH} ${NODE_DIR}

    # print versions
    node -v
    npm -v

    # install angular cli
    npm cache clean --force
    npm -g install @angular/cli@^$ANGULAR_CLI_VER
}

function runCapacitor() {
    echo npm install for field app
    pushd $FIELD_APP_PROJECT_PATH
        npm install
        runBeforeNgBuildHook
        ng build --configuration production --optimization  --common-chunk --vendor-chunk
    popd

    echo set up capacitor source
    pushd $FIELD_APP_PROJECT_PATH
        npx cap sync # pod install is called with this
    popd

    pushd $FIELD_APP_PROJECT_PATH
        runBeforeCapCopyHook
        npx cap copy ios
        runAfterCapCopyHook
    popd
}

function main() {
    start=$(date +%s)
    provisionForCapacitor
    end=$(date +%s)
    seconds=`expr $end - $start`
    echo =====================================
    echo =====================================
    printf 'provisionForCapacitor took %dh:%dm:%ds\n' $((seconds/3600)) $((seconds%3600/60)) $((seconds%60))
    echo =====================================
    echo =====================================

    runCapacitor
}

main
