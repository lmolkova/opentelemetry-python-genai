#!/usr/bin/env python3
# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
# /// script
# requires-python = ">=3.10"
# dependencies = ["ruff==0.16.1"]
# ///

from __future__ import annotations

import hashlib
import lzma
import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).with_name("templates")
OUTPUT = (
    ROOT / "util/opentelemetry-util-genai/src/opentelemetry/util/genai/semconv"
)


def _versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for line in (ROOT / "versions.env").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            name, value = line.split("=", 1)
            versions[name] = value
    return versions


def _asset_name() -> str:
    system = platform.system()
    machine = platform.machine().lower()
    architecture = "aarch64" if machine in {"arm64", "aarch64"} else "x86_64"
    if system == "Darwin":
        return f"weaver-{architecture}-apple-darwin.tar.xz"
    if system == "Linux":
        return f"weaver-{architecture}-unknown-linux-gnu.tar.xz"
    if system == "Windows" and architecture == "x86_64":
        return "weaver-x86_64-pc-windows-msvc.zip"
    raise RuntimeError(f"Unsupported Weaver platform: {system} {machine}")


def _download(url: str, destination: Path) -> None:
    with urllib.request.urlopen(url) as response:
        destination.write_bytes(response.read())


def _install_weaver(version: str) -> Path:
    override = os.environ.get("WEAVER")
    if override:
        return Path(override)

    cache_root = (
        Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        / "opentelemetry-python-genai"
    )
    executable = (
        cache_root
        / "weaver"
        / version
        / ("weaver.exe" if platform.system() == "Windows" else "weaver")
    )
    if executable.is_file():
        return executable

    asset = _asset_name()
    base_url = (
        f"https://github.com/open-telemetry/weaver/releases/download/"
        f"{version}/{asset}"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        archive = Path(temp_dir) / asset
        checksum_file = Path(temp_dir) / f"{asset}.sha256"
        _download(base_url, archive)
        _download(f"{base_url}.sha256", checksum_file)
        expected = checksum_file.read_text().split()[0]
        actual = hashlib.sha256(archive.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Checksum mismatch for {asset}")

        executable.parent.mkdir(parents=True, exist_ok=True)
        if asset.endswith(".zip"):
            with zipfile.ZipFile(archive) as package:
                member = next(
                    name
                    for name in package.namelist()
                    if name.endswith("/weaver.exe")
                )
                executable.write_bytes(package.read(member))
        else:
            with lzma.open(archive) as compressed:
                with tarfile.open(fileobj=compressed) as package:
                    member = next(
                        item
                        for item in package.getmembers()
                        if item.isfile() and item.name.endswith("/weaver")
                    )
                    source = package.extractfile(member)
                    if source is None:
                        raise RuntimeError(
                            f"Unable to extract Weaver from {asset}"
                        )
                    executable.write_bytes(source.read())
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    return executable


def main() -> None:
    versions = _versions()
    weaver = _install_weaver(versions["WEAVER_VERSION"])
    registry = (
        "https://github.com/open-telemetry/semantic-conventions-genai.git@"
        f"{versions['SEMCONV_GENAI_REF']}[model]"
    )
    subprocess.run(
        [
            str(weaver),
            "registry",
            "generate",
            "--registry",
            registry,
            "--templates",
            str(TEMPLATES),
            "--v2",
            "python-genai",
            str(OUTPUT),
        ],
        cwd=ROOT,
        check=True,
    )
    ruff = shutil.which("ruff")
    if ruff is None:
        raise RuntimeError("ruff is required; run this script with `uv run`")
    generated_files = [
        path
        for path in OUTPUT.glob("*/*.py")
        if "Code generated" in path.read_text()[:256]
    ]
    subprocess.run(
        [ruff, "check", "--fix", *map(str, generated_files)],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [ruff, "format", *map(str, generated_files)], cwd=ROOT, check=True
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
