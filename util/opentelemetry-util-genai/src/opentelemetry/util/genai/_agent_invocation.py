# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import cast

from opentelemetry._logs import Logger
from opentelemetry.util.genai._invocation import (
    Error,
    GenAIInvocation,
)
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import (
    GenAiOperationName,
    GenAiTokenType,
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
        _operation_name = GenAiOperationName.INVOKE_AGENT.value
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            operation_name=_operation_name,
            span_name=f"{_operation_name} {agent_name}"
            if agent_name
            else _operation_name,
            content_capturing_mode=content_capturing_mode,
        )
        self._request_model: str | None = request_model
        self._agent_name: str | None = agent_name
        self.agent_description: str | None = None

        self.conversation_id: str | None = None
        self.data_source_id: str | None = None
        self.output_type: str | None = None

        self.temperature: float | None = None
        self.top_p: float | None = None
        self.frequency_penalty: float | None = None
        self.presence_penalty: float | None = None
        self.max_tokens: int | None = None
        self.stop_sequences: list[str] | None = None
        self.seed: int | None = None
        self.choice_count: int | None = None

        self.finish_reasons: list[str] | None = None

        self.input_tokens: int | None = None
        self.output_tokens: int | None = None

        self.input_messages: list[InputMessage] = []
        self.output_messages: list[OutputMessage] = []
        self.system_instruction: (
            list[SystemInstructionPart] | list[MessagePart]
        ) = []
        """System instructions for the agent. Passing ``MessagePart`` is deprecated; use ``SystemInstructionPart``."""
        self.tool_definitions: list[ToolDefinition] | None = None
        self._agent_span: InvokeAgentSpan | InvokeAgentClientSpan

    @property
    def agent_name(self) -> str | None:
        """The agent name provided at construction time."""
        return self._agent_name

    def _apply_finish(self, error: Error | None = None) -> None:
        span = self._agent_span
        if error is not None:
            span.set_error_details(error.type, error.message)
            self._error_type = error.type

        span.set_agent_description(self.agent_description)
        span.set_conversation_id(self.conversation_id)
        span.set_data_source_id(self.data_source_id)
        span.set_output_type(self.output_type)
        span.set_request_temperature(self.temperature)
        span.set_request_top_p(self.top_p)
        span.set_request_frequency_penalty(self.frequency_penalty)
        span.set_request_presence_penalty(self.presence_penalty)
        span.set_request_max_tokens(self.max_tokens)
        span.set_request_stop_sequences(self.stop_sequences)
        span.set_request_seed(self.seed)
        span.set_request_choice_count(self.choice_count)
        span.set_response_finish_reasons(self.finish_reasons or None)
        span.set_usage_input_tokens(self.input_tokens)
        span.set_usage_output_tokens(self.output_tokens)
        if self._should_capture_content_on_span:
            span.set_input_messages(self.input_messages or None)
            span.set_output_messages(self.output_messages or None)
            span.set_system_instructions(
                cast(
                    "Sequence[SystemInstructionPart] | None",
                    self.system_instruction or None,
                )
            )
        span.set_tool_definitions(self.tool_definitions)
        span.set_attributes(self.attributes)
        self._call_completion_hook(
            inputs=self.input_messages,
            outputs=self.output_messages,
            system_instruction=self.system_instruction,
            tool_definitions=self.tool_definitions,
        )
        self._record_metrics()

    @abstractmethod
    def _record_metrics(self) -> None:
        """Record invocation metrics."""


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
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            request_model=request_model,
            agent_name=agent_name,
            content_capturing_mode=content_capturing_mode,
        )
        self._agent_span = self._spans.invoke_agent(
            self._span_name,
            operation_name=self._operation_name,
            agent_name=self._agent_name,
            request_model=self._request_model,
        )
        self._start(self._agent_span)

    def _record_metrics(self) -> None:
        duration_seconds = max(
            timeit.default_timer() - self._monotonic_start_s,
            0.0,
        )
        self._metrics.invoke_agent_duration(
            duration_seconds,
            error_type=self._error_type,
            agent_name=self._agent_name,
            request_model=self._request_model,
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )


class RemoteAgentInvocation(AgentInvocation):
    """Represents a remote agent invocation (CLIENT span kind).

    Use handler.invoke_remote_agent() rather than constructing this directly.

    Reference:
        https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-client-span
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
        agent_name: str | None = None,
        agent_id: str | None = None,
        agent_version: str | None = None,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            request_model=request_model,
            agent_name=agent_name,
            content_capturing_mode=content_capturing_mode,
        )
        self._provider: str = provider
        self._server_address: str | None = server_address
        self._server_port: int | None = server_port
        self._request_stream: bool | None = None
        self._ttfc_seconds: float | None = None
        self._stream_last_chunk_at: float | None = None

        self.agent_id: str | None = agent_id
        self.agent_version: str | None = agent_version
        self.previous_response_id: str | None = None
        self._cache_write_input_tokens: int | None = None
        self.cache_read_input_tokens: int | None = None

        self._agent_span = self._spans.invoke_agent_client(
            self._span_name,
            operation_name=self._operation_name,
            provider_name=self._provider,
            agent_name=self._agent_name,
            request_model=self._request_model,
            server_address=self._server_address,
            server_port=self._server_port,
        )
        self._start(self._agent_span)

    @property
    def cache_write_input_tokens(self) -> int | None:
        """The number of cache write input tokens."""
        return self._cache_write_input_tokens

    @cache_write_input_tokens.setter
    def cache_write_input_tokens(self, value: int | None) -> None:
        self._cache_write_input_tokens = value

    @property
    def cache_creation_input_tokens(self) -> int | None:
        """The number of cache creation input tokens.

        .. deprecated:: 1.3b0
            Use :attr:`cache_write_input_tokens` instead.
        """
        return self._cache_write_input_tokens

    @cache_creation_input_tokens.setter
    def cache_creation_input_tokens(self, value: int | None) -> None:
        self._cache_write_input_tokens = value

    def _apply_finish(self, error: Error | None = None) -> None:
        span = cast("InvokeAgentClientSpan", self._agent_span)
        span.set_agent_id(self.agent_id)
        span.set_agent_version(self.agent_version)
        span.set_request_previous_response_id(self.previous_response_id)
        span.set_usage_cache_write_input_tokens(self.cache_write_input_tokens)
        span.set_usage_cache_read_input_tokens(self.cache_read_input_tokens)
        super()._apply_finish(error)

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
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )

    def _record_metrics(self) -> None:
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
                additional_attributes=self.metric_attributes,
                context=self._span_context,
            )
