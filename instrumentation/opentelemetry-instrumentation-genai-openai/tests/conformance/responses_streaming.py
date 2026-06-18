# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Conformance scenario: OpenAI Responses API streaming.

Currently skipped: the Responses streaming wrapper does not yet emit the
streaming timing metrics (time-to-first-chunk / time-per-output-chunk). When
that is wired up, un-skip this scenario in ``test_conformance.py``.
"""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from opentelemetry.instrumentation.genai.openai import OpenAIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.test_util_genai.conformance import Scenario
from opentelemetry.test_util_genai.instrumentor import instrument

DEFAULT_MODEL = "gpt-4o-mini"


class ResponsesStreamingScenario(Scenario):
    expected_spans = ("chat",)
    expected_metrics = (
        "gen_ai.client.operation.duration",
        "gen_ai.client.token.usage",
        "gen_ai.client.operation.time_to_first_chunk",
        "gen_ai.client.operation.time_per_output_chunk",
    )

    def run(
        self,
        *,
        tracer_provider: TracerProvider,
        meter_provider: MeterProvider,
        logger_provider: LoggerProvider,
        vcr: Any,
    ) -> None:
        with instrument(
            OpenAIInstrumentor(),
            tracer_provider=tracer_provider,
            logger_provider=logger_provider,
            meter_provider=meter_provider,
            semconv="gen_ai_latest_experimental",
            content_capture="SPAN_ONLY",
        ):
            with vcr.use_cassette(
                "test_responses_create_streaming[content_mode0].yaml"
            ):
                with OpenAI().responses.create(
                    model=DEFAULT_MODEL,
                    instructions="You are a helpful assistant.",
                    input="Say this is a test",
                    service_tier="default",
                    stream=True,
                ) as stream:
                    for _ in stream:
                        pass
