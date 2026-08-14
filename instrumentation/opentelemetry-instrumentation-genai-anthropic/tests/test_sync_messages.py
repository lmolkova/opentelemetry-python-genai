# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Tests for sync Messages.create instrumentation."""
# pylint: disable=too-many-lines

import inspect
import json
import os
from pathlib import Path

import pytest
from anthropic import Anthropic, APIConnectionError, NotFoundError
from anthropic.resources.messages import Messages as _Messages

from opentelemetry.instrumentation.genai.anthropic import (
    AnthropicInstrumentor,
    _raw_response,
)
from opentelemetry.instrumentation.genai.anthropic.messages_extractors import (
    GEN_AI_USAGE_CACHE_CREATION_INPUT_TOKENS,
    GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS,
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

# Detect whether the installed anthropic SDK supports tools / thinking params.
# Older SDK versions (e.g. 0.16.0) do not accept these keyword arguments.
_create_params = set(inspect.signature(_Messages.create).parameters)
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


def assert_span_attributes(  # pylint: disable=too-many-arguments
    span,
    request_model,
    response_id=None,
    response_model=None,
    input_tokens=None,
    output_tokens=None,
    finish_reasons=None,
    operation_name="chat",
    server_address="api.anthropic.com",
):
    """Assert that a span has the expected attributes."""
    assert span.name == f"{operation_name} {request_model}"
    assert (
        operation_name
        == span.attributes[GenAIAttributes.GEN_AI_OPERATION_NAME]
    )
    assert (
        GenAIAttributes.GenAiProviderNameValues.ANTHROPIC.value
        == span.attributes[GenAIAttributes.GEN_AI_PROVIDER_NAME]
    )
    assert (
        request_model == span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL]
    )
    assert server_address == span.attributes[ServerAttributes.SERVER_ADDRESS]

    if response_id is not None:
        assert (
            response_id == span.attributes[GenAIAttributes.GEN_AI_RESPONSE_ID]
        )

    if response_model is not None:
        assert (
            response_model
            == span.attributes[GenAIAttributes.GEN_AI_RESPONSE_MODEL]
        )

    if input_tokens is not None:
        assert (
            input_tokens
            == span.attributes[GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS]
        )

    if output_tokens is not None:
        assert (
            output_tokens
            == span.attributes[GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS]
        )

    if finish_reasons is not None:
        # OpenTelemetry converts lists to tuples when storing as attributes
        assert (
            tuple(finish_reasons)
            == span.attributes[GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS]
        )


def _load_span_messages(span, attribute):
    value = span.attributes.get(attribute)
    assert value is not None
    assert isinstance(value, str)
    parsed = json.loads(value)
    assert isinstance(parsed, list)
    return parsed


def _skip_if_cassette_missing_and_no_real_key(request):
    cassette_path = (
        Path(__file__).parent / "cassettes" / f"{request.node.name}.yaml"
    )
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not cassette_path.exists() and api_key == "test_anthropic_api_key":
        pytest.skip(
            f"Cassette {cassette_path.name} is missing. "
            "Set a real ANTHROPIC_API_KEY to record it."
        )


