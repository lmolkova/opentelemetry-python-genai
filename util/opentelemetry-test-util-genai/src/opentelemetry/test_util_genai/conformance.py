# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Per-scenario conformance runner for GenAI instrumentations.

Intended call shape from a per-package ``tests/test_conformance.py``::

    @pytest.mark.parametrize(
        "scenario", [InferenceScenario(), ToolCallingScenario()]
    )
    def test_conformance(scenario, vcr, weaver_live_check):
        report = run_conformance(scenario, vcr=vcr, weaver=weaver_live_check)
        # Optionally layer lib-specific assertions on `report` here.

The ``*-conformance`` tox envs point pytest directly at
``tests/test_conformance.py``; the regular ``*-{oldest,latest}`` envs
``--ignore`` it. The OTLP/gRPC exporter and ``weaver_live_check`` only need
to be installed in the conformance envs.

Each ``tests/conformance/<op>.py`` defines a :class:`Scenario` subclass with:

- ``expected_spans`` — maps each ``gen_ai.operation.name`` to the exact number
  of spans the report must carry it on, with no undeclared operations present.
- ``expected_metrics`` — metric names that must appear in
  ``statistics.seen_registry_metrics``.
- ``expected_violations`` — :class:`ExpectedViolation` entries for known
  gaps. ``run_conformance`` fails on undeclared violations and on declared
  entries weaver no longer reports.
- ``run(*, tracer_provider, meter_provider, logger_provider, vcr)`` — wires
  the instrumentor against the providers and exercises one semconv operation
  type's happy path inside ``vcr.use_cassette(...)``.
- ``validate(report)`` — asserts the emitted telemetry matches the scenario.
  The base implementation enforces the exact ``expected_spans`` operation
  counts and ``expected_metrics`` presence; per-scenario overrides call
  ``super().validate(report)`` and layer on additional checks against the
  weaver report.

Each run writes two artifacts: the raw weaver report to
``weaver_reports/<library>/<Scenario>.json`` (gitignored, for debugging) and
the package's semconv attribute coverage to
``instrumentation/<pkg>/tests/conformance/data.json`` (committed). The latter
feeds ``scripts/update_conformance_reports.py``, so it reflects a *full* env
run — a filtered run produces a partial file.
"""

from __future__ import annotations

import inspect
import json
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.test.weaver_live_check import (
    LiveCheckError,
    LiveCheckReport,
    WeaverLiveCheck,
)
from opentelemetry.test_util_genai._semconv_reference import (
    build_scenario_data,
)
from opentelemetry.test_util_genai._setup_weaver import _workspace_root


@dataclass(frozen=True)
class ExpectedViolation:
    """One known-and-accepted semconv violation.

    Matched by weaver advice ``id`` plus a substring of its ``message``.
    Declared entries the report no longer contains are flagged so
    suppressions don't rot.
    """

    advice_id: str
    message_substring: str

    def matches(self, violation: dict[str, Any]) -> bool:
        return violation.get(
            "id"
        ) == self.advice_id and self.message_substring in str(
            violation.get("message", "")
        )


class Scenario(ABC):
    """Base class every ``tests/conformance/<op>.py`` scenario must subclass."""

    expected_spans: ClassVar[dict[str, int]] = {}
    expected_metrics: ClassVar[tuple[str, ...]] = ()
    expected_violations: ClassVar[tuple[ExpectedViolation, ...]] = ()

    @abstractmethod
    def run(
        self,
        *,
        tracer_provider: TracerProvider,
        meter_provider: MeterProvider,
        logger_provider: LoggerProvider,
        vcr: Any,
    ) -> None: ...

    def validate(self, report: LiveCheckReport) -> None:
        """Assert the weaver live-check report matches the scenario.

        ``expected_spans`` maps each ``gen_ai.operation.name`` to the exact
        number of spans that must carry it: the report's spans must match these
        operation counts exactly — no missing, no extra. ``expected_metrics``
        entries must each appear at least once. Subclasses should override and
        call ``super().validate(report)`` to layer on extra scenario-specific
        checks against the report.
        """
        expected_spans = dict(self.expected_spans)
        seen_spans = _seen_span_operations(report)
        assert seen_spans == expected_spans, (
            f"Expected span operation counts {dict(sorted(expected_spans.items()))} "
            f"but weaver saw {dict(sorted(seen_spans.items()))}"
        )

        expected_metrics = set(self.expected_metrics)
        seen_metrics = _seen_metric_names(report)
        missing_metrics = expected_metrics - seen_metrics
        assert not missing_metrics, (
            f"Expected metrics {sorted(expected_metrics)} but weaver only "
            f"saw {sorted(seen_metrics)} — missing {sorted(missing_metrics)}"
        )


def _build_providers(
    endpoint: str,
) -> tuple[TracerProvider, MeterProvider, LoggerProvider]:
    # OTLP/gRPC exporters are only installed in the *-conformance tox envs
    # (see dev-requirements-conformance.txt). Import lazily so this module
    # stays importable in regular test envs that exclude conformance tests.
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (  # noqa: PLC0415
        OTLPLogExporter,
    )
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (  # noqa: PLC0415
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (  # noqa: PLC0415
        OTLPSpanExporter,
    )

    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    )

    # Disable periodic export — metrics flush via the explicit force_flush()
    # at the end of the scenario, so the report is deterministic.
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=endpoint, insecure=True),
        export_interval_millis=2**31 - 1,
    )
    meter_provider = MeterProvider(metric_readers=[metric_reader])

    logger_provider = LoggerProvider()
    logger_provider.add_log_record_processor(
        SimpleLogRecordProcessor(
            OTLPLogExporter(endpoint=endpoint, insecure=True)
        )
    )

    return tracer_provider, meter_provider, logger_provider


def _seen_metric_names(report: LiveCheckReport) -> set[str]:
    """Names of metrics weaver observed at least one data point for."""
    seen = report["statistics"]["seen_registry_metrics"]
    return {name for name, count in seen.items() if count}


def _seen_span_operations(report: LiveCheckReport) -> dict[str, int]:
    """`gen_ai.operation.name` counts across the report's span samples."""
    counts: dict[str, int] = {}
    for entry in report["samples"]:
        if "span" not in entry:
            continue
        for attr in entry["span"]["attributes"]:
            if attr["name"] == "gen_ai.operation.name":
                counts[attr["value"]] = counts.get(attr["value"], 0) + 1
                break
    return counts


