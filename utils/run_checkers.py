#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["packaging"]
# ///
"""Runs Ruff, each type checker for the oldest and newest Python it checks for, and stubtest, like CI does.

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

from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parent.parent
# `uv run` points this to the script's own environment, which would make every nested `uv run` warn
ENV = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
if sys.stdout.isatty():
    # Output is captured, so the tools can't see the terminal themselves.
    # mypy and Ruff read `FORCE_COLOR`, ty reads `CLICOLOR_FORCE`. pyright never colors its output.
    ENV["FORCE_COLOR"] = ENV["CLICOLOR_FORCE"] = "1"
UV_RUN = ("uv", "run", "--locked")
STUBTEST = (
    "python",
    "-m",
    "mypy.stubtest",
    "Xlib",
    "--mypy-config-file=mypy.ini",
    "--allowlist=stubtest_allowlist.txt",
    # Like typeshed, stub-only private types must be marked `@type_check_only`
    "--strict-type-check-only",
)


def run(*command: str) -> str:
    # stderr goes to the terminal, so a failure shows why
    return subprocess.run(
        command, cwd=ROOT, env=ENV, check=True, stdout=subprocess.PIPE, text=True
    ).stdout


def newest_python() -> str:
    """The newest stable CPython uv knows about, prereleases excluded."""
    listing = json.loads(run("uv", "python", "list", "--all-versions", "--output-format=json"))
    major, minor = max(
        (python["version_parts"]["major"], python["version_parts"]["minor"])
        for python in listing
        if python["implementation"] == "cpython"
        and re.fullmatch(r"\d+\.\d+\.\d+", python["version"])
    )
    return f"{major}.{minor}"


def mypy_minors(newest: str) -> tuple[list[int], list[int]]:
    """The Python 3 minor versions the old and the new mypy install on, from their markers in pyproject.toml.

    For example, `mypy<1.6; python_version >= '3.8' and python_version < '3.10'` installs on `[8, 9]`.
    """
    with (ROOT / "pyproject.toml").open("rb") as file:
        group = tomllib.load(file)["dependency-groups"]["mypy"]
    newest_minor = int(newest.split(".")[1])
    minors = sorted(
        [
            minor
            for minor in range(newest_minor + 1)
            if requirement.marker is None
            or requirement.marker.evaluate(
                {"python_version": f"3.{minor}", "python_full_version": f"3.{minor}.0"}
            )
        ]
        for requirement in map(Requirement, filter(lambda entry: isinstance(entry, str), group))
        if requirement.name == "mypy"
    )
    if len(minors) != 2 or not all(minors):
        sys.exit(
            "error: the `mypy` group of pyproject.toml needs one old and one new `mypy` requirement,"
            f" each installable on Python 3.0 to {newest}"
        )
    old, new = minors
    return old, new


def isolated_mypy(python: str) -> tuple[str, ...]:
    """Runs the `mypy` group in a throwaway environment on `python`."""
    # `--quiet` hides the "Installed N packages" that the throwaway environment prints every run
    return (*UV_RUN, "--isolated", "--quiet", "--python", python, "--only-group=mypy")


def check(command: tuple[str, ...]) -> tuple[int, bytes]:
    result = subprocess.run(
        command, cwd=ROOT, env=ENV, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    return result.returncode, result.stdout


def main() -> int:
    newest = newest_python()
    old_mypy_minors, new_mypy_minors = mypy_minors(newest)
    old_mypy = isolated_mypy(f">=3.{old_mypy_minors[0]},<3.{old_mypy_minors[-1] + 1}")
    oldest_mypy = run(
        *old_mypy,
        "python",
        "-c",
        'import mypy.defaults as d; print(*d.PYTHON3_VERSION_MIN, sep=".")',
    ).strip()
    # Compares the stubs with the runtime of the Python it runs on, not a `--python-version`.
    # The old mypy can't: it checks for Python 3.8 with a typeshed that lacks what `Xlib/_typing.pyi` imports there.
    oldest_stubtest = f"3.{new_mypy_minors[0]}"

    checks = {
        # `--level=warning` hides one "Analysis of function is skipped because it is unannotated" per untyped function
        f"pyright (Python {newest})": (
            *UV_RUN,
            "pyright",
            "--level=warning",
            "--pythonversion",
            newest,
        ),
        "pyright (oldest, from pyrightconfig.json)": (*UV_RUN, "pyright", "--level=warning"),
        f"mypy (Python {newest})": (*UV_RUN, "mypy", "--python-version", newest),
        f"mypy (Python {oldest_mypy})": (*old_mypy, "mypy", "--python-version", oldest_mypy),
        "ruff": (*UV_RUN, "ruff", "check"),
        "ty (oldest, from ty.toml)": (*UV_RUN, "ty", "check"),
        f"ty (Python {newest})": (*UV_RUN, "ty", "check", "--python-version", newest),
        f"stubtest (Python {oldest_stubtest})": (*isolated_mypy(oldest_stubtest), *STUBTEST),
        f"stubtest (Python {newest})": (*isolated_mypy(newest), *STUBTEST),
    }

    failed = []
    with ThreadPoolExecutor(max_workers=len(checks)) as executor:
        futures = {label: executor.submit(check, command) for label, command in checks.items()}
        for label, future in futures.items():
            returncode, output = future.result()
            print("\n==>", label, flush=True)
            sys.stdout.buffer.write(output)
            sys.stdout.buffer.flush()
            if returncode:
                failed.append(label)

    if failed:
        print("\nFailed, rerun one with the command below it:", file=sys.stderr)
        for label in failed:
            print(f"  {label}\n    {shlex.join(checks[label])}", file=sys.stderr)
        return 1
    print("\nAll checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