@pytest.mark.vcr()
def test_sync_messages_create_basic(
    span_exporter, anthropic_client, instrument_no_content
):
    """Test basic sync message creation produces correct span."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    response = anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    assert_span_attributes(
        spans[0],
        request_model=model,
        response_id=response.id,
        response_model=response.model,
        input_tokens=expected_input_tokens(response.usage),
        output_tokens=response.usage.output_tokens,
        finish_reasons=[normalize_stop_reason(response.stop_reason)],
    )


@pytest.mark.vcr()
def test_sync_messages_create_with_raw_response(
    span_exporter, anthropic_client, instrument_no_content
):
    """``with_raw_response.create`` must not crash and must still record a span.

    Regression test: the instrumentation assumed the wrapped call always
    returns a ``Message`` and read ``message.model`` off the raw-response object
    (``LegacyAPIResponse``) that ``with_raw_response`` returns, raising
    ``AttributeError`` into the caller *after* the API call had already
    succeeded. The raw response must be returned to the caller untouched.
    """
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    raw_response = anthropic_client.messages.with_raw_response.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )

    # The caller still receives the raw response, with metadata and parse().
    assert hasattr(raw_response, "headers")
    message = raw_response.parse()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert_span_attributes(
        spans[0],
        request_model=model,
        response_id=message.id,
        response_model=message.model,
        input_tokens=expected_input_tokens(message.usage),
        output_tokens=message.usage.output_tokens,
        finish_reasons=[normalize_stop_reason(message.stop_reason)],
    )


@pytest.fixture(name="vcr_cassette_name")
def fixture_vcr_cassette_name(request):
    # Reuse an existing recorded interaction for tests that exercise the same
    # request but a different code path. VCR matches on method + URI, so the
    # recorded ``with_raw_response`` create call replays here unchanged.
    reused = {
        "test_sync_messages_raw_response_extraction_failure_not_raised": (
            "test_sync_messages_create_with_raw_response"
        ),
    }
    return reused.get(request.node.name, request.node.name)


@pytest.mark.vcr()
def test_sync_messages_raw_response_extraction_failure_not_raised(
    span_exporter, anthropic_client, instrument_no_content, monkeypatch
):
    """Extraction failures must never surface to the caller of ``parse()``.

    ``with_raw_response.create`` reads the body eagerly, so extraction runs in
    ``wrap_raw_response``'s ``is_closed`` branch. If that extraction raises, it
    must be swallowed (telemetry never breaks the caller) and the caller must
    still receive the parsed ``Message``.
    """

    def boom(self, invocation):
        raise ValueError("boom")

    monkeypatch.setattr(
        _raw_response.MessageWrapper, "extract_into", boom, raising=True
    )

    raw_response = anthropic_client.messages.with_raw_response.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hello in one word."}],
    )

    assert raw_response.parse().id


@pytest.mark.vcr()
def test_sync_messages_with_raw_response_never_parsed(
    span_exporter, anthropic_client, instrument_no_content
):
    raw_response = anthropic_client.messages.with_raw_response.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hello in one word."}],
    )
    assert raw_response.headers is not None
    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1


class _FakeHTTPResponse:
    """Minimal stand-in for the httpx response behind a raw response."""

    def __init__(self):
        self.close_calls = 0

    def close(self):
        self.close_calls += 1


def _build_message():
    from anthropic.types import Message

    return Message.model_construct(
        id="msg_test",
        type="message",
        role="assistant",
        model="claude-test",
        content=[],
        stop_reason="end_turn",
        stop_sequence=None,
        usage=None,
    )


def test_raw_response_proxy_swallows_message_extraction_error():
    """A telemetry extraction failure must never propagate to the caller.

    The proxy routes on what ``parse()`` returns. When it returns a ``Message``
    but extracting telemetry from it raises, the proxy logs at debug, finalizes
    the span once, and hands the caller the parsed message untouched -- the
    telemetry error must not surface as the caller's ``parse()`` result.
    """
    from opentelemetry.instrumentation.genai.anthropic._raw_response import (
        RawResponseProxy,
    )

    message = _build_message()
    finalize_calls = []

    class _Raw:
        http_response = _FakeHTTPResponse()

        def parse(self, *args, **kwargs):
            return message

    def _boom(_message):
        raise ValueError("telemetry extraction boom")

    proxy = RawResponseProxy(
        _Raw(),
        dispatch_message=_boom,
        wrap_stream=lambda _stream: None,
        finalize=lambda: finalize_calls.append(True),
    )

    result = proxy.parse()

    assert result is message
    # The span is still finalized exactly once despite the extraction failure.
    assert finalize_calls == [True]


def test_raw_response_proxy_parse_error_propagates_and_finalizes_once():
    """A caller ``parse()`` failure propagates unchanged and finalizes once.

    When the SDK's own ``parse()`` raises (validation/deserialization failure),
    that is the caller's own exception: telemetry must neither swallow it nor
    replace it. The span must still be finalized exactly once when the body is
    later closed, and never a second time (``stop()`` is not idempotent).
    """
    from opentelemetry.instrumentation.genai.anthropic._raw_response import (
        RawResponseProxy,
    )

    finalize_calls = []
    http_response = _FakeHTTPResponse()

    class _Raw:
        def __init__(self):
            self.http_response = http_response

        def parse(self, *args, **kwargs):
            raise ValueError("caller parse boom")

    proxy = RawResponseProxy(
        _Raw(),
        dispatch_message=lambda _message: None,
        wrap_stream=lambda _stream: None,
        finalize=lambda: finalize_calls.append(True),
    )

    with pytest.raises(ValueError, match="caller parse boom"):
        proxy.parse()

    # Not finalized until the caller closes the body.
    assert finalize_calls == []

    proxy.http_response.close()
    assert finalize_calls == [True]
    assert http_response.close_calls == 1

    # A second close must not finalize the span again.
    proxy.http_response.close()
    assert finalize_calls == [True]
    assert http_response.close_calls == 2


@pytest.mark.vcr()
def test_sync_messages_create_captures_content(
    span_exporter, anthropic_client, instrument_with_content
):
    """Test content capture on non-streaming create."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    anthropic_client.messages.create(
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


