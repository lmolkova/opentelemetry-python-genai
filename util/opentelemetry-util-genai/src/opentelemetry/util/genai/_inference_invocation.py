# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import cast

from opentelemetry._logs import Logger
from opentelemetry.trace import INVALID_SPAN, Span, Tracer
from opentelemetry.util.genai._invocation import (
    Error,
    GenAIInvocation,
)
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import (
    GenAiOperationName,
    GenAiTokenType,
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
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            operation_name=operation_name,
            span_name=f"{operation_name} {request_model}"
            if request_model
            else operation_name,
            error_type_resolver=error_type_resolver,
            content_capturing_mode=content_capturing_mode,
        )
        self._provider: str = provider
        self._request_model: str | None = request_model
        self._server_address: str | None = server_address
        self._server_port: int | None = server_port
        self._request_stream: bool | None = None
        self._ttfc_seconds: float | None = None
        self._stream_last_chunk_at: float | None = None
        self.conversation_id: str | None = None

        self.input_messages: list[InputMessage] = []
        self.output_messages: list[OutputMessage] = []
        self.system_instruction: (
            list[SystemInstructionPart] | list[MessagePart]
        ) = []
        """System instructions for the model. Passing ``MessagePart`` is deprecated; use ``SystemInstructionPart``."""
        self._response_model_name: str | None = None
        self.response_id: str | None = None
        self.finish_reasons: list[str] | None = None
        self.input_tokens: int | None = None
        self.output_tokens: int | None = None
        self.thinking_tokens: int | None = None
        self.temperature: float | None = None
        self.top_p: float | None = None
        self.frequency_penalty: float | None = None
        self.presence_penalty: float | None = None
        self.max_tokens: int | None = None
        self.stop_sequences: list[str] | None = None
        self.seed: int | None = None
        self.cache_write_input_tokens: int | None = None
        self.cache_read_input_tokens: int | None = None
        self.text_input_tokens: int | None = None
        self.image_input_tokens: int | None = None
        self.audio_input_tokens: int | None = None
        self.text_output_tokens: int | None = None
        self.image_output_tokens: int | None = None
        self.audio_output_tokens: int | None = None
        self.text_cache_read_input_tokens: int | None = None
        self.image_cache_read_input_tokens: int | None = None
        self.audio_cache_read_input_tokens: int | None = None
        self.reasoning_level: str | None = None
        self.previous_response_id: str | None = None
        self.conversation_compacted: bool | None = None
        self.prompt_name: str | None = None
        self.prompt_version: str | None = None
        self.prompt_variables: Mapping[str, object] | None = None
        self.tool_definitions: list[ToolDefinition] | None = None
        self.top_k: int | None = None
        self.request_choice_count: int | None = None
        self.output_type: str | None = None
        self._inference_span: InferenceSpan = self._spans.inference(
            self._span_name,
            operation_name=self._operation_name,
            provider_name=self._provider,
            request_model=self._request_model,
            server_address=self._server_address,
            server_port=self._server_port,
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

    @property
    def response_model_name(self) -> str | None:
        return self._response_model_name

    @response_model_name.setter
    def response_model_name(self, value: str | None) -> None:
        self._response_model_name = value

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

        if self._ttfc_seconds is None:
            self._ttfc_seconds = delta
            self._metrics.client_operation_time_to_first_chunk(
                delta,
                operation_name=self._operation_name,
                provider_name=self._provider,
                server_address=self._server_address,
                server_port=self._server_port,
                request_model=self._request_model,
                response_model=self._response_model_name,
                additional_attributes=self.metric_attributes,
                context=self._span_context,
            )
            return

        self._metrics.client_operation_time_per_output_chunk(
            delta,
            operation_name=self._operation_name,
            provider_name=self._provider,
            server_address=self._server_address,
            server_port=self._server_port,
            request_model=self._request_model,
            response_model=self._response_model_name,
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
        if error is not None:
            span.set_error_details(error.type, error.message)
            self._error_type = error.type
        span.set_conversation_id(self.conversation_id)
        span.set_request_stream(self._request_stream)
        span.set_request_temperature(self.temperature)
        span.set_request_top_p(self.top_p)
        span.set_request_top_k(self.top_k)
        span.set_request_frequency_penalty(self.frequency_penalty)
        span.set_request_presence_penalty(self.presence_penalty)
        span.set_request_max_tokens(self.max_tokens)
        span.set_request_stop_sequences(self.stop_sequences)
        span.set_request_seed(self.seed)
        span.set_response_finish_reasons(self._get_finish_reasons())
        span.set_response_model(self.response_model_name)
        span.set_response_id(self.response_id)
        span.set_usage_input_tokens(self.input_tokens)
        span.set_usage_output_tokens(self.output_tokens)
        span.set_request_choice_count(self.request_choice_count)
        span.set_output_type(self.output_type)
        span.set_usage_cache_write_input_tokens(
            self.cache_write_input_tokens or None
        )
        span.set_usage_cache_read_input_tokens(
            self.cache_read_input_tokens or None
        )
        span.set_usage_reasoning_output_tokens(self.thinking_tokens or None)
        span.set_usage_text_input_tokens(self.text_input_tokens or None)
        span.set_usage_image_input_tokens(self.image_input_tokens or None)
        span.set_usage_audio_input_tokens(self.audio_input_tokens or None)
        span.set_usage_text_output_tokens(self.text_output_tokens or None)
        span.set_usage_image_output_tokens(self.image_output_tokens or None)
        span.set_usage_audio_output_tokens(self.audio_output_tokens or None)
        span.set_usage_text_cache_read_input_tokens(
            self.text_cache_read_input_tokens or None
        )
        span.set_usage_image_cache_read_input_tokens(
            self.image_cache_read_input_tokens or None
        )
        span.set_usage_audio_cache_read_input_tokens(
            self.audio_cache_read_input_tokens or None
        )
        span.set_request_reasoning_level(self.reasoning_level)
        span.set_request_previous_response_id(self.previous_response_id)
        span.set_conversation_compacted(
            True if self.conversation_compacted else None
        )
        span.set_prompt_name(self.prompt_name)
        span.set_prompt_version(self.prompt_version)
        span.set_response_time_to_first_chunk(self._ttfc_seconds)
        if self._should_capture_content_on_span:
            span.set_input_messages(self.input_messages or None)
            span.set_output_messages(self.output_messages or None)
            span.set_system_instructions(
                cast(
                    "Sequence[SystemInstructionPart] | None",
                    self.system_instruction or None,
                )
            )
            if self.prompt_variables:
                for name, value in self.prompt_variables.items():
                    span.set_prompt_variable(
                        name,
                        value
                        if isinstance(value, str)
                        else gen_ai_json_dumps(value),
                    )
        span.set_tool_definitions(self.tool_definitions)
        span.set_attributes(self.attributes)
        duration_seconds = max(
            timeit.default_timer() - self._monotonic_start_s,
            0.0,
        )
        self._metrics.client_operation_duration(
            duration_seconds,
            operation_name=self._operation_name,
            server_address=self._server_address,
            server_port=self._server_port,
            request_model=self._request_model,
            response_model=self._response_model_name,
            provider_name=self._provider,
            error_type=self._error_type,
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )
        if self.input_tokens is not None:
            self._metrics.client_token_usage(
                self.input_tokens,
                operation_name=self._operation_name,
                provider_name=self._provider,
                token_type=GenAiTokenType.INPUT,
                server_address=self._server_address,
                server_port=self._server_port,
                request_model=self._request_model,
                response_model=self._response_model_name,
                additional_attributes=self.metric_attributes,
                context=self._span_context,
            )
        if self.output_tokens is not None:
            self._metrics.client_token_usage(
                self.output_tokens,
                operation_name=self._operation_name,
                provider_name=self._provider,
                token_type=GenAiTokenType.OUTPUT,
                server_address=self._server_address,
                server_port=self._server_port,
                request_model=self._request_model,
                response_model=self._response_model_name,
                additional_attributes=self.metric_attributes,
                context=self._span_context,
            )
        event = self._maybe_create_event()
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
    ) -> ClientInferenceOperationDetailsEvent | None:
        """Emit a gen_ai.client.inference.operation.details event.

        For more details, see the semantic convention documentation:
        https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md#event-eventgen_aiclientinferenceoperationdetails
        """
        if not should_emit_event():
            return None

        input_messages = None
        output_messages = None
        system_instructions = None
        prompt_variables = None
        if self._should_capture_content_on_event:
            input_messages = self.input_messages or None
            output_messages = self.output_messages or None
            system_instructions = cast(
                "Sequence[SystemInstructionPart] | None",
                self.system_instruction or None,
            )
            if self.prompt_variables:
                prompt_variables = {
                    name: value
                    if isinstance(value, str)
                    else gen_ai_json_dumps(value)
                    for name, value in self.prompt_variables.items()
                }

        return self._events.client_inference_operation_details(
            operation_name=self._operation_name,
            provider_name=self._provider,
            request_model=self._request_model,
            server_address=self._server_address,
            server_port=self._server_port,
            conversation_id=self.conversation_id,
            request_stream=self._request_stream,
            request_temperature=self.temperature,
            request_top_p=self.top_p,
            request_top_k=self.top_k,
            request_frequency_penalty=self.frequency_penalty,
            request_presence_penalty=self.presence_penalty,
            request_max_tokens=self.max_tokens,
            request_stop_sequences=self.stop_sequences,
            request_seed=self.seed,
            response_finish_reasons=self._get_finish_reasons(),
            response_model=self.response_model_name,
            response_id=self.response_id,
            usage_input_tokens=self.input_tokens,
            usage_output_tokens=self.output_tokens,
            request_choice_count=self.request_choice_count,
            output_type=self.output_type,
            usage_cache_write_input_tokens=self.cache_write_input_tokens
            or None,
            usage_cache_read_input_tokens=self.cache_read_input_tokens or None,
            usage_reasoning_output_tokens=self.thinking_tokens or None,
            usage_text_input_tokens=self.text_input_tokens or None,
            usage_image_input_tokens=self.image_input_tokens or None,
            usage_audio_input_tokens=self.audio_input_tokens or None,
            usage_text_output_tokens=self.text_output_tokens or None,
            usage_image_output_tokens=self.image_output_tokens or None,
            usage_audio_output_tokens=self.audio_output_tokens or None,
            usage_text_cache_read_input_tokens=self.text_cache_read_input_tokens
            or None,
            usage_image_cache_read_input_tokens=self.image_cache_read_input_tokens
            or None,
            usage_audio_cache_read_input_tokens=self.audio_cache_read_input_tokens
            or None,
            request_reasoning_level=self.reasoning_level,
            request_previous_response_id=self.previous_response_id,
            conversation_compacted=True
            if self.conversation_compacted
            else None,
            prompt_name=self.prompt_name,
            prompt_version=self.prompt_version,
            prompt_variables=prompt_variables,
            response_time_to_first_chunk=self._ttfc_seconds,
            input_messages=input_messages,
            output_messages=output_messages,
            system_instructions=system_instructions,
            tool_definitions=self.tool_definitions,
            error_type=self._error_type,
            additional_attributes=self.attributes,
            context=self._span_context,
        )


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
