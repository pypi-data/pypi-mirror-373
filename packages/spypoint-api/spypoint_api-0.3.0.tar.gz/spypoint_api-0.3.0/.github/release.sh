#!/usr/bin/env bash
set -euo pipefail

increment_version() {
  local delimiter=.
  local array=($(echo "$1" | tr $delimiter '\n'))
  array[$2]=$((array[$2]+1))
  if [ $2 -lt 2 ]; then array[2]=0; fi
  if [ $2 -lt 1 ]; then array[1]=0; fi
  echo $(local IFS=$delimiter ; echo "${array[*]}")
}

apply_bump() {
  if [ "$1" == "patch" ]; then
    increment_version "$2" 2
  elif [ "$1" == "minor" ]; then
   increment_version "$2" 1
  elif [ "$1" == "major" ]; then
   increment_version "$2" 0
  fi
}

change_pyproject() {
  sed -i '' "s/${1}/${2}/g" pyproject.toml
}

git_tag () {
  git commit -am "${1}"
  git tag "${1}" -am "${1}"
}

BUMP="$1"
CURRENT="$(grep 'version' pyproject.toml | cut -d\   -f3 | tr -d '"')"
NEXT="$(apply_bump "$BUMP" "$CURRENT")"

echo "$BUMP - from $CURRENT to $NEXT"
change_pyproject "$CURRENT" "$NEXT"
git_tag "$NEXT"