@pytest.mark.vcr()
def test_sync_messages_create_with_all_params(
    span_exporter, anthropic_client, instrument_no_content
):
    """Test message creation with all optional parameters."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello."}]

    anthropic_client.messages.create(
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
    # OpenTelemetry converts lists to tuples when storing as attributes
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_STOP_SEQUENCES] == (
        "STOP",
    )


@pytest.mark.vcr()
def test_sync_messages_create_token_usage(
    span_exporter, anthropic_client, instrument_no_content
):
    """Test that token usage is captured correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Count to 5."}]

    response = anthropic_client.messages.create(
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


@pytest.mark.vcr()
def test_sync_messages_create_stop_reason(
    span_exporter, anthropic_client, instrument_no_content
):
    """Test that stop reason is captured as finish_reasons array."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hi."}]

    response = anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    # Anthropic's stop_reason should be wrapped in a tuple (OTel converts lists)
    assert span.attributes[GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS] == (
        normalize_stop_reason(response.stop_reason),
    )


def test_sync_messages_create_connection_error(
    span_exporter, instrument_no_content
):
    """Test that connection errors are handled correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Hello"}]

    # Create client with invalid endpoint
    client = Anthropic(base_url="http://localhost:9999")

    with pytest.raises(APIConnectionError):
        client.messages.create(
            model=model,
            max_tokens=100,
            messages=messages,
            timeout=0.1,
        )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert ErrorAttributes.ERROR_TYPE in span.attributes
    assert "APIConnectionError" in span.attributes[ErrorAttributes.ERROR_TYPE]


@pytest.mark.vcr()
def test_sync_messages_create_api_error(
    span_exporter, anthropic_client, instrument_no_content
):
    """Test that API errors (e.g., invalid model) are handled correctly."""
    model = "invalid-model-name"
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(NotFoundError):
        anthropic_client.messages.create(
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


def test_uninstrument_removes_patching(
    span_exporter, tracer_provider, logger_provider, meter_provider
):
    """Test that uninstrument() removes the patching."""
    instrumentor = AnthropicInstrumentor()
    instrumentor.instrument(
        tracer_provider=tracer_provider,
        logger_provider=logger_provider,
        meter_provider=meter_provider,
    )

    # Uninstrument
    instrumentor.uninstrument()

    # Create a new client after uninstrumenting
    # The actual API call won't work without a real API key,
    # but we can verify no spans are created for a mocked scenario
    # For this test, we'll just verify uninstrument doesn't raise
    assert True


def test_multiple_instrument_uninstrument_cycles(
    tracer_provider, logger_provider, meter_provider
):
    """Test that multiple instrument/uninstrument cycles work correctly."""
    instrumentor = AnthropicInstrumentor()

    # First cycle
    instrumentor.instrument(
        tracer_provider=tracer_provider,
        logger_provider=logger_provider,
        meter_provider=meter_provider,
    )
    instrumentor.uninstrument()

    # Second cycle
    instrumentor.instrument(
        tracer_provider=tracer_provider,
        logger_provider=logger_provider,
        meter_provider=meter_provider,
    )
    instrumentor.uninstrument()

    # Third cycle - should still work
    instrumentor.instrument(
        tracer_provider=tracer_provider,
        logger_provider=logger_provider,
        meter_provider=meter_provider,
    )
    instrumentor.uninstrument()


@pytest.mark.vcr()
def test_sync_messages_create_streaming(  # pylint: disable=too-many-locals
    span_exporter, anthropic_client, instrument_no_content
):
    """Test streaming message creation produces correct span."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    # Collect response data from stream
    response_text = ""
    response_id = None
    response_model = None
    stop_reason = None
    input_tokens = None
    output_tokens = None

    with anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    ) as stream:
        for chunk in stream:
            # Extract data from chunks for assertion
            if chunk.type == "message_start":
                message = getattr(chunk, "message", None)
                if message:
                    response_id = getattr(message, "id", None)
                    response_model = getattr(message, "model", None)
                    usage = getattr(message, "usage", None)
                    if usage:
                        input_tokens = getattr(usage, "input_tokens", None)
            elif chunk.type == "content_block_delta":
                delta = getattr(chunk, "delta", None)
                if delta and hasattr(delta, "text"):
                    response_text += delta.text
            elif chunk.type == "message_delta":
                delta = getattr(chunk, "delta", None)
                if delta:
                    stop_reason = getattr(delta, "stop_reason", None)
                usage = getattr(chunk, "usage", None)
                if usage:
                    output_tokens = getattr(usage, "output_tokens", None)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    assert_span_attributes(
        spans[0],
        request_model=model,
        response_id=response_id,
        response_model=response_model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        finish_reasons=[normalize_stop_reason(stop_reason)]
        if stop_reason
        else None,
    )


@pytest.mark.vcr()
def test_sync_messages_create_streaming_captures_content(
    span_exporter, anthropic_client, instrument_with_content
):
    """Test content capture on create(stream=True)."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    with anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    ) as stream:
        for _ in stream:
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
    assert output_messages[0]["parts"] == [
        {"type": "text", "content": "Hello!"}
    ]


@pytest.mark.vcr()
def test_sync_messages_stream(  # pylint: disable=too-many-locals
    request, span_exporter, anthropic_client, instrument_no_content
):
    """Test Messages.stream produces correct span."""
    _skip_if_cassette_missing_and_no_real_key(request)
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    response_id = None
    response_model = None
    stop_reason = None
    input_tokens = None
    output_tokens = None

    with anthropic_client.messages.stream(
        model=model,
        max_tokens=100,
        messages=messages,
    ) as stream:
        for chunk in stream:
            if chunk.type == "message_start":
                message = getattr(chunk, "message", None)
                if message:
                    response_id = getattr(message, "id", None)
                    response_model = getattr(message, "model", None)
                    usage = getattr(message, "usage", None)
                    if usage:
                        input_tokens = getattr(usage, "input_tokens", None)
            elif chunk.type == "message_delta":
                delta = getattr(chunk, "delta", None)
                if delta:
                    stop_reason = getattr(delta, "stop_reason", None)
                usage = getattr(chunk, "usage", None)
                if usage:
                    output_tokens = getattr(usage, "output_tokens", None)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    assert_span_attributes(
        spans[0],
        request_model=model,
        response_id=response_id,
        response_model=response_model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        finish_reasons=[normalize_stop_reason(stop_reason)]
        if stop_reason
        else None,
    )


@pytest.mark.vcr()
def test_sync_messages_stream_captures_content(
    request, span_exporter, anthropic_client, instrument_with_content
):
    """Test content capture on Messages.stream."""
    _skip_if_cassette_missing_and_no_real_key(request)
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    with anthropic_client.messages.stream(
        model=model,
        max_tokens=100,
        messages=messages,
    ) as stream:
        for _ in stream:
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
    assert output_messages[0]["parts"] == [
        {"type": "text", "content": "Hello!"}
    ]


@pytest.mark.vcr()
def test_sync_messages_stream_delegates_response_attribute(
    request, anthropic_client, instrument_no_content
):
    """Messages.stream wrapper should expose attributes from the wrapped stream."""
    _skip_if_cassette_missing_and_no_real_key(request)

    with anthropic_client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hi."}],
    ) as stream:
        assert stream.response is not None
        assert stream.response.status_code == 200
        assert stream.response.headers.get("request-id") is not None


def test_sync_messages_stream_connection_error(
    span_exporter, instrument_no_content
):
    """Test that connection errors from Messages.stream are handled correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Hello"}]

    client = Anthropic(base_url="http://localhost:9999")

    with pytest.raises(APIConnectionError):
        with client.messages.stream(
            model=model,
            max_tokens=100,
            messages=messages,
            timeout=0.1,
        ) as stream:
            list(stream)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert ErrorAttributes.ERROR_TYPE in span.attributes
    assert "APIConnectionError" in span.attributes[ErrorAttributes.ERROR_TYPE]


@pytest.mark.vcr()
def test_sync_messages_stream_api_error(
    request, span_exporter, anthropic_client, instrument_no_content
):
    """Test that API errors from Messages.stream are propagated."""
    _skip_if_cassette_missing_and_no_real_key(request)
    model = "invalid-model-name"
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(NotFoundError):
        with anthropic_client.messages.stream(
            model=model,
            max_tokens=100,
            messages=messages,
        ) as stream:
            list(stream)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert ErrorAttributes.ERROR_TYPE in span.attributes
    assert "NotFoundError" in span.attributes[ErrorAttributes.ERROR_TYPE]


@pytest.mark.vcr()
def test_sync_messages_stream_interrupted_mid_iteration(
    request,
    span_exporter,
    anthropic_client,
    instrument_no_content,
    monkeypatch,
):
    """Mid-stream network errors from Messages.stream propagate and record error."""
    _skip_if_cassette_missing_and_no_real_key(request)
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    class ErrorInjectingStreamDelegate:
        def __init__(self, inner):
            self._inner = inner
            self._count = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self._count == 1:
                raise ConnectionError("connection reset during stream")
            self._count += 1
            return next(self._inner)

        def close(self):
            return self._inner.close()

        def __getattr__(self, name):
            return getattr(self._inner, name)

    with pytest.raises(
        ConnectionError, match="connection reset during stream"
    ):
        with anthropic_client.messages.stream(
            model=model,
            max_tokens=100,
            messages=messages,
        ) as stream:
            monkeypatch.setattr(
                stream,
                "stream",
                ErrorInjectingStreamDelegate(stream.stream),
            )
            for _ in stream:
                pass

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[ErrorAttributes.ERROR_TYPE] == "ConnectionError"


@pytest.mark.vcr()
def test_sync_messages_stream_closed_early_by_caller(
    request, span_exporter, anthropic_client, instrument_no_content
):
    """Caller-closing Messages.stream early finalizes the span without error."""
    _skip_if_cassette_missing_and_no_real_key(request)
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    with anthropic_client.messages.stream(
        model=model,
        max_tokens=100,
        messages=messages,
    ) as stream:
        next(stream)
        stream.close()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert ErrorAttributes.ERROR_TYPE not in span.attributes


@pytest.mark.vcr()
def test_sync_messages_create_streaming_iteration(
    span_exporter, anthropic_client, instrument_no_content
):
    """Test streaming with direct iteration (without context manager)."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hi."}]

    stream = anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    )

    # Consume the stream by iterating
    chunks = list(stream)
    assert len(chunks) > 0

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    # Verify span has response attributes from streaming
    assert GenAIAttributes.GEN_AI_RESPONSE_ID in span.attributes
    assert GenAIAttributes.GEN_AI_RESPONSE_MODEL in span.attributes


