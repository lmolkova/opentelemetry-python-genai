# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Access the ``semconv_genai`` report tooling from the pinned genai registry.

``_setup_weaver`` already downloads the whole ``semantic-conventions-genai``
repo at the SHA pinned in ``versions.env``, which ships the tooling that
generates the upstream coverage reports under ``reference/src/semconv_genai``.
Importing it from there keeps span classification and semconv requirement
levels in lockstep with the registry weaver validates against, instead of
duplicating them here.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from opentelemetry.test_util_genai._setup_weaver import _provision_genai_root


@dataclass(frozen=True)
class ReferenceTooling:
    classify: ModuleType
    data_files: ModuleType
    parse_results: ModuleType


_tooling: ReferenceTooling | None = None


def reference_tooling() -> ReferenceTooling:
    """Import ``semconv_genai`` from the pinned genai registry checkout."""
    global _tooling  # noqa: PLW0603
    if _tooling is not None:
        return _tooling

    src = _provision_genai_root() / "reference" / "src"
    if not (src / "semconv_genai").is_dir():
        raise RuntimeError(
            f"{src / 'semconv_genai'} not found. The report tooling ships with "
            "semantic-conventions-genai; check the SEMCONV_GENAI_REF pin in "
            "versions.env."
        )
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

    import semconv_genai.classify as classify  # noqa: PLC0415
    import semconv_genai.data_files as data_files  # noqa: PLC0415
    import semconv_genai.parse_results as parse_results  # noqa: PLC0415

    _tooling = ReferenceTooling(
        classify=classify,
        data_files=data_files,
        parse_results=parse_results,
    )
    return _tooling


def build_scenario_data(
    weaver_reports_dir: Path, library: str
) -> dict[str, Any]:
    """Reduce a library's weaver live-check reports to a ``data.json`` payload."""
    tooling = reference_tooling()
    result = tooling.parse_results.parse_result_dir(
        weaver_reports_dir, library, tooling.classify.classify_span
    )
    if result is None:
        raise RuntimeError(
            f"No weaver live-check reports found under {weaver_reports_dir}"
        )
    data, _ = tooling.data_files._build_single_scenario_data(result)  # noqa: SLF001
    return data


def load_scenario_data(data: dict[str, Any], library: str) -> Any:
    """Normalize a ``data.json`` payload into a ``ScenarioDataEntry``."""
    tooling = reference_tooling()
    return tooling.data_files._normalize_scenario_data_entry(data, library)  # noqa: SLF001
