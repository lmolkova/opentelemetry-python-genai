# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Provision advice policies and the semconv registry for weaver.

The registry source is ``open-telemetry/semantic-conventions-genai``,
whose ``model/manifest.yaml`` depends on a filtered copy of the upstream
``open-telemetry/semantic-conventions`` registry with the migrated GenAI
subdirectories and groups stripped out (so Weaver doesn't see duplicate
group ids). This module reproduces the genai repo's ``make filter-upstream``
target in Python.

Once https://github.com/open-telemetry/weaver/issues/1455 is fixed and the
genai repo drops its ``.build/sc-upstream-filtered`` workaround, the
filter step and migration tables below become dead code.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

# Bounds the fetch of the registry tarballs so a slow/unreachable
# GitHub doesn't hang conformance runs until the OS-level socket timeout.
_FETCH_TIMEOUT_SECONDS = 60

# Mirrors `SC_UPSTREAM_MIGRATED_{DIRS,GROUPS}` in the genai repo's Makefile.
_MIGRATED_DIRS: tuple[str, ...] = ("gen-ai", "mcp", "openai")
_MIGRATED_GROUPS: tuple[tuple[str, str], ...] = (
    ("aws/registry.yaml", "registry.aws.bedrock"),
)

logger = logging.getLogger(__name__)


def _workspace_root() -> Path:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        if (ancestor / "versions.env").is_file() and (
            ancestor / "policies"
        ).is_dir():
            return ancestor
    raise RuntimeError(
        f"Could not locate the genai workspace root (walked up from {here} "
        "looking for versions.env + policies/)."
    )


