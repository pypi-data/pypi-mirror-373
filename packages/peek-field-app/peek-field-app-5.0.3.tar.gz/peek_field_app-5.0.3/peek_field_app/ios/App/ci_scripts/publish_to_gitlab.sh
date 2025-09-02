#!/usr/bin/env bash

source common.sh

GITLAB_API_URL="https://gitlab.synerty.com/api/v4"
TAG_PREFIX="v"

appDotVersion=$(queryAppSpecNoQuotes ".appDotVersion")
environmentName=$(queryAppSpecNoQuotes ".appearance.environmentName")

packageName="${environmentName}-${appDotVersion}-development"

packageUploadApiBaseUrl="${GITLAB_API_URL}/projects/${GITLAB_PROJECT_ID}/packages/generic/${packageName}/${appDotVersion}"
echo "packageUploadApiBaseUrl"
echo "$packageUploadApiBaseUrl"
# development ipa
devIpaFilename="${packageName}.ipa"

# develop ipa folder zip
devIpaFolderZipFilename="${packageName}.zip"

# xarchive
xarchiveZipFilename="${packageName}.xarchive.zip"

function uploadPackages() {
  # development ipa
  pushd $CI_DEVELOPMENT_SIGNED_APP_PATH
    devIpaFilenameUrl="${packageUploadApiBaseUrl}/${devIpaFilename}"
    echo "devIpaFilenameUrl"
    echo "$devIpaFilenameUrl"

    curl --header "PRIVATE-TOKEN: ${GITLAB_ACCESS_TOKEN}" \
      --upload-file "App.ipa" \
      "${devIpaFilenameUrl}"
  popd

  # development ipa - full folder
  pushd $CI_DEVELOPMENT_SIGNED_APP_PATH

    zip -r "$devIpaFolderZipFilename" .

    devIpaFolderZipUrl="${packageUploadApiBaseUrl}/${devIpaFolderZipFilename}"

    curl --header "PRIVATE-TOKEN: ${GITLAB_ACCESS_TOKEN}" \
      --upload-file "${devIpaFolderZipFilename}" \
      "${devIpaFolderZipUrl}"

    rm -f "$devIpaFolderZipFilename"
  popd

  # xarchive folder
  pushd $CI_ARCHIVE_PATH
    zip -r "$xarchiveZipFilename" .

    xarchiveZipUrl="${packageUploadApiBaseUrl}/${xarchiveZipFilename}"

    curl --header "PRIVATE-TOKEN: ${GITLAB_ACCESS_TOKEN}" \
      --upload-file "${xarchiveZipFilename}" \
      "${xarchiveZipUrl}"

    rm -f "$xarchiveZipFilename"
  popd
}

function _generateReleaseInfoJsonString() {
  # get package id by package name
  packageId=$(curl --request GET \
  --url "${GITLAB_API_URL}/projects/${GITLAB_PROJECT_ID}/packages?package_name=${packageName}" \
  --header "PRIVATE-TOKEN: ${GITLAB_ACCESS_TOKEN}" | jq -r ".[0].id")

  # get packages files with package id
  packageFilesJson=$(curl --request GET \
  --url "${GITLAB_API_URL}/projects/${GITLAB_PROJECT_ID}/packages/${packageId}/package_files" \
  --header "PRIVATE-TOKEN: ${GITLAB_ACCESS_TOKEN}" | jq .)

  # get project url by project id with no trailing slash '/'
  #  e.g. https://gitlab.synerty.com/clients/nz-orion/peek-ios
  projectWebUrl=$(curl --request GET \
   --url "${GITLAB_API_URL}/projects/${GITLAB_PROJECT_ID}/" \
   --header "PRIVATE-TOKEN: ${GITLAB_ACCESS_TOKEN}" | jq -r '.web_url'
  )

  # jq
  #  1. for each object in array
  #  2. create key 'name' with value from key '.file_name'
  #  3. crate key 'url' with a value from string concat with pass-in argument projectWebUrl
  #       e.g. https://gitlab.synerty.com/clients/nz-orion/peek-ios/-/package_files/3/download
  #  4. create key 'link_type' with value "package"
  #  5. remove the keys from original objects
  #  above outputs json object lines
  #  jq --slurp # make an array of objects from json object lines
  echo "$packageFilesJson" \
      | jq --arg projectWebUrl "${projectWebUrl}" \
      '.[]
        | .["name"] = .file_name
        | .["url"] = $projectWebUrl + "/-/package_files/" + (.id|tostring) + "/download"
        | .["link_type"] = "package"
        | del(.file_name, .size, .file_md5, .file_sha1, .file_sha256, .created_at, .package_id, .id) ' \
      | jq --slurp > _links.json

  releaseTitle="v${appDotVersion} for environment '${environmentName}' with app signing 'development'" # replace every '-' with ' '
  descriptionMarkdown="This is an automatic iOS build by Xcode Cloud with

app environment name: \`${environmentName}\`

app version: \`${appDotVersion}\`

app signing: development


in build ${CI_BUILD_NUMBER} ${CI_BUILD_URL}."

  jq --arg releaseTitle "$releaseTitle" \
    --arg tagPrefix "$TAG_PREFIX" \
    --arg appDotVersion "$appDotVersion" \
    --arg descriptionMarkdown "$descriptionMarkdown" \
    --argjson links "$(<_links.json)" \
    '.assets.links = $links
      | .name = $releaseTitle
      | .tag_name = $tagPrefix + $appDotVersion
      | .description = $descriptionMarkdown' \
    new_release.template.json
}

function createRelease() {

  curl --request POST \
    --url "https://gitlab.synerty.com/api/v4/projects/${GITLAB_PROJECT_ID}/releases" \
    --header "PRIVATE-TOKEN: ${GITLAB_ACCESS_TOKEN}" \
    --header "Content-Type: application/json" \
    --data "$(_generateReleaseInfoJsonString)"
}

function publishToGitlab() {
  uploadPackages
  createRelease
}
