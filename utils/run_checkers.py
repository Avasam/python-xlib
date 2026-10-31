#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Runs Ruff, and each type checker for the oldest and newest Python it checks for, like CI does.

They all run in parallel. Each output is printed in a fixed order, then the failures are listed.
Usage: uv run utils/run_checkers.py
"""

import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# `uv run` points this to the script's own environment, which would make every nested `uv run` warn
ENV = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
if sys.stdout.isatty():
    # Output is captured, so the tools can't see the terminal themselves.
    # mypy and Ruff read `FORCE_COLOR`, ty reads `CLICOLOR_FORCE`. pyright never colors its output.
    ENV["FORCE_COLOR"] = ENV["CLICOLOR_FORCE"] = "1"
UV_RUN = ("uv", "run", "--locked")


def run(*command: str) -> str:
    return subprocess.run(
        command, cwd=ROOT, env=ENV, check=True, capture_output=True, text=True
    ).stdout


def newest_python() -> str:
    """The newest stable CPython uv knows about, prereleases excluded."""
    listing = json.loads(run("uv", "python", "list", "--all-versions", "--output-format=json"))
    return "%d.%d" % max(
        (python["version_parts"]["major"], python["version_parts"]["minor"])
        for python in listing
        if python["implementation"] == "cpython"
        and re.fullmatch(r"\d+\.\d+\.\d+", python["version"])
    )


def old_mypy_python() -> str:
    """The Pythons the old mypy from the lock file installs on, from its marker in pyproject.toml.

    For example, `python_version >= '3.8' and python_version < '3.10'` becomes `>=3.8,<3.10`.
    """
    with (ROOT / "pyproject.toml").open("rb") as file:
        group = tomllib.load(file)["dependency-groups"]["mypy"]
    for requirement in group:
        if isinstance(requirement, str) and requirement.startswith("mypy<"):
            marker = requirement.partition(";")[2]
            specifier = ",".join(
                operator + version
                for operator, version in re.findall(
                    r"python_version\s*([<>=!]+)\s*['\"]([\d.]+)['\"]", marker
                )
            )
            if specifier:
                return specifier
    sys.exit('error: no "mypy<...; python_version ..." entry in the `mypy` group of pyproject.toml')


def check(command: tuple[str, ...]) -> tuple[int, bytes]:
    result = subprocess.run(
        command, cwd=ROOT, env=ENV, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    return result.returncode, result.stdout


def main() -> int:
    newest = newest_python()
    # `--quiet` hides the "Installed N packages" that the throwaway environment prints every run
    old_mypy = (
        *UV_RUN,
        "--isolated",
        "--quiet",
        "--python=" + old_mypy_python(),
        "--only-group=mypy",
    )
    oldest_mypy = run(
        *old_mypy,
        "python",
        "-c",
        'import mypy.defaults as d; print("%d.%d" % d.PYTHON3_VERSION_MIN)',
    ).strip()

    checks = {
        # `--level=warning` hides one "Analysis of function is skipped because it is unannotated" per untyped function
        "pyright (Python %s)" % newest: (
            *UV_RUN,
            "pyright",
            "--level=warning",
            "--pythonversion=" + newest,
        ),
        "pyright (oldest, from pyrightconfig.json)": (*UV_RUN, "pyright", "--level=warning"),
        "mypy (Python %s)" % newest: (*UV_RUN, "mypy", "--python-version=" + newest),
        "mypy (Python %s)" % oldest_mypy: (*old_mypy, "mypy", "--python-version=" + oldest_mypy),
        "ruff": (*UV_RUN, "ruff", "check"),
        "ty (oldest, from ty.toml)": (*UV_RUN, "ty", "check"),
        "ty (Python %s)" % newest: (*UV_RUN, "ty", "check", "--python-version=" + newest),
    }

    failed = []
    with ThreadPoolExecutor(max_workers=len(checks)) as executor:
        futures = {label: executor.submit(check, command) for label, command in checks.items()}
        for label, future in futures.items():
            returncode, output = future.result()
            print("\n==> " + label, flush=True)
            sys.stdout.buffer.write(output)
            sys.stdout.buffer.flush()
            if returncode:
                failed.append(label)

    if failed:
        print("\nFailed, rerun one with the command below it:", file=sys.stderr)
        for label in failed:
            print("  %s\n    %s" % (label, shlex.join(checks[label])), file=sys.stderr)
        return 1
    print("\nAll checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
