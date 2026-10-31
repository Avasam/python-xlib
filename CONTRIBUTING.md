# Contributing

## Changelog

Every user-facing change adds its entry to the `Unreleased` section at the top of [CHANGELOG.md](CHANGELOG.md), in the same commit or pull request as the change. CI, test and refactoring changes that users cannot observe need no entry.

Credit contributors other than the maintainer as `(thanks [@user][user])`, and add `[user]: https://github.com/user` to the sorted list of links at the end of the file if it is not there yet.

## Type stubs

The `.pyi` stubs in `Xlib/` come from typeshed and are licensed under Apache-2.0 (see [LICENSE-typeshed](LICENSE-typeshed)), which requires modified files to carry a prominent notice of the change. The first change to a stub adds `# Modified from typeshed` as its first line. A stub that already has that line needs nothing more.

stubtest compares the stubs with the implementation. What it reports that is not an error in the stubs goes in [stubtest_allowlist.txt](stubtest_allowlist.txt), with a comment saying why. `uv run utils/run_checkers.py` runs it with every other check.

### Supported type checker versions

Checking the oldest supported Python needs an old mypy (mypy 1.5 for Python 3.4), so the stubs must work with its bundled typeshed. A target that a newer mypy supports is assumed to be checked with that newer mypy. Dropping a Python version can drop the old mypy only it needed.

- Names that the oldest typeshed only has in `typing` on newer Pythons (`Final`, `Literal`, `TypedDict`, `TypeAlias`, ...) come from `typing_extensions`.
- Names that only a newer typeshed has go behind a `sys.version_info` gate at the oldest target that mypy supports, with a fallback below it. For example, [Xlib/_typing.pyi](Xlib/_typing.pyi) imports `ConvertibleToInt` from `_typeshed` on 3.7+ (mypy 1.7) and defines its own copy below.

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
