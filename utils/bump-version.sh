#!/bin/sh
# Prepares a release commit: bumps the version, moves the `Unreleased` changelog entries
# under the new version, commits, then offers to push. Pushing is what publishes, see CONTRIBUTING.md.
# Usage: bump-version.sh <major|minor|patch|X.Y.Z>
set -eu

repo=Avasam/python-xlib
branch=avasam-python-xlib

fail() {
  echo "error: $*" >&2
  exit 1
}

[ $# -eq 1 ] || fail "usage: $0 <major|minor|patch|X.Y.Z>"
case $1 in
  major | minor | patch) bump="--bump $1" ;;
  *) bump=$1 ;;
esac

cd "$(git rev-parse --show-toplevel)"

# Sanity checks, before touching anything
[ "$(git branch --show-current)" = "$branch" ] || fail "not on $branch"
[ -z "$(git status --porcelain)" ] || fail "uncommitted changes"
git fetch --quiet origin "$branch"
[ "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$branch")" ] \
  || fail "HEAD differs from origin/$branch, push or pull first so CI runs on what gets released"

sha=$(git rev-parse HEAD)
ci=$(gh run list --repo "$repo" --workflow ci.yml --commit "$sha" --json status,conclusion \
  --jq '.[0] | if . == null then "missing" elif .status != "completed" then .status else .conclusion end')
[ "$ci" = success ] || fail "CI on $sha is '$ci', not 'success'"

sh .github/scripts/changelog-section.sh Unreleased >/dev/null || fail "nothing to release"

# shellcheck disable=SC2086 # $bump is either one argument or `--bump <part>`
version=$(uv version $bump --dry-run --short)
if git ls-remote --exit-code --tags origin "refs/tags/$version" >/dev/null; then
  fail "tag $version already exists"
fi

# The tree was clean, so undoing every edit on failure or Ctrl+C loses nothing.
restore() {
  git checkout --quiet -- pyproject.toml uv.lock CHANGELOG.md
  rm -f CHANGELOG.md.tmp
}
trap restore EXIT
trap 'exit 1' INT TERM

# shellcheck disable=SC2086
uv version $bump --no-sync >/dev/null

# Keep an empty `Unreleased` section on top, and put its entries under the new version heading.
awk -v heading="Version $version" '
  !done && $0 == "Unreleased" {
    getline underline
    print "Unreleased"; print underline; print ""; print "---"; print ""
    line = heading; gsub(/./, "=", line)
    print heading; print line
    done = 1
    next
  }
  { print }
' CHANGELOG.md > CHANGELOG.md.tmp
mv CHANGELOG.md.tmp CHANGELOG.md

# Same checks as release.yml, so a broken changelog never gets pushed.
sh .github/scripts/changelog-section.sh "Version $version" >/dev/null
if sh .github/scripts/changelog-section.sh Unreleased >/dev/null 2>&1; then
  fail "'Unreleased' still has entries after the swap"
fi

git commit --quiet -m "Release $version" -- pyproject.toml uv.lock CHANGELOG.md
trap - EXIT INT TERM
git show --stat HEAD

printf 'Push and publish %s to PyPI? This cannot be undone. [y/N] ' "$version"
read -r answer
if [ "$answer" = y ] || [ "$answer" = Y ]; then
  git push origin "HEAD:$branch"
else
  echo "Not pushed. Publish with 'git push origin HEAD:$branch', or drop the commit with 'git reset --hard HEAD~1'."
fi
