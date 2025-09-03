#!/bin/bash

OWNER="amsdal"
REPO="amsdal_cli"
FOLDER="./src/amsdal_cli"
TAG_PREFIX="v"
FILE_NAME="__about__.py"
VERSION_REGEX="^__version__ = ['\"](.*)['\"]"


extract_version() {
    local file_path="$FOLDER/$FILE_NAME"
    local version=""

    if [[ -f "$file_path" ]]; then
        while IFS= read -r line; do
            if [[ $line =~ $VERSION_REGEX ]]; then
                version="${BASH_REMATCH[1]}"
                break
            fi
        done < "$file_path"

        if [[ -n $version ]]; then
            echo "$TAG_PREFIX$version"
        else
            echo "Version not found in $FOLDER"
            exit 1
        fi
    else
        echo "File $file_path does not exist"
        exit 1
    fi
}


fetch_repo_tags() {
    curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$OWNER/$REPO/tags?per_page=100" | jq -r '.[].name'
}

VERSION_TAG=$(extract_version)
REPO_TAGS=$(fetch_repo_tags)

if echo "$REPO_TAGS" | grep -q "^$VERSION_TAG$"; then
  echo "Tag $VERSION_TAG already exists in the repository."
else
  echo "Tag $VERSION_TAG does not exist in the repository. Creating and pushing tag."
  git tag $VERSION_TAG
  git push origin $VERSION_TAG
fi
