# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit

from opentelemetry._logs import Logger
from opentelemetry.util.genai._attribute import _Attribute
from opentelemetry.util.genai._invocation import Error, GenAIInvocation
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import (
    EmbeddingsAttributes,
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

    _provider = _Attribute[str]("provider_name")
    _request_model = _Attribute[str | None]("request_model")
    _server_address = _Attribute[str | None]("server_address")
    _server_port = _Attribute[int | None]("server_port")
    encoding_formats = _Attribute[list[str] | None]("request_encoding_formats")
    input_tokens = _Attribute[int | None]("usage_input_tokens")
    dimension_count = _Attribute[int | None]("embeddings_dimension_count")
    response_model_name = _Attribute[str | None]("response_model")

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
        self._semconv_attributes = EmbeddingsAttributes(
            operation_name=_operation_name,
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
            span_name=f"{_operation_name} {request_model}"
            if request_model
            else _operation_name,
            content_capturing_mode=content_capturing_mode,
        )
        self._embedding_span: EmbeddingsSpan = self._spans.embeddings(
            self._span_name,
            operation_name=self._semconv_attributes.operation_name,
            provider_name=self._semconv_attributes.provider_name,
            request_model=self._semconv_attributes.request_model,
            server_address=self._semconv_attributes.server_address,
            server_port=self._semconv_attributes.server_port,
        )
        self._start(self._embedding_span)

    def _apply_finish(self, error: Error | None = None) -> None:
        attributes = self._semconv_attributes
        if error is not None:
            self._embedding_span.set_error_details(error.type, error.message)
            attributes.error_type = error.type
        self._embedding_span.apply(attributes)
        self._embedding_span.set_attributes(self.attributes)
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