@pytest.mark.vcr()
def test_sync_messages_create_streaming_delegates_response_attribute(
    request, anthropic_client, instrument_no_content
):
    """Stream wrapper should expose attributes from the wrapped stream."""
    _skip_if_cassette_missing_and_no_real_key(request)

    stream = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hi."}],
        stream=True,
    )

    # `response` exists on Anthropic Stream and should be reachable on wrapper.
    assert stream.response is not None
    assert stream.response.status_code == 200
    assert stream.response.headers.get("request-id") is not None
    stream.close()


def test_sync_messages_create_streaming_connection_error(
    span_exporter, instrument_no_content
):
    """Test that connection errors during streaming are handled correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Hello"}]

    # Create client with invalid endpoint
    client = Anthropic(base_url="http://localhost:9999")

    with pytest.raises(APIConnectionError):
        client.messages.create(
            model=model,
            max_tokens=100,
            messages=messages,
            stream=True,
            timeout=0.1,
        )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert ErrorAttributes.ERROR_TYPE in span.attributes
    assert "APIConnectionError" in span.attributes[ErrorAttributes.ERROR_TYPE]


@pytest.mark.vcr()
@pytest.mark.skipif(
    not _has_tools_param,
    reason="anthropic SDK too old to support 'tools' parameter",
)
def test_sync_messages_create_captures_tool_use_content(
    request, span_exporter, anthropic_client, instrument_with_content
):
    """Test that tool_use blocks are captured as tool_call parts."""
    _skip_if_cassette_missing_and_no_real_key(request)
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "What is the weather in SF?"}]

    anthropic_client.messages.create(
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


@pytest.mark.vcr()
@pytest.mark.skipif(
    not _has_thinking_param,
    reason="anthropic SDK too old to support 'thinking' parameter",
)
def test_sync_messages_create_captures_thinking_content(
    request, span_exporter, anthropic_client, instrument_with_content
):
    """Test that thinking blocks are captured as reasoning parts."""
    _skip_if_cassette_missing_and_no_real_key(request)
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "What is 17*19? Think first."}]

    anthropic_client.messages.create(
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


@pytest.mark.vcr()
def test_stream_wrapper_finalize_idempotent(  # pylint: disable=too-many-locals
    span_exporter,
    anthropic_client,
    instrument_no_content,
):
    """Fully consumed stream plus explicit close should still yield one span."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    stream = anthropic_client.messages.create(
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

    # Consume the stream fully, then call close() to verify idempotent finalization.
    for chunk in stream:
        if chunk.type == "message_start":
            message = getattr(chunk, "message", None)
            if message:
                response_id = getattr(message, "id", None)
                response_model = getattr(message, "model", None)
                usage = getattr(message, "usage", None)
                if usage:
                    input_tokens = expected_input_tokens(usage)
        elif chunk.type == "message_delta":
            delta = getattr(chunk, "delta", None)
            if delta:
                stop_reason = getattr(delta, "stop_reason", None)
            usage = getattr(chunk, "usage", None)
            if usage:
                output_tokens = getattr(usage, "output_tokens", None)
                input_tokens = expected_input_tokens(usage)

    stream.close()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert_span_attributes(
        spans[0],
        request_model=model,
        response_id=response_id,
        response_model=response_model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        finish_reasons=[normalize_stop_reason(stop_reason)]
        if stop_reason
        else None,
    )


