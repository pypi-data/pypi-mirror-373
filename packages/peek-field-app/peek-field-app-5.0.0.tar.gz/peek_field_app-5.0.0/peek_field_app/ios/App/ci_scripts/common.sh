#!/usr/bin/env bash

#  common.sh
#  App
#
#  Created by Louis Lu on 21/09/23.
#

# XCode Cloud settings
TZ="Pacific/Auckland"
NODE_VER=18.16.1
ANGULAR_CLI_VER=16.1.1
FIELD_APP_PROJECT_PATH=$CI_PRIMARY_REPOSITORY_PATH"/peek_field_app"

NODE_DIR=$HOME/opt/node

if [[ "$(arch)" == "arm64" ]]
then
  ARCH="arm64"
else
  ARCH="x64"
fi

NODE_PATH="$NODE_DIR/node-v${NODE_VER}-darwin-${ARCH}/bin"
PATH+=":$NODE_PATH"
export PATH


export HOMEBREW_NO_INSTALL_CLEANUP=TRUE


function queryAppSpec() {
    query=$1

    jq $query $CI_PRIMARY_REPOSITORY_PATH/app_spec.json
}

function queryAppSpecNoQuotes() {
    query=$1

    ret=$(queryAppSpec $query)
    echo ${ret//\"/} # drop double quotes
}
