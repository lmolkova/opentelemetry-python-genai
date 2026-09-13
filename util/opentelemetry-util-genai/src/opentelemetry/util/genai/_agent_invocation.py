# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import cast

from opentelemetry._logs import Logger
from opentelemetry.util.genai._attribute import _Attribute
from opentelemetry.util.genai._invocation import (
    Error,
    GenAIInvocation,
)
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import (
    GenAiOperationName,
    GenAiTokenType,
    LocalAgentAttributes,
    RemoteAgentAttributes,
)
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import (
    InvokeAgentClientSpan,
    InvokeAgentSpan,
    _Spans,
)
from opentelemetry.util.genai.types import (
    InputMessage,
    MessagePart,
    OutputMessage,
    SystemInstructionPart,
    ToolDefinition,
)
from opentelemetry.util.genai.utils import ContentCapturingMode


class AgentInvocation(GenAIInvocation, ABC):
    """Base class representing a GenAI agent invocation (invoke_agent span).

    Use handler.invoke_local_agent() or handler.invoke_remote_agent()
    rather than constructing this directly.

    Reference:
        Client span: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-client-span
        Internal span: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-internal-span
    """

    _request_model = _Attribute[str | None]("request_model")
    _agent_name = _Attribute[str | None]("agent_name")
    agent_description = _Attribute[str | None]()
    conversation_id = _Attribute[str | None]()
    data_source_id = _Attribute[str | None]()
    output_type = _Attribute[str | None]()
    temperature = _Attribute[float | None]("request_temperature")
    top_p = _Attribute[float | None]("request_top_p")
    frequency_penalty = _Attribute[float | None]("request_frequency_penalty")
    presence_penalty = _Attribute[float | None]("request_presence_penalty")
    max_tokens = _Attribute[int | None]("request_max_tokens")
    stop_sequences = _Attribute[list[str] | None]("request_stop_sequences")
    seed = _Attribute[int | None]("request_seed")
    choice_count = _Attribute[int | None]("request_choice_count")
    finish_reasons = _Attribute[list[str] | None]("response_finish_reasons")
    input_tokens = _Attribute[int | None]("usage_input_tokens")
    output_tokens = _Attribute[int | None]("usage_output_tokens")
    input_messages = _Attribute[list[InputMessage]]()
    output_messages = _Attribute[list[OutputMessage]]()
    system_instruction = _Attribute[
        list[SystemInstructionPart] | Sequence[MessagePart]
    ]("system_instructions")
    tool_definitions = _Attribute[list[ToolDefinition] | None]()

    def __init__(
        self,
        spans: _Spans,
        metrics: _Metrics,
        logger: Logger,
        completion_hook: CompletionHook,
        *,
        semconv_attributes: LocalAgentAttributes | RemoteAgentAttributes,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        self._semconv_attributes = semconv_attributes
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            span_name=(
                f"{semconv_attributes.operation_name} {semconv_attributes.agent_name}"
                if semconv_attributes.agent_name
                else str(semconv_attributes.operation_name)
            ),
            content_capturing_mode=content_capturing_mode,
        )
        self._agent_span: InvokeAgentSpan | InvokeAgentClientSpan

    @property
    def agent_name(self) -> str | None:
        """The agent name provided at construction time."""
        return self._semconv_attributes.agent_name

    def _apply_finish(self, error: Error | None = None) -> None:
        span = self._agent_span
        attributes = self._semconv_attributes
        if error is not None:
            span.set_error_details(error.type, error.message)
            attributes.error_type = error.type
        attributes.response_finish_reasons = self.finish_reasons or None
        self._apply_span_attributes()
        if self._should_capture_content_on_span:
            span.set_input_messages(attributes.input_messages or None)
            span.set_output_messages(attributes.output_messages or None)
            span.set_system_instructions(
                attributes.system_instructions or None
            )
        span.set_tool_definitions(attributes.tool_definitions)
        span.set_attributes(self.attributes)
        self._call_completion_hook(
            inputs=self.input_messages,
            outputs=self.output_messages,
            system_instruction=cast(
                "list[SystemInstructionPart] | list[MessagePart]",
                self.system_instruction,
            ),
            tool_definitions=self.tool_definitions,
        )
        self._record_metrics()

    @abstractmethod
    def _record_metrics(self) -> None:
        """Record invocation metrics."""

    @abstractmethod
    def _apply_span_attributes(self) -> None:
        """Apply attributes for the concrete agent span."""