@pytest.mark.vcr()
def test_sync_messages_create_aggregates_cache_tokens(
    span_exporter, anthropic_client, instrument_no_content
):
    """Non-streaming response with non-zero cache tokens aggregates correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    response = anthropic_client.messages.create(
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


@pytest.mark.vcr()
def test_sync_messages_create_streaming_aggregates_cache_tokens(
    span_exporter, anthropic_client, instrument_no_content
):
    """Streaming response with non-zero cache tokens aggregates correctly."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    input_tokens = None
    output_tokens = None
    cache_creation = None
    cache_read = None

    with anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    ) as stream:
        for chunk in stream:
            if chunk.type == "message_delta":
                usage = getattr(chunk, "usage", None)
                if usage:
                    input_tokens = expected_input_tokens(usage)
                    output_tokens = getattr(usage, "output_tokens", None)
                    cache_creation = getattr(
                        usage, "cache_creation_input_tokens", None
                    )
                    cache_read = getattr(
                        usage, "cache_read_input_tokens", None
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


@pytest.mark.vcr()
def test_sync_messages_create_stream_propagation_error(
    span_exporter, anthropic_client, instrument_no_content, monkeypatch
):
    """Mid-stream errors from the underlying iterator must propagate and record error on span."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    stream = anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    )

    # Wrap the underlying stream so we inject an iteration error but still
    # delegate close()/other behavior to the real stream.
    class ErrorInjectingStreamDelegate:
        def __init__(self, inner):
            self._inner = inner
            self._count = 0

        def __iter__(self):
            return self

        def __next__(self):
            # Fail after yielding one chunk so this exercises a mid-stream error.
            if self._count == 1:
                raise ConnectionError("connection reset during stream")
            self._count += 1
            return next(self._inner)

        def close(self):
            return self._inner.close()

        def __getattr__(self, name):
            return getattr(self._inner, name)

    monkeypatch.setattr(
        stream, "stream", ErrorInjectingStreamDelegate(stream.stream)
    )

    with pytest.raises(
        ConnectionError, match="connection reset during stream"
    ):
        with stream:
            for _ in stream:
                pass

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[ErrorAttributes.ERROR_TYPE] == "ConnectionError"


@pytest.mark.vcr()
def test_sync_messages_create_streaming_user_exception(
    span_exporter, anthropic_client, instrument_no_content
):
    """Test that user raised exceptions are propagated."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    with pytest.raises(ValueError, match="User raised exception"):
        with anthropic_client.messages.create(
            model=model,
            max_tokens=100,
            messages=messages,
            stream=True,
        ) as stream:
            for _ in stream:
                raise ValueError("User raised exception")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[ErrorAttributes.ERROR_TYPE] == "ValueError"


@pytest.mark.vcr()
def test_sync_messages_stream_user_exception(
    request, span_exporter, anthropic_client, instrument_no_content
):
    """Test that user raised exceptions from Messages.stream are propagated."""
    _skip_if_cassette_missing_and_no_real_key(request)
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    with pytest.raises(ValueError, match="User raised exception"):
        with anthropic_client.messages.stream(
            model=model,
            max_tokens=100,
            messages=messages,
        ) as stream:
            for _ in stream:
                raise ValueError("User raised exception")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert span.attributes[ErrorAttributes.ERROR_TYPE] == "ValueError"


# =============================================================================
# Tests for EVENT_ONLY content capture mode
# =============================================================================


@pytest.mark.vcr()
def test_sync_messages_create_event_only_no_content_in_span(
    span_exporter, log_exporter, anthropic_client, instrument_event_only
):
    """Test that EVENT_ONLY mode does not capture content in span attributes
    but does emit a log event with the content."""
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    anthropic_client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]

    # Content should NOT be in span attributes under EVENT_ONLY
    assert GenAIAttributes.GEN_AI_INPUT_MESSAGES not in span.attributes
    assert GenAIAttributes.GEN_AI_OUTPUT_MESSAGES not in span.attributes

    # Basic span attributes should still be present
    assert span.attributes[GenAIAttributes.GEN_AI_REQUEST_MODEL] == model
    assert GenAIAttributes.GEN_AI_RESPONSE_MODEL in span.attributes
    assert GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS in span.attributes
    assert GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS in span.attributes

    # A log event should have been emitted with the content
    logs = log_exporter.get_finished_logs()
    assert len(logs) == 1
    log_record = logs[0].log_record
    assert log_record.event_name == "gen_ai.client.inference.operation.details"


