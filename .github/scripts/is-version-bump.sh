#!/bin/sh
# Succeeds when the changes between two commits are only what a release commit makes:
# any change to CHANGELOG.md, and nothing but the version line of pyproject.toml and uv.lock.
# Such a commit has the same code as the one before it, which already passed CI.
# Fails on anything else, including a base that is missing or unreachable.
# Usage: is-version-bump.sh <base> <head>
set -eu

base=$1
head=$2

git cat-file -e "$base^{commit}" 2>/dev/null || exit 1

files=$(git diff --name-only "$base" "$head")
[ -n "$files" ] || exit 1

for file in $files; do
  case $file in
    CHANGELOG.md) ;;
    pyproject.toml | uv.lock)
      # With no context lines, a bump is one removed and one added `version = "..."` line.
      changed=$(git diff -U0 "$base" "$head" -- "$file" | grep -E '^[-+]' | grep -vE '^(---|\+\+\+)')
      [ "$(printf '%s\n' "$changed" | wc -l)" -eq 2 ] || exit 1
      printf '%s\n' "$changed" | grep -qE '^-version = "[^"]*"' || exit 1
      printf '%s\n' "$changed" | grep -qE '^\+version = "[^"]*"' || exit 1
      ;;
    *) exit 1 ;;
  esac
done
