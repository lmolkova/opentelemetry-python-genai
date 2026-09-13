# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit
from collections.abc import Mapping
from dataclasses import dataclass, field

from opentelemetry._logs import Logger
from opentelemetry.trace import INVALID_SPAN, Span, Tracer
from opentelemetry.util.genai._attribute import _Attribute
from opentelemetry.util.genai._invocation import (
    Error,
    GenAIInvocation,
)
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import (
    GenAiOperationName,
    GenAiTokenType,
    InferenceAttributes,
)
from opentelemetry.util.genai.semconv.gen_ai._events import (
    ClientInferenceOperationDetailsEvent,
)
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import (
    InferenceSpan,
    _Spans,
)
from opentelemetry.util.genai.types import (
    ErrorTypeResolver,
    InputMessage,
    MessagePart,
    OutputMessage,
    SystemInstructionPart,
    ToolDefinition,
)
from opentelemetry.util.genai.utils import (
    ContentCapturingMode,
    gen_ai_json_dumps,
    should_emit_event,
)
from opentelemetry.util.types import AttributeValue


class InferenceInvocation(GenAIInvocation):
    """Represents a single LLM chat/completion call.

    Use handler.inference(provider) rather than constructing this directly.
    """

    conversation_id = _Attribute[str | None]()
    input_messages = _Attribute[list[InputMessage] | None]()
    output_messages = _Attribute[list[OutputMessage] | None]()
    system_instruction = _Attribute[
        list[SystemInstructionPart] | list[MessagePart] | None
    ]("system_instructions")
    """System instructions for the model. Passing ``MessagePart`` is deprecated; use ``SystemInstructionPart``."""
    response_model_name = _Attribute[str | None]("response_model")
    response_id = _Attribute[str | None]()
    finish_reasons = _Attribute[list[str] | None]("response_finish_reasons")
    input_tokens = _Attribute[int | None]("usage_input_tokens")
    output_tokens = _Attribute[int | None]("usage_output_tokens")
    thinking_tokens = _Attribute[int | None]("usage_reasoning_output_tokens")
    temperature = _Attribute[float | None]("request_temperature")
    top_p = _Attribute[float | None]("request_top_p")
    top_k = _Attribute[int | None]("request_top_k")
    frequency_penalty = _Attribute[float | None]("request_frequency_penalty")
    presence_penalty = _Attribute[float | None]("request_presence_penalty")
    max_tokens = _Attribute[int | None]("request_max_tokens")
    stop_sequences = _Attribute[list[str] | None]("request_stop_sequences")
    seed = _Attribute[int | None]("request_seed")
    request_choice_count = _Attribute[int | None]("request_choice_count")
    reasoning_level = _Attribute[str | None]("request_reasoning_level")
    previous_response_id = _Attribute[str | None](
        "request_previous_response_id"
    )
    cache_write_input_tokens = _Attribute[int | None](
        "usage_cache_write_input_tokens"
    )
    cache_read_input_tokens = _Attribute[int | None](
        "usage_cache_read_input_tokens"
    )
    text_input_tokens = _Attribute[int | None]("usage_text_input_tokens")
    image_input_tokens = _Attribute[int | None]("usage_image_input_tokens")
    audio_input_tokens = _Attribute[int | None]("usage_audio_input_tokens")
    text_output_tokens = _Attribute[int | None]("usage_text_output_tokens")
    image_output_tokens = _Attribute[int | None]("usage_image_output_tokens")
    audio_output_tokens = _Attribute[int | None]("usage_audio_output_tokens")
    text_cache_read_input_tokens = _Attribute[int | None](
        "usage_text_cache_read_input_tokens"
    )
    image_cache_read_input_tokens = _Attribute[int | None](
        "usage_image_cache_read_input_tokens"
    )
    audio_cache_read_input_tokens = _Attribute[int | None](
        "usage_audio_cache_read_input_tokens"
    )
    conversation_compacted = _Attribute[bool | None]()
    prompt_name = _Attribute[str | None]()
    prompt_version = _Attribute[str | None]()
    prompt_variables = _Attribute[Mapping[str, object] | None](
        "prompt_variable"
    )
    tool_definitions = _Attribute[list[ToolDefinition] | None]()
    output_type = _Attribute[str | None]()

    @property
    def _request_stream(self) -> bool | None:
        return self._semconv_attributes.request_stream

    @_request_stream.setter
    def _request_stream(self, value: bool | None) -> None:
        self._semconv_attributes.request_stream = value

    def __init__(
        self,
        spans: _Spans,
        metrics: _Metrics,
        logger: Logger,
        completion_hook: CompletionHook,
        provider: str,
        *,
        request_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        operation_name: str | None = None,
        error_type_resolver: ErrorTypeResolver | None = None,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        operation_name = operation_name or GenAiOperationName.CHAT.value
        """Use handler.inference(provider) rather than calling this directly."""
        self._semconv_attributes = InferenceAttributes(
            operation_name=operation_name,
            provider_name=provider,
            request_model=request_model,
            server_address=server_address,
            server_port=server_port,
        )
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            span_name=f"{operation_name} {request_model}"
            if request_model
            else operation_name,
            error_type_resolver=error_type_resolver,
            content_capturing_mode=content_capturing_mode,
        )
        self._stream_last_chunk_at: float | None = None
        self._inference_span: InferenceSpan = self._spans.inference(
            self._span_name,
            operation_name=self._semconv_attributes.operation_name,
            provider_name=self._semconv_attributes.provider_name,
            request_model=self._semconv_attributes.request_model,
            server_address=self._semconv_attributes.server_address,
            server_port=self._semconv_attributes.server_port,
        )
        self._start(self._inference_span)

    @property
    def cache_creation_input_tokens(self) -> int | None:
        """
        .. deprecated:: 1.3b0
            Use :attr:`cache_write_input_tokens` instead.
        """
        return self.cache_write_input_tokens

    @cache_creation_input_tokens.setter
    def cache_creation_input_tokens(self, value: int | None) -> None:
        self.cache_write_input_tokens = value

    def record_stream_chunk(self) -> None:
        """Mark the request as streamed and record one output chunk arriving."""
        if self._context_token is None:
            return
        self._request_stream = True
        self._on_stream_chunk(timeit.default_timer())

    def _on_stream_chunk(self, chunk_at: float) -> None:
        last_chunk_at = (
            self._stream_last_chunk_at
            if self._stream_last_chunk_at is not None
            else self._monotonic_start_s
        )
        self._stream_last_chunk_at = chunk_at
        delta = max(chunk_at - last_chunk_at, 0.0)

        if self._semconv_attributes.response_time_to_first_chunk is None:
            self._semconv_attributes.response_time_to_first_chunk = delta
            self._metrics.client_operation_time_to_first_chunk(
                delta,
                self._semconv_attributes,
                additional_attributes=self.metric_attributes,
                context=self._span_context,
            )
            return

        self._metrics.client_operation_time_per_output_chunk(
            delta,
            self._semconv_attributes,
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )

    def _get_finish_reasons(self) -> list[str] | None:
        if self.finish_reasons is not None:
            return self.finish_reasons or None
        if self.output_messages:
            reasons = [
                msg.finish_reason
                for msg in self.output_messages
                if msg.finish_reason
            ]
            return reasons or None
        return None

    def _apply_finish(self, error: Error | None = None) -> None:
        span = self._inference_span
        attributes = self._semconv_attributes
        if error is not None:
            span.set_error_details(error.type, error.message)
            attributes.error_type = error.type
        attributes.response_finish_reasons = self._get_finish_reasons()
        span.apply(attributes)
        if self._should_capture_content_on_span:
            span.set_input_messages(attributes.input_messages or None)
            span.set_output_messages(attributes.output_messages or None)
            span.set_system_instructions(
                attributes.system_instructions or None
            )
            span.set_tool_definitions(attributes.tool_definitions or None)
            if attributes.prompt_variable:
                for name, value in attributes.prompt_variable.items():
                    span.set_prompt_variable(
                        name,
                        value
                        if isinstance(value, str)
                        else gen_ai_json_dumps(value),
                    )
        span.set_attributes(self.attributes)
        duration_seconds = max(
            timeit.default_timer() - self._monotonic_start_s,
            0.0,
        )
        self._metrics.client_operation_duration(
            duration_seconds,
            attributes,
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )
        if self.input_tokens is not None:
            self._metrics.client_token_usage(
                self.input_tokens,
                attributes,
                token_type=GenAiTokenType.INPUT,
                additional_attributes=self.metric_attributes,
                context=self._span_context,
            )
        if self.output_tokens is not None:
            self._metrics.client_token_usage(
                self.output_tokens,
                attributes,
                token_type=GenAiTokenType.OUTPUT,
                additional_attributes=self.metric_attributes,
                context=self._span_context,
            )
        event = self._maybe_create_event(attributes)
        log_record = event.log_record if event is not None else None
        self._call_completion_hook(
            inputs=self.input_messages,
            outputs=self.output_messages,
            system_instruction=self.system_instruction,
            tool_definitions=self.tool_definitions,
            log_record=log_record,
        )
        if event is not None:
            event.emit()

    def _maybe_create_event(
        self,
        attributes: InferenceAttributes,
    ) -> ClientInferenceOperationDetailsEvent | None:
        """Emit a gen_ai.client.inference.operation.details event.

        For more details, see the semantic convention documentation:
        https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md#event-eventgen_aiclientinferenceoperationdetails
        """
        if not should_emit_event():
            return None

        event = (
            self._events.client_inference_operation_details_from_attributes(
                attributes,
                additional_attributes=self.attributes,
                context=self._span_context,
            )
        )
        if self._should_capture_content_on_event:
            event.set_input_messages(attributes.input_messages or None)
            event.set_output_messages(attributes.output_messages or None)
            event.set_system_instructions(
                attributes.system_instructions or None
            )
            if attributes.prompt_variable:
                for name, value in attributes.prompt_variable.items():
                    event.set_prompt_variable(
                        name,
                        value
                        if isinstance(value, str)
                        else gen_ai_json_dumps(value),
                    )
        return event