def _load_version_pins(path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise RuntimeError(f"Invalid version pin in {path}: {raw_line!r}")
        pins[key.strip()] = value.strip().strip('"').strip("'")
    return pins


def _cache_dir() -> Path:
    override = os.environ.get("SEMCONV_CACHE")
    if override:
        return Path(override)
    return Path.home() / ".cache" / "otel-conformance" / "semconv"


def _download_and_extract(url: str, target: Path, label: str) -> None:
    """Download ``url`` (a .tar.gz) and extract its single top-level dir into ``target``."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        dir=str(target.parent), prefix=f"{label}-"
    ) as tmp:
        tmp_path = Path(tmp)
        archive_path = tmp_path / "src.tar.gz"
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        logger.info("Fetching %s from %s", label, url)
        try:
            with (
                urllib.request.urlopen(
                    url, timeout=_FETCH_TIMEOUT_SECONDS
                ) as response,
                archive_path.open("wb") as out,
            ):
                shutil.copyfileobj(response, out)
        except (TimeoutError, urllib.error.URLError) as exc:
            raise RuntimeError(
                f"Failed to fetch {label} from {url}: {exc}"
            ) from exc
        with tarfile.open(archive_path, "r:gz") as archive:
            archive.extractall(extract_dir, filter="data")

        entries = [p for p in extract_dir.iterdir() if p.is_dir()]
        if len(entries) != 1:
            raise RuntimeError(
                f"Unexpected layout in {label} archive: "
                f"{[p.name for p in entries]}"
            )
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(entries[0]), str(target))


def _strip_group_block(text: str, group_id: str) -> str:
    """Drop the YAML block for ``- id: <group_id>`` from a Weaver registry file."""
    keep: list[str] = []
    skip = False
    prefix = "  - id: "
    target_line = prefix + group_id
    for line in text.splitlines(keepends=True):
        if line.startswith(prefix):
            skip = line.rstrip("\r\n") == target_line
        if not skip:
            keep.append(line)
    return "".join(keep)


def _materialize_filtered_upstream(
    genai_root: Path, upstream_root: Path
) -> Path:
    """Build ``<genai_root>/.build/sc-upstream-filtered`` from ``upstream_root``."""
    filtered = genai_root / ".build" / "sc-upstream-filtered"
    filtered.parent.mkdir(parents=True, exist_ok=True)
    if filtered.exists():
        shutil.rmtree(filtered)
    shutil.copytree(upstream_root / "model", filtered)

    for migrated in _MIGRATED_DIRS:
        migrated_path = filtered / migrated
        if migrated_path.exists():
            shutil.rmtree(migrated_path)

    for relative_file, group_id in _MIGRATED_GROUPS:
        target = filtered / relative_file
        if not target.is_file():
            continue
        original = target.read_text(encoding="utf-8")
        stripped = _strip_group_block(original, group_id)
        if stripped == original:
            logger.warning(
                "Migrated group %r not found in %s — list may be stale",
                group_id,
                relative_file,
            )
        target.write_text(stripped, encoding="utf-8")
    return filtered


def _rewrite_manifest_dependency(genai_root: Path, filtered: Path) -> None:
    """Bake an absolute ``registry_path`` into ``model/manifest.yaml``.

    Weaver resolves the manifest's relative ``./.build/sc-upstream-filtered``
    against the *current working directory*, not the manifest file, so a
    relative path only works when weaver is invoked from the genai repo root.
    """
    manifest = genai_root / "model" / "manifest.yaml"
    pattern = re.compile(
        r"^(\s*registry_path:\s*)\./\.build/sc-upstream-filtered\s*$",
        re.MULTILINE,
    )
    abs_path = filtered.resolve().as_posix()
    new_text, count = pattern.subn(
        lambda m: f"{m.group(1)}{abs_path}",
        manifest.read_text(encoding="utf-8"),
    )
    if count != 1:
        raise RuntimeError(
            f"Expected exactly one filtered-upstream registry_path entry in "
            f"{manifest}, found {count}."
        )
    manifest.write_text(new_text, encoding="utf-8")


def _provision_genai_root() -> Path:
    """Fetch the pinned genai registry, materialize its upstream dependency, return its root."""
    pins = _load_version_pins(_workspace_root() / "versions.env")
    try:
        genai_ref = pins["SEMCONV_GENAI_REF"]
    except KeyError as missing:
        raise RuntimeError(
            f"versions.env is missing required pin {missing!s}"
        ) from missing

    cache_root = _cache_dir()
    genai_target = cache_root / f"genai-{genai_ref}"
    stamp = genai_target / ".provisioned"
    if stamp.is_file():
        return genai_target

    cache_root.mkdir(parents=True, exist_ok=True)
    genai_archive_url = (
        "https://github.com/open-telemetry/semantic-conventions-genai/"
        f"archive/{genai_ref}.tar.gz"
    )
    _download_and_extract(
        genai_archive_url, genai_target, label="genai-semconv"
    )

    upstream_pins = _load_version_pins(genai_target / "versions.env")
    try:
        upstream_version = upstream_pins["SEMCONV_VERSION"]
    except KeyError as missing:
        raise RuntimeError(
            f"genai repo's versions.env is missing {missing!s}"
        ) from missing

    upstream_target = cache_root / f"upstream-{upstream_version}"
    if not (upstream_target / "model").is_dir():
        upstream_archive_url = (
            "https://github.com/open-telemetry/semantic-conventions/"
            f"archive/refs/tags/{upstream_version}.tar.gz"
        )
        _download_and_extract(
            upstream_archive_url, upstream_target, label="upstream-semconv"
        )

    filtered = _materialize_filtered_upstream(genai_target, upstream_target)
    _rewrite_manifest_dependency(genai_target, filtered)
    stamp.touch()
    return genai_target


def policies_dir() -> Path:
    """Return the ``policies`` directory with the committed advice ``.rego`` files."""
    return _workspace_root() / "policies"


# GenAI content-attribute schemas published by the semconv-genai registry under
# ``model/gen-ai``. Loaded into weaver's rego data via ``--advice-data`` and
# matched by ``policies/genai_content_validation.rego``.
_GENAI_SCHEMA_FILES: tuple[str, ...] = (
    "gen-ai-input-messages.json",
    "gen-ai-output-messages.json",
    "gen-ai-system-instructions.json",
    "gen-ai-tool-definitions.json",
    "gen-ai-retrieval-documents.json",
)


def advice_data_glob() -> str:
    """Return a ``weaver --advice-data`` glob of the GenAI content JSON schemas.

    Weaver loads every matched ``*.json`` into rego data keyed by filename stem
    (``gen-ai-input-messages.json`` -> ``data["gen-ai-input-messages"]``), which
    ``policies/genai_content_validation.rego`` validates content attributes
    against. The schemas come straight from the pinned semconv-genai registry
    (https://github.com/open-telemetry/semantic-conventions-genai/tree/main/model/gen-ai);
    the only rewrite is swapping the external draft-07 meta-schema ``$ref`` for a
    local ``"type": "object"`` because weaver's rego engine can't fetch it at
    eval time.
    """
    source = _provision_genai_root() / "model" / "gen-ai"
    target = _provision_genai_root() / ".build" / "advice-data"
    target.mkdir(parents=True, exist_ok=True)
    for filename in _GENAI_SCHEMA_FILES:
        schema_path = source / filename
        if not schema_path.is_file():
            logger.warning(
                "GenAI schema not found: %s (skipping)", schema_path
            )
            continue
        normalized = schema_path.read_text(encoding="utf-8").replace(
            '"$ref": "http://json-schema.org/draft-07/schema#"',
            '"type": "object"',
        )
        (target / filename).write_text(normalized, encoding="utf-8")
    return str(target / "*.json")


def semconv_registry() -> Path:
    """Return the path to ``<semantic-conventions-genai>/model`` for the pinned ref."""
    return _provision_genai_root() / "model"


def weaver_config_file() -> Path:
    """Return the path to the workspace ``.weaver.toml``."""
    return _workspace_root() / ".weaver.toml"
