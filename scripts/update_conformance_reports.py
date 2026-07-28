#!/usr/bin/env python3

# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Render semconv coverage reports from committed conformance data.

Reads every ``instrumentation/<pkg>/tests/conformance/data.json`` written by
the conformance runs and renders the report pages under
``docs/conformance/reports/`` plus an index in ``docs/conformance/README.md``.

The rendering itself is ``semconv_genai.report`` from the pinned
semantic-conventions-genai checkout, so the pages match the ones that repo
publishes and follow its layout changes for free. Only two things there are
bound to its own ``scenarios/<lib>/`` layout, and both are redirected below:
where library data is loaded from, and what a library links to.

Usage::

    uv run python scripts/update_conformance_reports.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from opentelemetry.test_util_genai._semconv_reference import (
    load_scenario_data,
    reference_tooling,
)
from opentelemetry.test_util_genai._setup_weaver import (
    _load_version_pins,
    _workspace_root,
)

DATA_FILES_GLOB = "instrumentation/*/tests/conformance/data.json"

# Upstream links its report pages at the semconv docs sitting next to them in
# its own tree; we have no local copy, so point at the pinned revision.
UPSTREAM_DOCS_PREFIX = "](../../docs/"


def _library_name(package_dir: Path) -> str:
    name = package_dir.name
    for prefix in ("opentelemetry-instrumentation-", "genai-"):
        name = name.removeprefix(prefix)
    return name


def _conformance_dirs() -> dict[str, Path]:
    return {
        _library_name(p.parents[2]): p.parent
        for p in _workspace_root().glob(DATA_FILES_GLOB)
    }


def _load_entries() -> list[Any]:
    """Load every package's conformance data as upstream ``ScenarioDataEntry``."""
    entries = []
    for data_file in sorted(_workspace_root().glob(DATA_FILES_GLOB)):
        library = _library_name(data_file.parents[2])
        data = json.loads(data_file.read_text(encoding="utf-8"))
        entries.append(load_scenario_data(data, library))
    return entries


def _semconv_docs_url() -> str:
    pins = _load_version_pins(_workspace_root() / "versions.env")
    return (
        "](https://github.com/open-telemetry/semantic-conventions-genai/blob/"
        f"{pins['SEMCONV_GENAI_REF']}/docs/"
    )


def _report_module(conformance_dirs: dict[str, Path]) -> Any:
    """Import upstream's renderer with our data sources bound into it.

    Both patches must land before ``semconv_genai.report`` is imported: it
    pulls the two names in by value, so patching afterwards has no effect.
    """
    tooling = reference_tooling()
    import semconv_genai  # noqa: PLC0415

    semconv_genai.reference_scenario_file = conformance_dirs.__getitem__
    tooling.data_files.load_scenario_data_files = _load_entries

    from semconv_genai import report  # noqa: PLC0415

    return report


def main() -> None:
    conformance_dirs = _conformance_dirs()
    report = _report_module(conformance_dirs)

    docs_dir = _workspace_root() / "docs" / "conformance"
    report.write_status_report(docs_dir / "README.md")

    rendered = {
        report._report_filename(type_key, kind)  # noqa: SLF001
        for kind, type_order in (
            ("span", report.SPAN_TYPE_ORDER),
            ("event", report.EVENT_TYPE_ORDER),
            ("metric", getattr(report, "METRIC_TYPE_ORDER", ())),
        )
        for type_key in type_order
    }

    docs_url = _semconv_docs_url()
    for page in sorted((docs_dir / "reports").glob("*.md")):
        if page.name not in rendered:
            page.unlink()
            continue
        page.write_text(
            page.read_text(encoding="utf-8").replace(
                UPSTREAM_DOCS_PREFIX, docs_url
            ),
            encoding="utf-8",
        )

    print(f"Wrote {len(rendered)} report pages under {docs_dir / 'reports'}")


if __name__ == "__main__":
    main()