@dataclass
class LLMInvocation:
    """Deprecated. Use InferenceInvocation instead.

    Data container for an LLM invocation. Pass to handler.llm() to start
    the span, then update fields and call handler.stop_llm() or handler.fail_llm().
    """

    request_model: str | None = None
    input_messages: list[InputMessage] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    output_messages: list[OutputMessage] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    system_instruction: (  # pyright: ignore[reportUnknownVariableType]
        list[SystemInstructionPart] | list[MessagePart]
    ) = field(default_factory=list)
    provider: str | None = None
    response_model_name: str | None = None
    response_id: str | None = None
    finish_reasons: list[str] | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None

    attributes: dict[str, AttributeValue] = field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]
    """Additional attributes to set on spans and/or events. Not set on metrics."""
    metric_attributes: dict[str, AttributeValue] = field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]
    """Additional attributes to set on metrics. Must be low cardinality. Not set on spans or events."""
    temperature: float | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    max_tokens: int | None = None
    stop_sequences: list[str] | None = None
    seed: int | None = None
    server_address: str | None = None
    server_port: int | None = None

    _inference_invocation: InferenceInvocation | None = field(
        default=None, init=False, repr=False
    )

    def _start_with_handler(
        self,
        tracer: Tracer,
        metrics: _Metrics,
        logger: Logger,
        completion_hook: CompletionHook,
        *,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        """Create and start an InferenceInvocation from this data container. Called by handler.start_llm()."""
        inv = InferenceInvocation(
            _Spans(tracer),
            metrics,
            logger,
            completion_hook,
            self.provider or "",
            request_model=self.request_model,
            server_address=self.server_address,
            server_port=self.server_port,
            content_capturing_mode=content_capturing_mode,
        )
        inv.input_messages = self.input_messages
        inv.output_messages = self.output_messages
        inv.system_instruction = self.system_instruction
        inv.response_model_name = self.response_model_name
        inv.response_id = self.response_id
        inv.finish_reasons = self.finish_reasons
        inv.input_tokens = self.input_tokens
        inv.output_tokens = self.output_tokens

        inv.temperature = self.temperature
        inv.top_p = self.top_p
        inv.frequency_penalty = self.frequency_penalty
        inv.presence_penalty = self.presence_penalty
        inv.max_tokens = self.max_tokens
        inv.stop_sequences = self.stop_sequences
        inv.seed = self.seed
        inv.attributes.update(self.attributes)
        inv.metric_attributes.update(self.metric_attributes)
        self._inference_invocation = inv

    def _sync_to_invocation(self) -> None:
        inv = self._inference_invocation
        if inv is None:
            return
        # Start attributes (provider, request_model, server_address, server_port)
        # are fixed at construction in _start_with_handler and cannot be reassigned.
        inv.input_messages = self.input_messages
        inv.output_messages = self.output_messages
        inv.system_instruction = self.system_instruction
        inv.response_model_name = self.response_model_name
        inv.response_id = self.response_id
        inv.finish_reasons = self.finish_reasons
        inv.input_tokens = self.input_tokens
        inv.output_tokens = self.output_tokens

        inv.temperature = self.temperature
        inv.top_p = self.top_p
        inv.frequency_penalty = self.frequency_penalty
        inv.presence_penalty = self.presence_penalty
        inv.max_tokens = self.max_tokens
        inv.stop_sequences = self.stop_sequences
        inv.seed = self.seed
        inv.attributes = self.attributes
        inv.metric_attributes = self.metric_attributes

    @property
    def span(self) -> Span:
        """The underlying span, for back-compat with code that checks span.is_recording()."""
        return (
            self._inference_invocation.span
            if self._inference_invocation is not None
            else INVALID_SPAN
        )
