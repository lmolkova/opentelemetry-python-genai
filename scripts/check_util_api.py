#!/usr/bin/env python3
# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Fail on breaking changes to the opentelemetry-util-genai public API.

Instrumentations released from this repo accept any util version below 2, so
every 1.x util release has to keep working with them. This script uses griffe
to compare the working tree with the latest util release tag, or with
``--against <ref>``.

Intended breaks go into ``api_breaks_allowlist.txt`` in the util package
directory, one object path per line.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import griffe
from packaging.version import Version

ROOT = Path(__file__).resolve().parent.parent
UTIL_DIR = ROOT / "util" / "opentelemetry-util-genai"
SEARCH_PATH = "util/opentelemetry-util-genai/src"
PACKAGE = "opentelemetry.util.genai"
TAG_PREFIX = "opentelemetry-util-genai=="
ALLOWLIST = UTIL_DIR / "api_breaks_allowlist.txt"


def _latest_release_ref() -> str:
    tags = subprocess.run(
        ["git", "tag", "--list", f"{TAG_PREFIX}*"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    if not tags:
        sys.exit(f"No {TAG_PREFIX}* tags found; fetch tags or pass --against.")
    latest = max(tags, key=lambda t: Version(t.removeprefix(TAG_PREFIX)))
    # griffe treats refs containing "==" as PyPI specs, so pass the commit.
    return subprocess.run(
        ["git", "rev-list", "-n1", latest],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _load_allowlist() -> set[str]:
    if not ALLOWLIST.exists():
        return set()
    lines = (line.split("#", 1)[0].strip() for line in ALLOWLIST.open())
    return {line for line in lines if line}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--against",
        help="git ref to compare against (default: latest util release tag)",
    )
    args = parser.parse_args()
    ref: str = args.against or _latest_release_ref()

    old = griffe.load_git(
        PACKAGE, ref=ref, repo=ROOT, search_paths=[SEARCH_PATH]
    )
    new = griffe.load(PACKAGE, search_paths=[str(ROOT / SEARCH_PATH)])

    allowed = _load_allowlist()
    used: set[str] = set()
    failures: list[str] = []
    for breakage in griffe.find_breaking_changes(old, new):
        path = breakage.obj.path
        # Fires on any change to an attribute initializer, not an API break.
        if breakage.kind is griffe.BreakageKind.ATTRIBUTE_CHANGED_VALUE:
            continue
        if path in allowed:
            used.add(path)
            continue
        failures.append(
            breakage.explain(style=griffe.ExplanationStyle.ONE_LINE)
        )

    for path in sorted(allowed - used):
        print(f"note: stale allowlist entry, can be removed: {path}")

    if failures:
        print(f"Breaking changes to {PACKAGE} public API vs {ref}:")
        for failure in failures:
            print(f"  {failure}")
        print(
            "\nReleased instrumentations accept any util <2 and may rely on "
            "these APIs. Restore them, or if no released package uses them, "
            f"add the object paths to {ALLOWLIST.relative_to(ROOT)}."
        )
        return 1
    print(f"No breaking changes to {PACKAGE} public API vs {ref}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
