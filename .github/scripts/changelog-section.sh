#!/bin/sh
# Prints the body of a section of CHANGELOG.md, without its heading and surrounding blank lines.
# Fails when the section is missing or empty.
# Usage: changelog-section.sh <heading>, such as "Version 1.0.0" or "Unreleased"
set -eu

section=$(awk -v heading="$1" '
  # Skip the heading and its "====" underline
  $0 == heading { found = 1; getline; next }
  # Sections end at the "---" separator before the next version heading
  found && $0 == "---" { exit }
  found && (started || $0 != "") { started = 1; print }
' CHANGELOG.md)

if [ -z "$section" ]; then
  echo "No '$1' section with entries in CHANGELOG.md" >&2
  exit 1
fi
printf '%s\n' "$section"
