#!/bin/bash

set -eux -o pipefail

bump_scheme="${1:-patch}"

current_version="$(uv version --short)"
: ">>> Current version: $current_version"

# bump to a new version
uv version --bump "$bump_scheme"
new_version="$(uv version --short)"
: ">>> New version: $new_version"

# commit changes
git commit -am "Release $new_version"
git tag "v$new_version"
GIT_PAGER=cat git log --pretty="format:%s" -3
git push origin main --tags
