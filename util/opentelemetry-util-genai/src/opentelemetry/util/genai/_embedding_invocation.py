# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit

from opentelemetry._logs import Logger
from opentelemetry.util.genai._invocation import Error, GenAIInvocation
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import (
    GenAiOperationName,
    GenAiTokenType,
)
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import (
    EmbeddingsSpan,
    _Spans,
)
from opentelemetry.util.genai.utils import ContentCapturingMode


class EmbeddingInvocation(GenAIInvocation):
    """Represents a single embedding model invocation.

    Use handler.embedding(provider) rather than constructing this directly.
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
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        """Use handler.embedding(provider) rather than calling this directly."""
        _operation_name = GenAiOperationName.EMBEDDINGS.value
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            operation_name=_operation_name,
            span_name=f"{_operation_name} {request_model}"
            if request_model
            else _operation_name,
            content_capturing_mode=content_capturing_mode,
        )
        # e.g., azure.ai.openai, openai, aws.bedrock
        self._provider: str = provider
        self._request_model: str | None = request_model
        self._server_address: str | None = server_address
        self._server_port: int | None = server_port
        # encoding_formats can be multi-value -> combinational cardinality risk.
        # Keep on spans/events only.
        self.encoding_formats: list[str] | None = None
        self.input_tokens: int | None = None
        self.dimension_count: int | None = None
        self.response_model_name: str | None = None
        self._embedding_span: EmbeddingsSpan = self._spans.embeddings(
            self._span_name,
            operation_name=self._operation_name,
            provider_name=self._provider,
            request_model=self._request_model,
            server_address=self._server_address,
            server_port=self._server_port,
        )
        self._start(self._embedding_span)

    def _apply_finish(self, error: Error | None = None) -> None:
        if error is not None:
            self._embedding_span.set_error_details(error.type, error.message)
            self._error_type = error.type
        self._embedding_span.set_embeddings_dimension_count(
            self.dimension_count
        )
        self._embedding_span.set_request_encoding_formats(
            self.encoding_formats
        )
        self._embedding_span.set_response_model(self.response_model_name)
        self._embedding_span.set_usage_input_tokens(self.input_tokens)
        self._embedding_span.set_attributes(self.attributes)
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
            response_model=self.response_model_name,
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
                response_model=self.response_model_name,
                additional_attributes=self.metric_attributes,
                context=self._span_context,
            )
