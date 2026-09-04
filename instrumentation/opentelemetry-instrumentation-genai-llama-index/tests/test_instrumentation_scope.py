# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from __future__ import annotations

import pytest
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.base.llms.types import ToolCallBlock
from llama_index.core.llms import ChatMessage, MockFunctionCallingLLM
from llama_index.core.tools import FunctionTool

from opentelemetry.instrumentation.genai.llama_index import (
    LlamaIndexInstrumentor,
    __version__,
)
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)
from opentelemetry.test_util_genai.instrumentor import instrument

SCOPE = "opentelemetry.instrumentation.genai.llama_index"


@pytest.mark.asyncio
async def test_instrumentation_scope(
    span_exporter,
    metric_reader,
    tracer_provider,
    logger_provider,
    meter_provider,
) -> None:
    async def weather(city: str) -> str:
        """Get the weather for a city."""
        return f"Sunny in {city}"

    def function_response(messages, **kwargs):
        if any(message.role.value == "tool" for message in messages):
            return ChatMessage(role="assistant", content="It is sunny.")
        return ChatMessage(
            role="assistant",
            blocks=[
                ToolCallBlock(
                    tool_call_id="weather-call",
                    tool_name="weather",
                    tool_kwargs={"city": "Paris"},
                )
            ],
        )

    agent = FunctionAgent(
        name="weather-agent",
        llm=MockFunctionCallingLLM(
            is_chat_model=True, response_generator=function_response
        ),
        tools=[FunctionTool.from_defaults(async_fn=weather)],
        streaming=False,
    )

    with instrument(
        LlamaIndexInstrumentor(),
        tracer_provider=tracer_provider,
        logger_provider=logger_provider,
        meter_provider=meter_provider,
    ):
        await agent.run(user_msg="What is the weather in Paris?")

    assert_instrumentation_scope(
        SCOPE,
        __version__,
        span_exporter=span_exporter,
        metric_reader=metric_reader,
    )
