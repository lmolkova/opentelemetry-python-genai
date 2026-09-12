# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit
from abc import ABC, abstractmethod
from typing import Final

from opentelemetry._logs import Logger
from opentelemetry.semconv._incubating.attributes import (
    gen_ai_attributes as GenAI,
)
from opentelemetry.semconv.attributes import server_attributes
from opentelemetry.util.genai._invocation import (
    Error,
    GenAIInvocation,
    get_content_attributes,
)
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import GenAiTokenType
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import _Spans
from opentelemetry.util.genai.types import (
    InputMessage,
    MessagePart,
    OutputMessage,
    SystemInstructionPart,
    ToolDefinition,
)
from opentelemetry.util.genai.utils import ContentCapturingMode
from opentelemetry.util.types import AttributeValue

_GEN_AI_USAGE_CACHE_WRITE_INPUT_TOKENS: Final = (
    "gen_ai.usage.cache_write.input_tokens"
)
_GEN_AI_REQUEST_PREVIOUS_RESPONSE_ID: Final = (
    "gen_ai.request.previous_response.id"
)


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
        _operation_name = GenAI.GenAiOperationNameValues.INVOKE_AGENT.value
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

    @property
    def agent_name(self) -> str | None:
        """The agent name provided at construction time."""
        return self._agent_name

    def _get_agent_attributes(self) -> dict[str, AttributeValue]:
        optional_attrs = (
            (GenAI.GEN_AI_AGENT_DESCRIPTION, self.agent_description),
        )
        return {k: v for k, v in optional_attrs if v is not None}

    def _get_request_attributes(self) -> dict[str, AttributeValue]:
        optional_attrs = (
            (GenAI.GEN_AI_CONVERSATION_ID, self.conversation_id),
            (GenAI.GEN_AI_DATA_SOURCE_ID, self.data_source_id),
            (GenAI.GEN_AI_OUTPUT_TYPE, self.output_type),
            (GenAI.GEN_AI_REQUEST_TEMPERATURE, self.temperature),
            (GenAI.GEN_AI_REQUEST_TOP_P, self.top_p),
            (GenAI.GEN_AI_REQUEST_FREQUENCY_PENALTY, self.frequency_penalty),
            (GenAI.GEN_AI_REQUEST_PRESENCE_PENALTY, self.presence_penalty),
            (GenAI.GEN_AI_REQUEST_MAX_TOKENS, self.max_tokens),
            (GenAI.GEN_AI_REQUEST_STOP_SEQUENCES, self.stop_sequences),
            (GenAI.GEN_AI_REQUEST_SEED, self.seed),
            (GenAI.GEN_AI_REQUEST_CHOICE_COUNT, self.choice_count),
        )
        return {k: v for k, v in optional_attrs if v is not None}

    def _get_response_attributes(self) -> dict[str, AttributeValue]:
        if self.finish_reasons:
            return {GenAI.GEN_AI_RESPONSE_FINISH_REASONS: self.finish_reasons}
        return {}

    def _get_usage_attributes(self) -> dict[str, AttributeValue]:
        optional_attrs = (
            (GenAI.GEN_AI_USAGE_INPUT_TOKENS, self.input_tokens),
            (GenAI.GEN_AI_USAGE_OUTPUT_TOKENS, self.output_tokens),
        )
        return {k: v for k, v in optional_attrs if v is not None}

    def _get_content_attributes_for_span(self) -> dict[str, AttributeValue]:
        return get_content_attributes(
            input_messages=self.input_messages,
            output_messages=self.output_messages,
            system_instruction=self.system_instruction,
            tool_definitions=self.tool_definitions,
            for_span=True,
            content_capturing_mode=self._content_capturing_mode,
        )

    def _apply_finish(self, error: Error | None = None) -> None:
        if error is not None:
            self._apply_error_attributes(error)

        attributes: dict[str, AttributeValue] = {}
        attributes.update(self._get_agent_attributes())
        attributes.update(self._get_request_attributes())
        attributes.update(self._get_response_attributes())
        attributes.update(self._get_usage_attributes())
        attributes.update(self._get_content_attributes_for_span())
        attributes.update(self.attributes)
        self.span.set_attributes(attributes)
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
        self._start(
            self._spans.invoke_agent(
                self._span_name,
                operation_name=self._operation_name,
                agent_name=self._agent_name,
                request_model=self._request_model,
            )
        )

    def _get_start_attributes(self) -> dict[str, AttributeValue]:
        optional_attrs = (
            (GenAI.GEN_AI_REQUEST_MODEL, self._request_model),
            (GenAI.GEN_AI_AGENT_NAME, self._agent_name),
        )
        return {
            GenAI.GEN_AI_OPERATION_NAME: self._operation_name,
            **{k: v for k, v in optional_attrs if v is not None},
        }

    def _record_metrics(self) -> None:
        duration_seconds = max(
            timeit.default_timer() - self._monotonic_start_s,
            0.0,
        )
        self._metrics.invoke_agent_duration(
            duration_seconds,
            error_type=self._metric_error_type,
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

        self._start(
            self._spans.invoke_agent_client(
                self._span_name,
                operation_name=self._operation_name,
                provider_name=self._provider,
                agent_name=self._agent_name,
                request_model=self._request_model,
                server_address=self._server_address,
                server_port=self._server_port,
            )
        )

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

    def _get_start_attributes(self) -> dict[str, AttributeValue]:
        optional_attrs = (
            (GenAI.GEN_AI_REQUEST_MODEL, self._request_model),
            (GenAI.GEN_AI_AGENT_NAME, self._agent_name),
            (server_attributes.SERVER_ADDRESS, self._server_address),
            (server_attributes.SERVER_PORT, self._server_port),
            (GenAI.GEN_AI_PROVIDER_NAME, self._provider),
        )
        return {
            GenAI.GEN_AI_OPERATION_NAME: self._operation_name,
            **{k: v for k, v in optional_attrs if v is not None},
        }

    def _get_agent_attributes(self) -> dict[str, AttributeValue]:
        optional_attrs = (
            (GenAI.GEN_AI_AGENT_ID, self.agent_id),
            (GenAI.GEN_AI_AGENT_DESCRIPTION, self.agent_description),
            (GenAI.GEN_AI_AGENT_VERSION, self.agent_version),
        )
        return {k: v for k, v in optional_attrs if v is not None}

    def _get_request_attributes(self) -> dict[str, AttributeValue]:
        attrs = super()._get_request_attributes()
        if self.previous_response_id is not None:
            attrs[_GEN_AI_REQUEST_PREVIOUS_RESPONSE_ID] = (
                self.previous_response_id
            )
        return attrs

    def _get_usage_attributes(self) -> dict[str, AttributeValue]:
        attrs = super()._get_usage_attributes()
        if self.cache_write_input_tokens is not None:
            attrs[_GEN_AI_USAGE_CACHE_WRITE_INPUT_TOKENS] = (
                self.cache_write_input_tokens
            )
        if self.cache_read_input_tokens is not None:
            attrs[GenAI.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS] = (
                self.cache_read_input_tokens
            )
        return attrs

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
            error_type=self._metric_error_type,
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
