# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit
from collections.abc import Mapping, Sequence
from typing import Any

from opentelemetry._logs import Logger
from opentelemetry.semconv.attributes import server_attributes
from opentelemetry.util.genai._invocation import Error, GenAIInvocation
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import GenAiOperationName
from opentelemetry.util.genai.semconv.gen_ai import attributes as Attr
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import _Spans
from opentelemetry.util.genai.utils import (
    ContentCapturingMode,
    gen_ai_json_dumps,
)
from opentelemetry.util.types import AttributeValue


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
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            operation_name=_operation_name,
            span_name=f"{_operation_name} {data_source_id}"
            if data_source_id
            else _operation_name,
            content_capturing_mode=content_capturing_mode,
        )
        self._data_source_id: str | None = data_source_id
        self._provider: str | None = provider
        self._request_model: str | None = request_model
        self._server_address: str | None = server_address
        self._server_port: int | None = server_port
        self.top_k: int | None = None
        self.query_text: str | None = None
        self.documents: Sequence[Mapping[str, Any]] | None = None
        self._start(
            self._spans.retrieval(
                self._span_name,
                operation_name=self._operation_name,
                data_source_id=self._data_source_id,
                provider_name=self._provider,
                request_model=self._request_model,
                server_address=self._server_address,
                server_port=self._server_port,
            )
        )

    def _get_start_attributes(self) -> dict[str, AttributeValue]:
        """Return sampling-relevant attributes available at span creation time."""
        optional_attrs: tuple[tuple[str, AttributeValue | None], ...] = (
            (Attr.GEN_AI_DATA_SOURCE_ID, self._data_source_id),
            (Attr.GEN_AI_PROVIDER_NAME, self._provider),
            (Attr.GEN_AI_REQUEST_MODEL, self._request_model),
            (server_attributes.SERVER_ADDRESS, self._server_address),
            (server_attributes.SERVER_PORT, self._server_port),
        )
        return {
            Attr.GEN_AI_OPERATION_NAME: self._operation_name,
            **{k: v for k, v in optional_attrs if v is not None},
        }

    def _get_content_attributes_for_span(self) -> dict[str, AttributeValue]:
        if (
            not self.span.is_recording()
            or not self._should_capture_content_on_span
        ):
            return {}
        optional_attrs: tuple[tuple[str, AttributeValue | None], ...] = (
            (Attr.GEN_AI_RETRIEVAL_QUERY_TEXT, self.query_text),
            (
                Attr.GEN_AI_RETRIEVAL_DOCUMENTS,
                gen_ai_json_dumps(self.documents)
                if self.documents is not None
                else None,
            ),
        )
        return {k: v for k, v in optional_attrs if v is not None}

    def _apply_finish(self, error: Error | None = None) -> None:
        if error is not None:
            self._apply_error_attributes(error)
        attributes: dict[str, AttributeValue] = {}
        if self.top_k is not None:
            attributes[Attr.GEN_AI_RETRIEVAL_TOP_K] = int(self.top_k)
        attributes.update(self._get_content_attributes_for_span())
        attributes.update(self.attributes)
        self.span.set_attributes(attributes)
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
