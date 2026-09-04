# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Shared assertions for GenAI instrumentation tests."""

from __future__ import annotations

from collections.abc import Iterable

from opentelemetry.sdk._logs.export import InMemoryLogRecordExporter
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.sdk.util.instrumentation import InstrumentationScope


def assert_instrumentation_scope(
    name: str,
    version: str,
    *,
    span_exporter: InMemorySpanExporter | None = None,
    metric_reader: InMemoryMetricReader | None = None,
    log_exporter: InMemoryLogRecordExporter | None = None,
    scopes: Iterable[InstrumentationScope] | None = None,
) -> None:
    """Assert every recorded signal is attributed to this instrumentation.

    ``TelemetryHandler`` falls back to its own module when an instrumentation
    doesn't pass ``instrumentation_scope_name``, which makes the telemetry of
    every util-genai based instrumentation indistinguishable by
    ``otel.scope.name``. Call this from one happy-path test per package.

    Pass ``scopes`` instead of an exporter for telemetry collected outside the
    shared in-memory fixtures.
    """
    recorded = list(scopes or ())
    if span_exporter is not None:
        spans = span_exporter.get_finished_spans()
        assert spans
        recorded += [span.instrumentation_scope for span in spans]
    if log_exporter is not None:
        logs = log_exporter.get_finished_logs()
        assert logs
        recorded += [log.instrumentation_scope for log in logs]
    if metric_reader is not None:
        data = metric_reader.get_metrics_data()
        assert data is not None
        scope_metrics = [
            scope_metric
            for resource_metric in data.resource_metrics
            for scope_metric in resource_metric.scope_metrics
        ]
        assert scope_metrics
        recorded += [scope_metric.scope for scope_metric in scope_metrics]

    assert recorded
    for scope in recorded:
        assert scope is not None
        assert scope.name == name
        assert scope.version == version
