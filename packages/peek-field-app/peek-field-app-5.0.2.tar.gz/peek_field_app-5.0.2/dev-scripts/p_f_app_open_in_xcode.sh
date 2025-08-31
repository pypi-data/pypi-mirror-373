#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# Force close Xcode without prompts
osascript -e 'tell application "Xcode" to quit saving no' &

# Boot the simulator first and wait for it to be ready
xcrun simctl boot "iPad mini (6th generation)" &

cd ~/dev-peek/peek-field-app

cd peek_field_app
npm install
ng build

npx cap sync
npx cap open ios

# Wait a bit for Xcode to fully open
sleep 8

# Run using previous settings
osascript -e 'tell application "Xcode"'           \
     -e 'activate'           \
     -e 'tell application "System Events"'           \
     -e 'keystroke "r" using {command down}'           \
     -e 'end tell'           \
     -e 'end tell'