def _package_dir(scenario: Scenario) -> Path:
    """The ``instrumentation/<pkg>`` directory the scenario is defined in."""
    path = Path(inspect.getfile(type(scenario))).resolve()
    for ancestor in path.parents:
        if ancestor.parent.name == "instrumentation":
            return ancestor
    raise RuntimeError(
        f"{type(scenario).__name__} is defined at {path}, which is not inside "
        "an instrumentation/<package> directory."
    )


def library_name(scenario: Scenario) -> str:
    """The scenario's library slug, matching the semconv-genai naming."""
    name = _package_dir(scenario).name
    for prefix in ("opentelemetry-instrumentation-", "genai-"):
        name = name.removeprefix(prefix)
    return name


# Library directories emptied so far in this process, so a renamed or deleted
# scenario leaves no stale dump behind while repeated runs stay additive.
_cleared_report_dirs: set[Path] = set()


def _report_dir(library: str) -> Path:
    out = _workspace_root() / "weaver_reports" / library
    if out not in _cleared_report_dirs:
        shutil.rmtree(out, ignore_errors=True)
        _cleared_report_dirs.add(out)
    out.mkdir(parents=True, exist_ok=True)
    return out


def _dump_report(
    scenario: Scenario, report: LiveCheckReport, library: str
) -> None:
    """Write the raw weaver report — the debugging artifact, kept verbatim."""
    out = _report_dir(library) / f"{type(scenario).__name__}.json"
    out.write_text(json.dumps(report._report, indent=2, sort_keys=True))  # noqa: SLF001


def _write_scenario_data(scenario: Scenario, library: str) -> None:
    """Refresh the package's committed semconv coverage data.

    Derived from *every* report the package has dumped this run rather than
    merged scenario by scenario: required-level attributes are the intersection
    across all spans of a type, which only holds when they are reduced together.
    """
    data = build_scenario_data(_report_dir(library), library)
    out = _package_dir(scenario) / "tests" / "conformance" / "data.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def run_conformance(
    scenario: Scenario,
    *,
    vcr: Any,
    weaver: WeaverLiveCheck,
) -> LiveCheckReport:
    """Run one conformance scenario and return the weaver report.

    Raises :class:`LiveCheckError` on undeclared violations and
    :class:`AssertionError` on declared violations weaver no longer
    reports.
    """
    tracer_provider, meter_provider, logger_provider = _build_providers(
        weaver.otlp_endpoint
    )

    try:
        scenario.run(
            tracer_provider=tracer_provider,
            meter_provider=meter_provider,
            logger_provider=logger_provider,
            vcr=vcr,
        )
        tracer_provider.force_flush()
        meter_provider.force_flush()
        logger_provider.force_flush()

        report = weaver.end(timeout=120)
        library = library_name(scenario)
        _dump_report(scenario, report, library)
        # Coverage records what weaver observed, so it is written before the
        # checks: a scenario that fails (or xfails, like the CrewAI baseline)
        # still measured something worth reporting.
        _write_scenario_data(scenario, library)

        _check_violations(scenario, report)
        scenario.validate(report)
        return report
    finally:
        tracer_provider.shutdown()
        meter_provider.shutdown()
        logger_provider.shutdown()


def _check_violations(scenario: Scenario, report: LiveCheckReport) -> None:
    """Reconcile weaver violations against ``scenario.expected_violations``."""
    violations = report.violations
    expected = scenario.expected_violations

    unexpected = [
        v for v in violations if not any(ev.matches(v) for ev in expected)
    ]
    if unexpected:
        raise LiveCheckError(
            "Unexpected semconv violations (not declared in "
            "scenario.expected_violations):\n"
            + "\n".join(f"- {v}" for v in unexpected),
            report,
        )

    unmet = [
        ev for ev in expected if not any(ev.matches(v) for v in violations)
    ]
    if unmet:
        raise AssertionError(
            "Scenario declares expected_violations that weaver did not "
            "report — likely fixed upstream. Remove these entries:\n"
            + "\n".join(f"- {ev}" for ev in unmet)
        )
