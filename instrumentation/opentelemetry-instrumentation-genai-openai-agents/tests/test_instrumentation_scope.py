# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from __future__ import annotations

from typing import Any

import agents
import pytest

from opentelemetry.instrumentation.genai.openai_agents import (
    OpenAIAgentsInstrumentor,
    __version__,
)
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)
from opentelemetry.test_util_genai.instrumentor import instrument

from .test_instrumentor import _get_weather

SCOPE = "opentelemetry.instrumentation.genai.openai_agents"


@pytest.mark.asyncio
async def test_instrumentation_scope(
    tracer_provider: TracerProvider,
    logger_provider: Any,
    meter_provider: Any,
    span_exporter: InMemorySpanExporter,
    metric_reader: InMemoryMetricReader,
    vcr: Any,
) -> None:
    with instrument(
        OpenAIAgentsInstrumentor(),
        tracer_provider=tracer_provider,
        logger_provider=logger_provider,
        meter_provider=meter_provider,
        content_capture="SPAN_ONLY",
    ):
        agent = agents.Agent(
            name="test_agent", model="gpt-4o-mini", tools=[_get_weather]
        )
        with vcr.use_cassette("test_runner_records_tool_call_arguments.yaml"):
            await agents.Runner.run(
                agent, "what is the weather in Barcelona?"
            )

    assert_instrumentation_scope(
        SCOPE,
        __version__,
        span_exporter=span_exporter,
        metric_reader=metric_reader,
    )
