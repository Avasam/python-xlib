# Contributing

## Changelog

Every user-facing change adds its entry to the `Unreleased` section at the top of [CHANGELOG.md](CHANGELOG.md), in the same commit or pull request as the change. CI, test and refactoring changes that users cannot observe need no entry.

Credit contributors other than the maintainer as `(thanks [@user][user])`, and add `[user]: https://github.com/user` to the sorted list of links at the end of the file if it is not there yet.

## Type stubs

The `.pyi` stubs in `Xlib/` come from typeshed and are licensed under Apache-2.0 (see [LICENSE-typeshed](LICENSE-typeshed)), which requires modified files to carry a prominent notice of the change. The first change to a stub adds `# Modified from typeshed` as its first line. A stub that already has that line needs nothing more.

## Releasing (maintainers)

The version in `pyproject.toml` is the single source of truth. When a push to `Avasam/python-xlib` carries a version that has no tag yet, [release.yml](.github/workflows/release.yml) publishes to PyPI through trusted publishing, then creates the tag and the GitHub release on that commit. Tags are never created by hand, so the tag, PyPI and `Xlib.__version__` cannot disagree.

### Cutting a release

The version bump is what triggers the release, so the changelog must be complete **before** bumping.

1. Check that `Unreleased` covers every user-facing change since the [latest release](https://github.com/Avasam/python-xlib/releases/latest), using its "commits to avasam-python-xlib since this release" link.
2. Run `sh utils/bump-version.sh <major|minor|patch|X.Y.Z>`. From a clean `avasam-python-xlib` branch that matches `origin` and passed CI, it bumps `pyproject.toml` and `uv.lock`, moves the `Unreleased` entries under a new `Version X.Y.Z` heading, commits `Release X.Y.Z`, then asks before pushing.

It refuses to run when `Unreleased` is empty, when the tag already exists, or when the latest `ci.yml` run on `HEAD` did not succeed. To do it by hand instead, rename the `Unreleased` heading to `Version X.Y.Z`, run `uv version X.Y.Z`, and commit the three files.

The `check` job refuses to release when `CHANGELOG.md` has no `Version X.Y.Z` section, or when `Unreleased` still has entries. The GitHub release notes are copied from the `Version X.Y.Z` section.

### When something fails

- **`check` fails**: nothing was published. Fix it in a new commit and push. The release runs again since the version is still untagged.
- **`publish-pypi` fails**, for example on a trusted publisher misconfiguration: fix the cause, then re-run the failed jobs of that workflow run.
- **`release` fails after PyPI succeeded**: re-run the failed `release` job of that workflow run. Do not push another commit first. The version is still untagged, so that push would try to publish again, and PyPI rejects files that already exist.

A version published to PyPI is final, even if deleted. To fix a bad release, release a new version.
