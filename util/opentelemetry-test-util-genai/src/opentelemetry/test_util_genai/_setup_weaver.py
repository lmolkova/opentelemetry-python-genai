# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Provision advice policies and the semconv registry for weaver.

The weaver binary is installed by CI (see ``.github/workflows/test.yml``)
or locally by the contributor — this module only handles the schema / registry
side. Both ``policies_dir()`` and ``semconv_registry()`` read the
``SEMCONV_VERSION`` pin from ``versions.env`` and share one cached
semantic-conventions tarball.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# Bounds the fetch of the semantic-conventions tarball so a slow/unreachable
# GitHub doesn't hang conformance runs until the OS-level socket timeout.
_FETCH_TIMEOUT_SECONDS = 60

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


def _load_version_pins() -> dict[str, str]:
    content = (_workspace_root() / "versions.env").read_text(encoding="utf-8")
    pins: dict[str, str] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise RuntimeError(
                f"Invalid version pin in versions.env: {raw_line!r}"
            )
        pins[key.strip()] = value.strip().strip('"').strip("'")
    return pins


def _cache_dir() -> Path:
    override = os.environ.get("SEMCONV_CACHE")
    if override:
        return Path(override)
    return Path.home() / ".cache" / "otel-conformance" / "semconv"


def _fetch_semconv(version: str) -> Path:
    """Download `semantic-conventions` at ``version`` and return the extracted root."""
    cache_root = _cache_dir()
    safe = version.replace("/", "_")
    target = cache_root / safe
    if (target / "model").is_dir() and (target / "docs" / "gen-ai").is_dir():
        return target

    cache_root.mkdir(parents=True, exist_ok=True)
    url = (
        "https://github.com/open-telemetry/semantic-conventions/"
        f"archive/refs/tags/{version}.tar.gz"
    )
    with tempfile.TemporaryDirectory(
        dir=str(cache_root), prefix=f"semconv-{safe}-"
    ) as tmp:
        tmp_path = Path(tmp)
        archive_path = tmp_path / "src.tar.gz"
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        logger.info("Fetching semantic-conventions @ %s", version)
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
                f"Failed to fetch semantic-conventions @ {version} from {url}: "
                f"{exc}"
            ) from exc
        with tarfile.open(archive_path, "r:gz") as archive:
            archive.extractall(extract_dir, filter="data")

        entries = [p for p in extract_dir.iterdir() if p.is_dir()]
        if len(entries) != 1:
            raise RuntimeError(
                "Unexpected layout in semantic-conventions archive: "
                f"{[p.name for p in entries]}"
            )
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(entries[0]), str(target))
    return target


def _semconv_root() -> Path:
    return _fetch_semconv(_load_version_pins()["SEMCONV_VERSION"])


# `_schema_<key>` constants referenced from
# policies/genai_content_validation.rego.
_GENAI_SCHEMA_FILES: dict[str, str] = {
    "input_messages": "gen-ai-input-messages.json",
    "output_messages": "gen-ai-output-messages.json",
    "system_instructions": "gen-ai-system-instructions.json",
    "tool_definitions": "gen-ai-tool-definitions.json",
    "retrieval_documents": "gen-ai-retrieval-documents.json",
}


def _generate_schemas_rego(schemas: dict[str, Any]) -> str:
    lines = [
        "# Auto-generated from semantic-conventions. Do not edit.",
        "# Re-generated each time _setup_weaver.policies_dir() runs.",
        "package live_check_advice",
        "",
        "import rego.v1",
        "",
    ]
    for key, schema in schemas.items():
        if schema is None:
            lines.append(f"_schema_{key} := null")
        else:
            # indent=2 to stay under weaver's 1024-char-per-line rego limit.
            lines.append(f"_schema_{key} := {json.dumps(schema, indent=2)}")
        lines.append("")
    return "\n".join(lines)


def policies_dir() -> Path:
    """Write ``policies/_schemas.rego`` and return the policies directory."""
    docs_genai = _semconv_root() / "docs" / "gen-ai"

    schemas: dict[str, Any] = {}
    for key, filename in _GENAI_SCHEMA_FILES.items():
        schema_path = docs_genai / filename
        if schema_path.exists():
            # OPA's json.match_schema can't fetch the draft-07 meta-schema at
            # eval time; swap the external $ref for a local "must be an object".
            schemas[key] = json.loads(
                schema_path.read_text(encoding="utf-8").replace(
                    '"$ref": "http://json-schema.org/draft-07/schema#"',
                    '"type": "object"',
                )
            )
        else:
            logger.warning(
                "GenAI schema not found: %s (emitting null stub)", schema_path
            )
            schemas[key] = None

    policies = _workspace_root() / "policies"
    (policies / "_schemas.rego").write_text(
        _generate_schemas_rego(schemas), encoding="utf-8"
    )
    return policies


def semconv_registry() -> Path:
    """Return the path to ``<semantic-conventions>/model`` for the pinned tag."""
    return _semconv_root() / "model"
