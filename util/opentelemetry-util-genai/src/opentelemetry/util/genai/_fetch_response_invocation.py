# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit
from collections.abc import Sequence
from typing import cast

from opentelemetry._logs import Logger
from opentelemetry.util.genai._invocation import (
    Error,
    GenAIInvocation,
)
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import GenAiOperationName
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import (
    FetchResponseSpan,
    _Spans,
)
from opentelemetry.util.genai.types import (
    ErrorTypeResolver,
    MessagePart,
    OutputMessage,
    SystemInstructionPart,
    ToolDefinition,
)
from opentelemetry.util.genai.utils import ContentCapturingMode


class FetchResponseInvocation(GenAIInvocation):
    """Represents a single fetch of a previously generated model response.

    Use handler.fetch_response() rather than constructing this directly.

    Reference: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md#fetch-response

    The operation performs no inference and consumes no tokens: it returns a
    response produced by an earlier operation. Any token counts carried on the
    fetched response describe that original generation and MUST NOT be reported
    here, so this invocation deliberately exposes no token usage fields.

    Semantic convention attributes for fetch response spans:
    - gen_ai.operation.name: "fetch_response" (Required)
    - gen_ai.provider.name: Provider name (Required)
    - gen_ai.response.id: Identifier of the response being fetched (Required)
    - error.type: Error type when the fetch itself failed (Conditionally Required)
    - gen_ai.request.stream_cursor: Set from ``stream_cursor`` when the fetch
      resumes a streamed response from a prior position (Conditionally Required)
    - gen_ai.request.stream: Set to true when the fetched response is streamed
      (Conditionally Required)
    - server.port: Set only when ``server_port`` is provided (Conditionally Required)
    - gen_ai.response.finish_reasons: Outcome of the original generation
      (Recommended)
    - gen_ai.response.model: Set from ``response_model_name`` (Recommended)
    - gen_ai.response.status: Lifecycle status of the fetched response
      (Recommended)
    - server.address: Set only when ``server_address`` is provided (Recommended)
    - gen_ai.output.messages, gen_ai.system_instructions,
      gen_ai.tool.definitions: content carried on the fetched response,
      recorded on the span only when content capturing is enabled (Opt-In).
      A fetched response does not carry the original input messages, so
      gen_ai.input.messages is never set.

    A fetched response whose *original* generation failed is not a failure of
    the fetch: report it through ``response_status`` and ``finish_reasons`` and
    still call ``stop()``. Only call ``fail()`` when the fetch call itself
    failed.
    """

    def __init__(
        self,
        spans: _Spans,
        metrics: _Metrics,
        logger: Logger,
        completion_hook: CompletionHook,
        provider: str,
        *,
        response_id: str,
        request_stream: bool | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        error_type_resolver: ErrorTypeResolver | None = None,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        """Use handler.fetch_response() rather than calling this directly."""
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            operation_name=GenAiOperationName.FETCH_RESPONSE.value,
            # The response identifier is high cardinality, so semconv keeps it
            # out of the span name.
            span_name=GenAiOperationName.FETCH_RESPONSE.value,
            error_type_resolver=error_type_resolver,
            content_capturing_mode=content_capturing_mode,
        )
        self._provider: str = provider
        self._response_id: str = response_id
        self._request_stream = request_stream
        self._ttfc_seconds: float | None = None
        self._stream_last_chunk_at: float | None = None
        self._server_address: str | None = server_address
        self._server_port: int | None = server_port
        self.response_model_name: str | None = None
        self.response_status: str | None = None
        self.finish_reasons: list[str] | None = None
        self.stream_cursor: str | None = None
        self.output_messages: list[OutputMessage] = []
        self.system_instruction: (
            list[SystemInstructionPart] | list[MessagePart]
        ) = []
        """System instructions for the model. Passing ``MessagePart`` is deprecated; use ``SystemInstructionPart``."""
        self.tool_definitions: list[ToolDefinition] | None = None
        self._fetch_response_span: FetchResponseSpan = (
            self._spans.fetch_response(
                self._span_name,
                operation_name=self._operation_name,
                provider_name=self._provider,
                response_id=self._response_id,
                request_stream=self._request_stream,
                server_address=self._server_address,
                server_port=self._server_port,
            )
        )
        self._start(self._fetch_response_span)

    @property
    def response_id(self) -> str:
        """The identifier of the response being fetched."""
        return self._response_id

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
                response_model=self.response_model_name,
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
            response_model=self.response_model_name,
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )

    def _apply_finish(self, error: Error | None = None) -> None:
        if error is not None:
            self._fetch_response_span.set_error_details(
                error.type, error.message
            )
            self._error_type = error.type
        span = self._fetch_response_span
        span.set_request_stream_cursor(self.stream_cursor)
        span.set_response_finish_reasons(self.finish_reasons or None)
        span.set_response_model(self.response_model_name)
        span.set_response_status(self.response_status)
        span.set_output_messages(
            (self.output_messages or None)
            if self._should_capture_content_on_span
            else None
        )
        span.set_system_instructions(
            cast(
                "Sequence[SystemInstructionPart] | None",
                (self.system_instruction or None)
                if self._should_capture_content_on_span
                else None,
            )
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
            response_model=self.response_model_name,
            provider_name=self._provider,
            error_type=self._error_type,
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )
        self._call_completion_hook(
            outputs=self.output_messages,
            system_instruction=self.system_instruction,
            tool_definitions=self.tool_definitions,
        )