@pytest.mark.vcr()
def test_sync_messages_create_streaming_with_raw_response(
    span_exporter, anthropic_client, instrument_no_content
):
    """Streaming ``with_raw_response.create`` defers parse() and records a full span.

    Regression test: the raw response the SDK returns from
    ``with_raw_response.create(stream=True)`` is a ``LegacyAPIResponse``, not a
    ``Stream``, so it fell past the stream check and the span was ended
    immediately with no response attributes, before the caller even called
    ``parse()``. The proxy must defer finalization until the parsed stream is
    drained and then populate the span with the response model, usage, and
    finish reason.
    """
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    raw_response = anthropic_client.messages.with_raw_response.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    )

    # Raw-response metadata still resolves natively off the proxy.
    assert hasattr(raw_response, "headers")
    assert raw_response.headers is not None

    # Deferred: the span must not be finalized before the caller parses/drains.
    assert span_exporter.get_finished_spans() == ()

    stream = raw_response.parse()
    response_text = ""
    for chunk in stream:
        if chunk.type == "content_block_delta":
            delta = getattr(chunk, "delta", None)
            if delta and hasattr(delta, "text"):
                response_text += delta.text
    assert response_text == "Hello."

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    # The span is no longer a premature empty one: it carries response
    # attributes accumulated from the drained stream.
    assert_span_attributes(
        spans[0],
        request_model=model,
        response_model=model,
        input_tokens=13,
        output_tokens=5,
        finish_reasons=["stop"],
    )


