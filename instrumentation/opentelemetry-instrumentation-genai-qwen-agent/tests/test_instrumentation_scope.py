# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from qwen_agent.agents import Assistant

from opentelemetry.instrumentation.genai.qwen_agent import __version__
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)

SCOPE = "opentelemetry.instrumentation.genai.qwen_agent"


def test_instrumentation_scope(
    span_exporter, metric_reader, instrument_with_content, vcr
):
    bot = Assistant(
        llm={"model": "qwen-max", "model_type": "qwen_dashscope"},
        name="TestAssistant",
        description="A test assistant.",
        system_message="You are a helpful assistant.",
    )
    with vcr.use_cassette("test_agent_run.yaml"):
        assert list(
            bot.run([{"role": "user", "content": "Hello, what is 1+1?"}])
        )

    assert_instrumentation_scope(
        SCOPE,
        __version__,
        span_exporter=span_exporter,
        metric_reader=metric_reader,
    )
