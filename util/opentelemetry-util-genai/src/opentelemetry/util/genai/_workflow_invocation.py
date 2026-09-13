# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit

from opentelemetry._logs import Logger
from opentelemetry.util.genai._invocation import (
    Error,
    GenAIInvocation,
)
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import GenAiOperationName
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import (
    InvokeWorkflowSpan,
    _Spans,
)
from opentelemetry.util.genai.types import (
    InputMessage,
    OutputMessage,
)
from opentelemetry.util.genai.utils import ContentCapturingMode


class WorkflowInvocation(GenAIInvocation):
    """
    Represents a predetermined sequence of operations (e.g. agent, LLM, tool,
    and retrieval invocations). A workflow groups multiple operations together,
    accepting input(s) and producing final output(s).

    Use handler.workflow(name) rather than constructing this directly.
    """

    def __init__(
        self,
        spans: _Spans,
        metrics: _Metrics,
        logger: Logger,
        completion_hook: CompletionHook,
        name: str | None,
        *,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        """Use handler.workflow(name) rather than calling this directly."""
        _operation_name = GenAiOperationName.INVOKE_WORKFLOW.value
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            operation_name=_operation_name,
            span_name=f"{_operation_name} {name}" if name else _operation_name,
            content_capturing_mode=content_capturing_mode,
        )
        self._name: str | None = name
        self.conversation_id: str | None = None
        self.input_messages: list[InputMessage] = []
        self.output_messages: list[OutputMessage] = []
        self._workflow_span: InvokeWorkflowSpan = self._spans.invoke_workflow(
            self._span_name,
            operation_name=self._operation_name,
            workflow_name=self._name,
        )
        self._start(self._workflow_span)

    def _apply_finish(self, error: Error | None = None) -> None:
        if error is not None:
            self._workflow_span.set_error_details(error.type, error.message)
            self._error_type = error.type
        self._workflow_span.set_conversation_id(self.conversation_id)
        if self._should_capture_content_on_span:
            self._workflow_span.set_input_messages(self.input_messages or None)
            self._workflow_span.set_output_messages(
                self.output_messages or None
            )
        self._workflow_span.set_attributes(self.attributes)
        self._call_completion_hook(
            inputs=self.input_messages,
            outputs=self.output_messages,
        )
        self._record_metrics()

    def _record_metrics(self) -> None:
        duration_seconds = max(
            timeit.default_timer() - self._monotonic_start_s,
            0.0,
        )
        self._metrics.invoke_workflow_duration(
            duration_seconds,
            error_type=self._error_type,
            workflow_name=self._name,
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )
