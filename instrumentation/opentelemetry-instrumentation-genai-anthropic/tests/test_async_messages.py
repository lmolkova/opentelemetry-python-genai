# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Tests for async Messages.create instrumentation."""

import inspect
import json

import pytest
from anthropic import APIConnectionError, AsyncAnthropic, NotFoundError
from anthropic.resources.messages import AsyncMessages as _AsyncMessages

from opentelemetry.instrumentation.genai.anthropic.messages_extractors import (
    GEN_AI_USAGE_CACHE_CREATION_INPUT_TOKENS,
    GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS,
)
from opentelemetry.instrumentation.genai.anthropic.wrappers import (
    AsyncMessagesStreamWrapper,
)
from opentelemetry.semconv._incubating.attributes import (
    error_attributes as ErrorAttributes,
)
from opentelemetry.semconv._incubating.attributes import (
    gen_ai_attributes as GenAIAttributes,
)
from opentelemetry.semconv._incubating.attributes import (
    server_attributes as ServerAttributes,
)

_create_params = set(inspect.signature(_AsyncMessages.create).parameters)
_has_tools_param = "tools" in _create_params
_has_thinking_param = "thinking" in _create_params


def normalize_stop_reason(stop_reason):
    """Map Anthropic stop reasons to GenAI semconv values."""
    return {
        "end_turn": "stop",
        "stop_sequence": "stop",
        "max_tokens": "length",
        "tool_use": "tool_calls",
    }.get(stop_reason, stop_reason)


def expected_input_tokens(usage):
    """Compute semconv input tokens from Anthropic usage."""
    base = getattr(usage, "input_tokens", 0) or 0
    cache_creation = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    return base + cache_creation + cache_read


def _load_span_messages(span, attribute):
    value = span.attributes.get(attribute)
    assert value is not None
    assert isinstance(value, str)
    parsed = json.loads(value)
    assert isinstance(parsed, list)
    return parsed


class _AsyncErrorInjectingStreamDelegate:
    def __init__(self, inner):
        self._inner = inner
        self._count = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._count == 1:
            raise ConnectionError("connection reset during stream")
        self._count += 1
        return await self._inner.__anext__()

    async def close(self):
        return await self._inner.close()

    def __getattr__(self, name):
        return getattr(self._inner, name)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_basic(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test basic async message creation produces correct span."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    response = await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.name == f"chat {model}"
    assert span.attributes[GenAIAttributes.GEN_AI_OPERATION_NAME] == "chat"
    assert span.attributes[GenAIAttributes.GEN_AI_PROVIDER_NAME] == "anthropic"
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_ID] == response.id
    assert (
        span.attributes[GenAIAttributes.GEN_AI_RESPONSE_MODEL]
        == response.model
    )
    assert span.attributes[
        GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS
    ] == expected_input_tokens(response.usage)
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS]
        == response.usage.output_tokens
    )
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS] == (
        normalize_stop_reason(response.stop_reason),
    )
    assert (
        span.attributes[ServerAttributes.SERVER_ADDRESS] == "api.anthropic.com"
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_with_raw_response(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Async ``with_raw_response.create`` must not crash and record a span.

    Regression test mirroring the sync case: the raw-response object the SDK
    returns from ``with_raw_response`` has no ``model`` attribute, so extraction
    raised ``AttributeError`` into the caller after the API call succeeded.
    """
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    raw_response = (
        await async_anthropic_client.messages.with_raw_response.create(
            model=model,
            max_tokens=100,
            messages=messages,
        )
    )

    assert hasattr(raw_response, "headers")
    message = raw_response.parse()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.name == f"chat {model}"
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_ID] == message.id
    assert (
        span.attributes[GenAIAttributes.GEN_AI_RESPONSE_MODEL] == message.model
    )
    assert span.attributes[
        GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS
    ] == expected_input_tokens(message.usage)
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS]
        == message.usage.output_tokens
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_captures_content(
    span_exporter, async_anthropic_client, instrument_with_content
):
    """Test content capture on async non-streaming create."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]

    input_messages = _load_span_messages(
        span, GenAIAttributes.GEN_AI_INPUT_MESSAGES
    )
    output_messages = _load_span_messages(
        span, GenAIAttributes.GEN_AI_OUTPUT_MESSAGES
    )

    assert input_messages[0]["role"] == "user"
    assert input_messages[0]["parts"][0]["type"] == "text"
    assert output_messages[0]["role"] == "assistant"
    assert output_messages[0]["parts"][0]["type"] == "text"


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_with_all_params(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test async message creation with all optional parameters."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello."}]

    await async_anthropic_client.messages.create(
        model=model,
        max_tokens=50,
        messages=messages,
        temperature=0.7,
        top_p=0.9,
        top_k=40,
        stop_sequences=["STOP"],
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MAX_TOKENS] == 50
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_TEMPERATURE] == 0.7
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_TOP_P] == 0.9
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_TOP_K] == 40
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_STOP_SEQUENCES] == (
        "STOP",
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_token_usage(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test that async token usage is captured correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Count to 5."}]

    response = await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS in span.attributes
    assert GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS in span.attributes
    assert span.attributes[
        GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS
    ] == expected_input_tokens(response.usage)
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS]
        == response.usage.output_tokens
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_stop_reason(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test that async stop reason is captured as finish_reasons array."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hi."}]

    response = await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS] == (
        normalize_stop_reason(response.stop_reason),
    )


@pytest.mark.asyncio
async def test_async_messages_create_connection_error(
    span_exporter, instrument_no_content
):
    """Test that async connection errors are handled correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Hello"}]

    client = AsyncAnthropic(base_url="http://localhost:9999")

    try:
        with pytest.raises(APIConnectionError):
            await client.messages.create(
                model=model,
                max_tokens=100,
                messages=messages,
                timeout=0.1,
            )
    finally:
        await client.close()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert ErrorAttributes.ERROR_TYPE in span.attributes
    assert "APIConnectionError" in span.attributes[ErrorAttributes.ERROR_TYPE]


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_streaming(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test async create(stream=True) returns a wrapped stream and records a span."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    response_id = None
    response_model = None
    stop_reason = None
    input_tokens = None
    output_tokens = None

    stream = await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    )
    assert isinstance(stream, AsyncMessagesStreamWrapper)

    async with stream:
        async for chunk in stream:
            if chunk.type == "message_start":
                response_id = chunk.message.id
                response_model = chunk.message.model
                input_tokens = chunk.message.usage.input_tokens
            elif chunk.type == "message_delta":
                stop_reason = chunk.delta.stop_reason
                output_tokens = chunk.usage.output_tokens

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_ID] == response_id
    assert (
        span.attributes[GenAIAttributes.GEN_AI_RESPONSE_MODEL]
        == response_model
    )
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS]
        == input_tokens
    )
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS]
        == output_tokens
    )
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS] == (
        normalize_stop_reason(stop_reason),
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_streaming_captures_content(
    span_exporter, async_anthropic_client, instrument_with_content
):
    """Test content capture on async create(stream=True)."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    stream = await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    )
    async with stream:
        async for _ in stream:
            pass

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]

    input_messages = _load_span_messages(
        span, GenAIAttributes.GEN_AI_INPUT_MESSAGES
    )
    output_messages = _load_span_messages(
        span, GenAIAttributes.GEN_AI_OUTPUT_MESSAGES
    )
    assert input_messages[0]["role"] == "user"
    assert output_messages[0]["role"] == "assistant"
    assert output_messages[0]["parts"]


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_streaming_iteration(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test async streaming with direct iteration."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hi."}]

    stream = await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    )

    chunks = []
    async with stream:
        async for chunk in stream:
            chunks.append(chunk)
    assert len(chunks) > 0

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert GenAIAttributes.GEN_AI_RESPONSE_ID in span.attributes
    assert GenAIAttributes.GEN_AI_RESPONSE_MODEL in span.attributes


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_streaming_delegates_response_attribute(
    async_anthropic_client, instrument_no_content
):
    """Async stream wrapper should expose attributes from the wrapped stream."""
    stream = await async_anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hi."}],
        stream=True,
    )

    assert stream.response is not None
    assert stream.response.status_code == 200
    assert stream.response.headers.get("request-id") is not None
    await stream.close()


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_stream(  # pylint: disable=too-many-locals
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test AsyncMessages.stream produces correct span."""
    model = "claude-haiku-4-5"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    response_id = None
    response_model = None
    stop_reason = None
    input_tokens = None
    output_tokens = None

    async with async_anthropic_client.messages.stream(
        model=model,
        max_tokens=100,
        messages=messages,
    ) as stream:
        async for chunk in stream:
            if chunk.type == "message_start":
                response_id = chunk.message.id
                response_model = chunk.message.model
                input_tokens = chunk.message.usage.input_tokens
            elif chunk.type == "message_delta":
                stop_reason = chunk.delta.stop_reason
                output_tokens = chunk.usage.output_tokens

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_ID] == response_id
    assert (
        span.attributes[GenAIAttributes.GEN_AI_RESPONSE_MODEL]
        == response_model
    )
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS]
        == input_tokens
    )
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS]
        == output_tokens
    )
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS] == (
        normalize_stop_reason(stop_reason),
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_stream_captures_content(
    span_exporter, async_anthropic_client, instrument_with_content
):
    """Test content capture on AsyncMessages.stream."""
    model = "claude-haiku-4-5"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    async with async_anthropic_client.messages.stream(
        model=model,
        max_tokens=100,
        messages=messages,
    ) as stream:
        async for _ in stream:
            pass

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]

    input_messages = _load_span_messages(
        span, GenAIAttributes.GEN_AI_INPUT_MESSAGES
    )
    output_messages = _load_span_messages(
        span, GenAIAttributes.GEN_AI_OUTPUT_MESSAGES
    )
    assert input_messages[0]["role"] == "user"
    assert input_messages[0]["parts"][0]["type"] == "text"
    assert output_messages[0]["role"] == "assistant"
    assert output_messages[0]["parts"]


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_stream_delegates_response_attribute(
    async_anthropic_client, instrument_no_content
):
    """AsyncMessages.stream wrapper should expose wrapped response attributes."""
    async with async_anthropic_client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hi."}],
    ) as stream:
        assert stream.response is not None
        assert stream.response.status_code == 200
        assert stream.response.headers.get("request-id") is not None


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_stream_api_error(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test that API errors from AsyncMessages.stream are propagated."""
    model = "invalid-model-name"
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(NotFoundError):
        async with async_anthropic_client.messages.stream(
            model=model,
            max_tokens=100,
            messages=messages,
        ) as stream:
            async for _ in stream:
                pass

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert ErrorAttributes.ERROR_TYPE in span.attributes
    assert "NotFoundError" in span.attributes[ErrorAttributes.ERROR_TYPE]


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_stream_interrupted_mid_iteration(
    span_exporter,
    async_anthropic_client,
    instrument_no_content,
    monkeypatch,
):
    """Mid-stream errors from AsyncMessages.stream propagate and record error."""
    model = "claude-haiku-4-5"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    with pytest.raises(
        ConnectionError, match="connection reset during stream"
    ):
        async with async_anthropic_client.messages.stream(
            model=model,
            max_tokens=100,
            messages=messages,
        ) as stream:
            monkeypatch.setattr(
                stream,
                "stream",
                _AsyncErrorInjectingStreamDelegate(stream.stream),
            )
            async for _ in stream:
                pass

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[ErrorAttributes.ERROR_TYPE] == "ConnectionError"


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_stream_closed_early_by_caller(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Caller-closing AsyncMessages.stream early finalizes without error."""
    model = "claude-haiku-4-5"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    async with async_anthropic_client.messages.stream(
        model=model,
        max_tokens=100,
        messages=messages,
    ) as stream:
        await anext(stream)
        await stream.close()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert ErrorAttributes.ERROR_TYPE not in span.attributes


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_stream_user_exception(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test that user raised exceptions from AsyncMessages.stream propagate."""
    model = "claude-haiku-4-5"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    with pytest.raises(ValueError, match="User raised exception"):
        async with async_anthropic_client.messages.stream(
            model=model,
            max_tokens=100,
            messages=messages,
        ) as stream:
            async for _ in stream:
                raise ValueError("User raised exception")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[ErrorAttributes.ERROR_TYPE] == "ValueError"


@pytest.mark.asyncio
async def test_async_messages_create_streaming_connection_error(
    span_exporter, instrument_no_content
):
    """Test that async connection errors during streaming are handled correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Hello"}]

    client = AsyncAnthropic(base_url="http://localhost:9999")

    try:
        with pytest.raises(APIConnectionError):
            await client.messages.create(
                model=model,
                max_tokens=100,
                messages=messages,
                stream=True,
                timeout=0.1,
            )
    finally:
        await client.close()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert ErrorAttributes.ERROR_TYPE in span.attributes
    assert "APIConnectionError" in span.attributes[ErrorAttributes.ERROR_TYPE]


@pytest.mark.asyncio
@pytest.mark.vcr()
@pytest.mark.skipif(
    not _has_tools_param,
    reason="anthropic SDK too old to support 'tools' parameter",
)
async def test_async_messages_create_captures_tool_use_content(
    span_exporter, async_anthropic_client, instrument_with_content
):
    """Test that async tool_use blocks are captured as tool_call parts."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "What is the weather in SF?"}]

    await async_anthropic_client.messages.create(
        model=model,
        max_tokens=256,
        messages=messages,
        tools=[
            {
                "name": "get_weather",
                "description": "Get weather by city",
                "input_schema": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            }
        ],
        tool_choice={"type": "tool", "name": "get_weather"},
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    output_messages = _load_span_messages(
        span, GenAIAttributes.GEN_AI_OUTPUT_MESSAGES
    )

    assert any(
        part.get("type") == "tool_call"
        for message in output_messages
        for part in message.get("parts", [])
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
@pytest.mark.skipif(
    not _has_thinking_param,
    reason="anthropic SDK too old to support 'thinking' parameter",
)
async def test_async_messages_create_captures_thinking_content(
    span_exporter, async_anthropic_client, instrument_with_content
):
    """Test that async thinking blocks are captured as reasoning parts."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "What is 17*19? Think first."}]

    await async_anthropic_client.messages.create(
        model=model,
        max_tokens=16000,
        messages=messages,
        thinking={"type": "enabled", "budget_tokens": 10000},
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    output_messages = _load_span_messages(
        span, GenAIAttributes.GEN_AI_OUTPUT_MESSAGES
    )

    assert any(
        part.get("type") == "reasoning"
        for message in output_messages
        for part in message.get("parts", [])
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_stream_wrapper_finalize_idempotent(
    span_exporter,
    async_anthropic_client,
    instrument_no_content,
):
    """Fully consumed async stream plus explicit close should still yield one span."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    stream = await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    )

    response_id = None
    response_model = None
    stop_reason = None
    input_tokens = None
    output_tokens = None

    async for chunk in stream:
        if chunk.type == "message_start":
            response_id = chunk.message.id
            response_model = chunk.message.model
            input_tokens = expected_input_tokens(chunk.message.usage)
        elif chunk.type == "message_delta":
            stop_reason = chunk.delta.stop_reason
            output_tokens = chunk.usage.output_tokens
            input_tokens = expected_input_tokens(chunk.usage)

    await stream.close()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_ID] == response_id
    assert (
        span.attributes[GenAIAttributes.GEN_AI_RESPONSE_MODEL]
        == response_model
    )
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS]
        == input_tokens
    )
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS]
        == output_tokens
    )
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS] == (
        normalize_stop_reason(stop_reason),
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_aggregates_cache_tokens(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Async non-streaming response with cache tokens aggregates correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    response = await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]

    assert GEN_AI_USAGE_CACHE_CREATION_INPUT_TOKENS in span.attributes
    assert GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS in span.attributes
    assert span.attributes[
        GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS
    ] == expected_input_tokens(response.usage)
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS]
        == response.usage.output_tokens
    )
    cache_creation = getattr(response.usage, "cache_creation_input_tokens", 0)
    cache_read = getattr(response.usage, "cache_read_input_tokens", 0)
    assert (
        span.attributes[GEN_AI_USAGE_CACHE_CREATION_INPUT_TOKENS]
        == cache_creation
    )
    assert span.attributes[GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS] == cache_read


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_streaming_aggregates_cache_tokens(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Async streaming response with cache tokens aggregates correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    input_tokens = None
    output_tokens = None
    cache_creation = None
    cache_read = None

    stream = await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    )
    async with stream:
        async for chunk in stream:
            if chunk.type == "message_delta":
                input_tokens = expected_input_tokens(chunk.usage)
                output_tokens = chunk.usage.output_tokens
                cache_creation = getattr(
                    chunk.usage, "cache_creation_input_tokens", None
                )
                cache_read = getattr(
                    chunk.usage, "cache_read_input_tokens", None
                )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]

    assert GEN_AI_USAGE_CACHE_CREATION_INPUT_TOKENS in span.attributes
    assert GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS in span.attributes
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS]
        == input_tokens
    )
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS]
        == output_tokens
    )
    assert (
        span.attributes[GEN_AI_USAGE_CACHE_CREATION_INPUT_TOKENS]
        == cache_creation
    )
    assert span.attributes[GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS] == cache_read


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_stream_propagation_error(
    span_exporter, async_anthropic_client, instrument_no_content, monkeypatch
):
    """Mid-stream async errors must propagate and record error on span."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    stream = await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    )

    class ErrorInjectingStreamDelegate:
        def __init__(self, inner):
            self._inner = inner
            self._count = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self._count == 1:
                raise ConnectionError("connection reset during stream")
            self._count += 1
            return await self._inner.__anext__()

        async def close(self):
            return await self._inner.close()

        def __getattr__(self, name):
            return getattr(self._inner, name)

    monkeypatch.setattr(
        stream, "stream", ErrorInjectingStreamDelegate(stream.stream)
    )

    with pytest.raises(
        ConnectionError, match="connection reset during stream"
    ):
        async with stream:
            async for _ in stream:
                pass

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[ErrorAttributes.ERROR_TYPE] == "ConnectionError"


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_streaming_user_exception(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test that user raised exceptions are propagated from async streams."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    with pytest.raises(ValueError, match="User raised exception"):
        stream = await async_anthropic_client.messages.create(
            model=model,
            max_tokens=100,
            messages=messages,
            stream=True,
        )
        async with stream:
            async for _ in stream:
                raise ValueError("User raised exception")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[ErrorAttributes.ERROR_TYPE] == "ValueError"


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_api_error(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Test async API errors are recorded and re-raised unchanged."""
    model = "invalid-model-name"
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(NotFoundError):
        await async_anthropic_client.messages.create(
            model=model,
            max_tokens=100,
            messages=messages,
        )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert ErrorAttributes.ERROR_TYPE in span.attributes
    assert "NotFoundError" in span.attributes[ErrorAttributes.ERROR_TYPE]


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_event_only_no_content_in_span(
    span_exporter,
    log_exporter,
    async_anthropic_client,
    instrument_event_only,
):
    """Test EVENT_ONLY mode emits async create content as a log event only."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    await async_anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]

    assert GenAIAttributes.GEN_AI_INPUT_MESSAGES not in span.attributes
    assert GenAIAttributes.GEN_AI_OUTPUT_MESSAGES not in span.attributes
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert GenAIAttributes.GEN_AI_RESPONSE_MODEL in span.attributes
    assert GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS in span.attributes
    assert GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS in span.attributes

    logs = log_exporter.get_finished_logs()
    assert len(logs) == 1
    log_record = logs[0].log_record
    assert log_record.event_name == "gen_ai.client.inference.operation.details"
    assert (
        log_record.attributes[GenAIAttributes.GEN_AI_PROVIDER_NAME]
        == "anthropic"
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_streaming_with_raw_response(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Async streaming ``with_raw_response.create`` defers parse() and records a full span.

    Regression test mirroring the sync case: the async raw response is not an
    ``AsyncStream``, so it fell past the stream check and the span was ended
    immediately with no response attributes. The proxy must defer finalization
    until the parsed async stream is drained and then populate the span.
    """
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    raw_response = (
        await async_anthropic_client.messages.with_raw_response.create(
            model=model,
            max_tokens=100,
            messages=messages,
            stream=True,
        )
    )

    # Raw-response metadata still resolves natively off the proxy.
    assert hasattr(raw_response, "headers")
    assert raw_response.headers is not None

    # Deferred: the span must not be finalized before the caller parses/drains.
    assert span_exporter.get_finished_spans() == ()

    stream = raw_response.parse()
    response_text = ""
    async for chunk in stream:
        if chunk.type == "content_block_delta":
            delta = getattr(chunk, "delta", None)
            if delta and hasattr(delta, "text"):
                response_text += delta.text
    assert response_text == "Hello!"

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    # The span is no longer a premature empty one: it carries response
    # attributes accumulated from the drained stream.
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_MODEL] == model
    assert span.attributes[GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS] == 13
    assert span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS] == 5
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS] == (
        "stop",
    )


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_create_streaming_with_raw_response_never_parsed(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """A never-parsed async streaming raw response is finalized once when closed.

    When the caller reads only metadata and never calls ``parse()``, the span
    must still be finalized exactly once when the underlying body is closed,
    since ``stop()`` is not idempotent.
    """
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    raw_response = (
        await async_anthropic_client.messages.with_raw_response.create(
            model=model,
            max_tokens=100,
            messages=messages,
            stream=True,
        )
    )

    # Deferred: nothing finalized while the caller has not parsed or closed.
    assert span_exporter.get_finished_spans() == ()

    # Caller drains/closes the body without ever parsing it.
    await raw_response.http_response.aclose()

    assert len(span_exporter.get_finished_spans()) == 1

    # A second close must not finalize the span again.
    await raw_response.http_response.aclose()
    assert len(span_exporter.get_finished_spans()) == 1


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_with_streaming_response_nonstreaming(
    span_exporter, metric_reader, async_anthropic_client, instrument_no_content
):
    """Non-streaming async ``with_streaming_response.create`` records response attrs.

    Regression test for the async half of the routing bug: the SDK sets
    ``x-stainless-raw-response: stream`` on every ``with_streaming_response``
    call, and ``AsyncAPIResponse.parse()`` is a coroutine, so this non-streaming
    call was handed back uninstrumented and got a request-only span. Routing on
    the awaited ``parse()`` result extracts the message and records the response
    model, usage, and finish reason.
    """
    from opentelemetry.semconv._incubating.metrics import gen_ai_metrics

    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    async with async_anthropic_client.messages.with_streaming_response.create(
        model=model,
        max_tokens=100,
        messages=messages,
    ) as raw_response:
        assert hasattr(raw_response, "headers")
        # AsyncAPIResponse.parse() is a coroutine; the proxy hands back one too.
        message = await raw_response.parse()

    from anthropic.types import Message

    assert isinstance(message, Message)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert GenAIAttributes.GEN_AI_RESPONSE_MODEL in span.attributes
    assert GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS in span.attributes
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_ID] == message.id
    assert (
        span.attributes[GenAIAttributes.GEN_AI_RESPONSE_MODEL] == message.model
    )
    assert span.attributes[
        GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS
    ] == expected_input_tokens(message.usage)
    assert (
        span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS]
        == message.usage.output_tokens
    )
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS] == (
        normalize_stop_reason(message.stop_reason),
    )

    metrics = {
        metric.name: metric
        for rm in metric_reader.get_metrics_data().resource_metrics
        for scope in rm.scope_metrics
        for metric in scope.metrics
    }
    assert gen_ai_metrics.GEN_AI_CLIENT_TOKEN_USAGE in metrics


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_async_messages_with_streaming_response_streaming(
    span_exporter, async_anthropic_client, instrument_no_content
):
    """Streaming async ``with_streaming_response.create`` defers and records a full span.

    The awaited ``parse()`` yields an ``AsyncStream``; draining it finalizes the
    span with the response model, token usage, and finish reason.
    """
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    async with async_anthropic_client.messages.with_streaming_response.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    ) as raw_response:
        assert hasattr(raw_response, "headers")
        # Deferred: the span is not finalized before the stream is drained.
        assert span_exporter.get_finished_spans() == ()

        stream = await raw_response.parse()
        response_text = ""
        async for chunk in stream:
            if chunk.type == "content_block_delta":
                delta = getattr(chunk, "delta", None)
                if delta and hasattr(delta, "text"):
                    response_text += delta.text
    assert response_text == "Hello!"

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_MODEL] == model
    assert span.attributes[GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS] == 13
    assert span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS] == 5
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS] == (
        "stop",
    )
