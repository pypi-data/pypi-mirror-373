#!/usr/bin/env python3
import json
import os
import pprint
import re
from collections import defaultdict
from pathlib import Path

try:
    import git
except ImportError as e:
    print("please install gitpython by `pip install gitpython`")
    exit(1)

from git import GitCommandError, TagReference

BASE_DIR = os.getcwd()

assert Path("peek_field_app/angular.json").exists(), (
    "The current directory must be where the `peek_field_app` "
    "directory is located"
)

VERSION_PATTERN = re.compile(r"(\d+\.\d+\.\d+)")
REPO = git.Repo(BASE_DIR, search_parent_directories=True)
APP_SPEC_JSON = json.load(open(f"{BASE_DIR}/app_spec.json", "r"))
TAG_PREFIX = "v"


def getHEADCommit():
    return REPO.head.object.hexsha[0:8]


def printGitStatus():
    print(f"On branch {REPO.active_branch}, HEAD is {getHEADCommit()}")


def printAppSpecJson():
    print("your app customisation are as follows:")
    pprint.pprint(APP_SPEC_JSON)


def checkBranchNameSameAsEnvName():
    expectedBranchName = APP_SPEC_JSON.get("appearance", {}).get(
        "environmentName", None
    )
    if not expectedBranchName:
        raise ValueError("invalid environmentName in app_spec.json")

    currentBranchName = REPO.active_branch.name
    if expectedBranchName.lower() != currentBranchName.lower():
        raise ValueError(
            f"git branch name and environment name should be same, got "
            f"environmentName: '{expectedBranchName}', "
            f"git branch name: '{currentBranchName}'."
        )


def _getExistingGitTags() -> list[str]:
    return [t.name for t in REPO.tags]


def getPeekVersion() -> str:
    with open(f"{BASE_DIR}/peek_field_app/__init__.py") as f:
        matched = VERSION_PATTERN.search(f.read())
        if not matched:
            raise ValueError("NO VERSION found in __init__.py")

        return matched.group(1)  # version


def makeGitTagVersion(peekVersion: str) -> str:
    existingTags = _getExistingGitTags()
    versionDict = defaultdict(set)

    for existingTag in existingTags:
        existingTag = existingTag.lstrip(TAG_PREFIX)  # drop prefix 'v'
        major, minor, revision, build = existingTag.split(".")
        thisPeekVersion = f"{major}.{minor}.{revision}"
        versionDict[thisPeekVersion].add(build)

    newBuild = 1
    if peekVersion not in versionDict:
        print(f"existing builds for '{peekVersion}' are not found")
    else:
        buildsForPeekVersion = sorted(
            [int(b) for b in versionDict[peekVersion]]
        )
        print(f"existing builds for '{peekVersion}' are {buildsForPeekVersion}")

        lastBuild = max(buildsForPeekVersion)
        newBuild = lastBuild + 1

    return f"{TAG_PREFIX}{peekVersion}.{newBuild}"


def createNewGitTag(tagName: str) -> TagReference:
    return REPO.create_tag(tagName)


def deleteNewGitTag(tag: TagReference):
    REPO.delete_tag(tag)


def updateProjectFiles(tagName):
    tagName = tagName.lstrip(TAG_PREFIX)
    
    # update app_spec.json
    appSpecJsonPath = f"{BASE_DIR}/app_spec.json"
    j = json.load(open(appSpecJsonPath, "r"))
    j["appDotVersion"] = tagName
    json.dump(j, open(appSpecJsonPath, "w"), sort_keys=True, indent=4)

    # update Xcode project file
    projectFilePath = f"{BASE_DIR}/peek_field_app/ios/App/App.xcodeproj/project.pbxproj"
    appId = APP_SPEC_JSON["appId"]
    teamId = APP_SPEC_JSON["teamId"]
    
    with open(projectFilePath, "r") as f:
        content = f.read()
    
    # Update PRODUCT_BUNDLE_IDENTIFIER
    content = re.sub(
        r'PRODUCT_BUNDLE_IDENTIFIER = [^;]+;',
        f'PRODUCT_BUNDLE_IDENTIFIER = {appId};',
        content
    )
    
    # Update DEVELOPMENT_TEAM
    content = re.sub(
        r'DEVELOPMENT_TEAM = [^;]+;',
        f'DEVELOPMENT_TEAM = {teamId};',
        content
    )
    
    with open(projectFilePath, "w") as f:
        f.write(content)
    
    print(f"updated Xcode project with appId '{appId}' and teamId '{teamId}'")

    try:
        # git add
        REPO.git.add(all=True)
        # git commit
        REPO.git.commit(message=f"updated appDotVersion to {tagName}, appId to {appId}, teamId to {teamId}")
    except GitCommandError:
        pass


def updateGitIgnore():
    # remove all lines that contain "@peek" or "@_peek"
    inputFilename = f"{BASE_DIR}/peek_field_app/.gitignore"
    outputFilename = inputFilename
    keywords = ["@peek", "@_peek", "/src/assets/"]
    try:
        lines = []
        with open(inputFilename, "r") as inputFile:
            for line in inputFile:
                matched = False
                for keyword in keywords:
                    if keyword in line:
                        matched = True

                if not matched:
                    lines.append(line)

        with open(outputFilename, "w") as outputFile:
            outputFile.writelines(lines)

        print(f"updated gitignore from '{inputFilename}'.")

    except FileNotFoundError:
        print(f"File '{inputFilename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    updateGitIgnore()

    printGitStatus()
    peekVersion = getPeekVersion()
    print(f"peek version from source is '{peekVersion}'")

    checkBranchNameSameAsEnvName()

    newGitTagVersion = makeGitTagVersion(peekVersion=peekVersion)
    print(f"new tag for '{peekVersion}' will be {newGitTagVersion}")

    updateProjectFiles(newGitTagVersion)
    print(f"updated appDotVersion in app_spec.json to '{newGitTagVersion}'")

    printAppSpecJson()

    printGitStatus()
    newTagRef = createNewGitTag(newGitTagVersion)
    print(f"created git tag '{newGitTagVersion}' for commit {getHEADCommit()}")

    print(
        f"tagged version '{newGitTagVersion}' "
        f"should start building on Xcode Cloud"
    )
    return newGitTagVersion


if __name__ == "__main__":
    main()