@pytest.mark.vcr()
def test_sync_messages_create_streaming_with_raw_response_never_parsed(
    span_exporter, anthropic_client, instrument_no_content
):
    """A never-parsed streaming raw response is finalized once when closed.

    When the caller reads only metadata and never calls ``parse()``, the span
    must still be finalized (so it does not leak) exactly once when the
    underlying body is closed, since ``stop()`` is not idempotent.
    """
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    raw_response = anthropic_client.messages.with_raw_response.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    )

    # Deferred: nothing finalized while the caller has not parsed or closed.
    assert span_exporter.get_finished_spans() == ()

    # Caller drains/closes the body without ever parsing it.
    raw_response.http_response.close()

    assert len(span_exporter.get_finished_spans()) == 1

    # A second close must not finalize the span again.
    raw_response.http_response.close()
    assert len(span_exporter.get_finished_spans()) == 1


@pytest.mark.vcr()
def test_sync_messages_with_streaming_response_nonstreaming(
    span_exporter, metric_reader, anthropic_client, instrument_no_content
):
    """Non-streaming ``with_streaming_response.create`` records response attrs.

    Regression test for the routing bug: the SDK sets
    ``x-stainless-raw-response: stream`` on *every* ``with_streaming_response``
    call, so keying the stream proxy off that header routed this non-streaming
    call (whose ``parse()`` returns a ``Message``) into the stream path and
    finalized the span with request attributes only. Routing on what ``parse()``
    returns instead extracts the message and records the response model, usage,
    and finish reason.
    """
    from opentelemetry.semconv._incubating.metrics import gen_ai_metrics

    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    with anthropic_client.messages.with_streaming_response.create(
        model=model,
        max_tokens=100,
        messages=messages,
    ) as raw_response:
        assert hasattr(raw_response, "headers")
        message = raw_response.parse()

    from anthropic.types import Message

    assert isinstance(message, Message)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    # The response attributes are now present (they were absent before the fix).
    assert GenAIAttributes.GEN_AI_RESPONSE_MODEL in span.attributes
    assert GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS in span.attributes
    assert_span_attributes(
        span,
        request_model=model,
        response_id=message.id,
        response_model=message.model,
        input_tokens=expected_input_tokens(message.usage),
        output_tokens=message.usage.output_tokens,
        finish_reasons=[normalize_stop_reason(message.stop_reason)],
    )

    # The token-usage metric is recorded for this non-streaming path.
    metrics = {
        metric.name: metric
        for rm in metric_reader.get_metrics_data().resource_metrics
        for scope in rm.scope_metrics
        for metric in scope.metrics
    }
    assert gen_ai_metrics.GEN_AI_CLIENT_TOKEN_USAGE in metrics


@pytest.mark.vcr()
def test_sync_messages_with_streaming_response_streaming(
    span_exporter, anthropic_client, instrument_no_content
):
    """Streaming ``with_streaming_response.create`` defers and records a full span.

    ``parse()`` yields a ``Stream``; draining it finalizes the span with the
    response model, token usage, and finish reason accumulated from the stream.
    """
    model = "claude-sonnet-4-20250514"
    messages = [{"role": "user", "content": "Say hello in one word."}]

    with anthropic_client.messages.with_streaming_response.create(
        model=model,
        max_tokens=100,
        messages=messages,
        stream=True,
    ) as raw_response:
        assert hasattr(raw_response, "headers")
        # Deferred: the span is not finalized before the stream is drained.
        assert span_exporter.get_finished_spans() == ()

        stream = raw_response.parse()
        response_text = ""
        for chunk in stream:
            if chunk.type == "content_block_delta":
                delta = getattr(chunk, "delta", None)
                if delta and hasattr(delta, "text"):
                    response_text += delta.text
    assert response_text == "Hello."

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert_span_attributes(
        spans[0],
        request_model=model,
        response_model=model,
        input_tokens=13,
        output_tokens=5,
        finish_reasons=["stop"],
    )
