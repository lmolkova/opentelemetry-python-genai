# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit
from collections.abc import Mapping, Sequence
from typing import Any

from opentelemetry._logs import Logger
from opentelemetry.util.genai._attribute import _Attribute
from opentelemetry.util.genai._invocation import Error, GenAIInvocation
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import (
    GenAiOperationName,
    RetrievalAttributes,
)
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import (
    RetrievalSpan,
    _Spans,
)
from opentelemetry.util.genai.utils import ContentCapturingMode


class RetrievalInvocation(GenAIInvocation):
    """Represents a single retrieval invocation (retrieval span).

    Use handler.retrieval() rather than constructing this directly.

    Reference: https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md#retrievals

    Semantic convention attributes for retrieval spans:
    - gen_ai.operation.name: "retrieval" (Required)
    - error.type: Error type if operation failed (Conditionally Required)
    - gen_ai.data_source.id: Data source identifier (Conditionally Required, when applicable)
    - gen_ai.provider.name: Provider name (Conditionally Required, when applicable)
    - gen_ai.request.model: Model name if applicable (Conditionally Required, if available)
    - server.port: Server port (Conditionally Required, if server.address is set)
    - gen_ai.retrieval.top_k: Maximum number of documents to return (Recommended)
    - server.address: Server address (Recommended)
    - gen_ai.retrieval.documents: Retrieved documents (Opt-In, may contain sensitive data)
    - gen_ai.retrieval.query.text: Query text (Opt-In, may contain sensitive data)
    """

    _data_source_id = _Attribute[str | None]("data_source_id")
    _provider = _Attribute[str | None]("provider_name")
    _request_model = _Attribute[str | None]("request_model")
    _server_address = _Attribute[str | None]("server_address")
    _server_port = _Attribute[int | None]("server_port")
    top_k = _Attribute[int | None]("retrieval_top_k")
    query_text = _Attribute[str | None]("retrieval_query_text")
    documents = _Attribute[Sequence[Mapping[str, Any]] | None](
        "retrieval_documents"
    )

    def __init__(
        self,
        spans: _Spans,
        metrics: _Metrics,
        logger: Logger,
        completion_hook: CompletionHook,
        *,
        data_source_id: str | None = None,
        provider: str | None = None,
        request_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        """Use handler.retrieval() instead of calling this directly."""
        _operation_name = GenAiOperationName.RETRIEVAL.value
        self._semconv_attributes = RetrievalAttributes(
            operation_name=_operation_name,
            data_source_id=data_source_id,
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
            span_name=f"{_operation_name} {data_source_id}"
            if data_source_id
            else _operation_name,
            content_capturing_mode=content_capturing_mode,
        )
        self._retrieval_span: RetrievalSpan = self._spans.retrieval(
            self._span_name,
        )
        self._start(self._retrieval_span)

    def _apply_finish(self, error: Error | None = None) -> None:
        attributes = self._semconv_attributes
        if error is not None:
            self._retrieval_span.set_error_details(error.type, error.message)
            attributes.error_type = error.type
        self._retrieval_span.apply(attributes)
        if self.span.is_recording() and self._should_capture_content_on_span:
            self._retrieval_span.set_retrieval_query_text(
                attributes.retrieval_query_text
            )
            self._retrieval_span.set_retrieval_documents(
                attributes.retrieval_documents
            )
        self._retrieval_span.set_attributes(self.attributes)
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