class LocalAgentInvocation(AgentInvocation):
    """Represents an in-process agent invocation (INTERNAL span kind).

    Use handler.invoke_local_agent() rather than constructing this directly.

    Reference:
        https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-internal-span
    """

    def __init__(
        self,
        spans: _Spans,
        metrics: _Metrics,
        logger: Logger,
        completion_hook: CompletionHook,
        *,
        request_model: str | None = None,
        agent_name: str | None = None,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        operation_name = GenAiOperationName.INVOKE_AGENT.value
        attributes = LocalAgentAttributes(
            operation_name=operation_name,
            request_model=request_model,
            agent_name=agent_name,
        )
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            semconv_attributes=attributes,
            content_capturing_mode=content_capturing_mode,
        )
        self._agent_span = self._spans.invoke_agent(
            self._span_name,
            operation_name=self._semconv_attributes.operation_name,
            agent_name=self._semconv_attributes.agent_name,
            request_model=self._semconv_attributes.request_model,
        )
        self._start(self._agent_span)

    def _apply_span_attributes(self) -> None:
        span = cast("InvokeAgentSpan", self._agent_span)
        attributes = cast("LocalAgentAttributes", self._semconv_attributes)
        span.apply(attributes)

    def _record_metrics(self) -> None:
        duration_seconds = max(
            timeit.default_timer() - self._monotonic_start_s,
            0.0,
        )
        self._metrics.invoke_agent_duration(
            duration_seconds,
            cast("LocalAgentAttributes", self._semconv_attributes),
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )


class RemoteAgentInvocation(AgentInvocation):
    """Represents a remote agent invocation (CLIENT span kind).

    Use handler.invoke_remote_agent() rather than constructing this directly.

    Reference:
        https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-client-span
    """

    _provider = _Attribute[str]("provider_name")
    _server_address = _Attribute[str | None]("server_address")
    _server_port = _Attribute[int | None]("server_port")
    agent_id = _Attribute[str | None]()
    agent_version = _Attribute[str | None]()
    previous_response_id = _Attribute[str | None](
        "request_previous_response_id"
    )
    cache_read_input_tokens = _Attribute[int | None](
        "usage_cache_read_input_tokens"
    )

    @property
    def _request_stream(self) -> bool | None:
        attributes = cast("RemoteAgentAttributes", self._semconv_attributes)
        return attributes.request_stream

    @_request_stream.setter
    def _request_stream(self, value: bool | None) -> None:
        attributes = cast("RemoteAgentAttributes", self._semconv_attributes)
        attributes.request_stream = value

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
        agent_name: str | None = None,
        agent_id: str | None = None,
        agent_version: str | None = None,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        operation_name = GenAiOperationName.INVOKE_AGENT.value
        attributes = RemoteAgentAttributes(
            operation_name=operation_name,
            provider_name=provider,
            request_model=request_model,
            server_address=server_address,
            server_port=server_port,
            agent_name=agent_name,
            agent_id=agent_id,
            agent_version=agent_version,
        )
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            semconv_attributes=attributes,
            content_capturing_mode=content_capturing_mode,
        )
        self._stream_last_chunk_at: float | None = None

        self._agent_span = self._spans.invoke_agent_client(
            self._span_name,
            operation_name=self._semconv_attributes.operation_name,
            provider_name=attributes.provider_name,
            agent_name=self._semconv_attributes.agent_name,
            request_model=self._semconv_attributes.request_model,
            server_address=attributes.server_address,
            server_port=attributes.server_port,
        )
        self._start(self._agent_span)

    def _apply_span_attributes(self) -> None:
        span = cast("InvokeAgentClientSpan", self._agent_span)
        attributes = cast("RemoteAgentAttributes", self._semconv_attributes)
        span.apply(attributes)

    @property
    def cache_write_input_tokens(self) -> int | None:
        """The number of cache write input tokens."""
        attributes = cast("RemoteAgentAttributes", self._semconv_attributes)
        return attributes.usage_cache_write_input_tokens

    @cache_write_input_tokens.setter
    def cache_write_input_tokens(self, value: int | None) -> None:
        attributes = cast("RemoteAgentAttributes", self._semconv_attributes)
        attributes.usage_cache_write_input_tokens = value

    @property
    def cache_creation_input_tokens(self) -> int | None:
        """The number of cache creation input tokens.

        .. deprecated:: 1.3b0
            Use :attr:`cache_write_input_tokens` instead.
        """
        attributes = cast("RemoteAgentAttributes", self._semconv_attributes)
        return attributes.usage_cache_write_input_tokens

    @cache_creation_input_tokens.setter
    def cache_creation_input_tokens(self, value: int | None) -> None:
        attributes = cast("RemoteAgentAttributes", self._semconv_attributes)
        attributes.usage_cache_write_input_tokens = value

    def _on_stream_chunk(self, chunk_at: float) -> None:
        attributes = cast("RemoteAgentAttributes", self._semconv_attributes)
        last_chunk_at = (
            self._stream_last_chunk_at
            if self._stream_last_chunk_at is not None
            else self._monotonic_start_s
        )
        self._stream_last_chunk_at = chunk_at
        delta = max(chunk_at - last_chunk_at, 0.0)

        if attributes.response_time_to_first_chunk is None:
            attributes.response_time_to_first_chunk = delta
            self._metrics.client_operation_time_to_first_chunk(
                delta,
                attributes,
                additional_attributes=self.metric_attributes,
                context=self._span_context,
            )
            return

        self._metrics.client_operation_time_per_output_chunk(
            delta,
            attributes,
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )

    def _record_metrics(self) -> None:
        attributes = cast("RemoteAgentAttributes", self._semconv_attributes)
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
