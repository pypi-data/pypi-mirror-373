#!/bin/bash

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <release_date> <release_version>"
  exit 1
fi

RELEASE_DATE=$1
RELEASE_VERSION=$2


git checkout -b "release/$RELEASE_DATE"

hatch run release $RELEASE_VERSION

git push origin "release/$RELEASE_DATE"

echo "Branch release/$RELEASE_DATE created and pushed."
