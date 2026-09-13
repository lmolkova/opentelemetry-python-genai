# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit

from opentelemetry._logs import Logger
from opentelemetry.util.genai._attribute import _Attribute
from opentelemetry.util.genai._invocation import Error, GenAIInvocation
from opentelemetry.util.genai.completion_hook import CompletionHook
from opentelemetry.util.genai.semconv.gen_ai import (
    ExecuteToolAttributes,
    GenAiOperationName,
)
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import (
    ExecuteToolSpan,
    _Spans,
)
from opentelemetry.util.genai.utils import ContentCapturingMode
from opentelemetry.util.types import AnyValue


class ToolInvocation(GenAIInvocation):
    """Represents a tool call invocation for execute_tool span tracking.

    Not used as a message part — use ToolCallRequestPart for that purpose.

    Use handler.tool(name) rather than constructing this directly.

    Reference: https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md#execute-tool-span

    Semantic convention attributes for execute_tool spans:
    - gen_ai.operation.name: "execute_tool" (Required)
    - gen_ai.tool.name: Name of the tool (Recommended)
    - gen_ai.agent.name: Human-readable name of the agent executing the tool
      (Conditionally Required "When applicable")
    - gen_ai.tool.call.id: Tool call identifier (Recommended if available)
    - gen_ai.tool.type: Type classification - "function", "extension", or "datastore" (Recommended if available)
    - gen_ai.tool.description: Tool description (Recommended if available)
    - gen_ai.tool.call.arguments: Parameters passed to tool (Opt-In, may contain sensitive data)
    - gen_ai.tool.call.result: Result returned by tool (Opt-In, may contain sensitive data)
    - error.type: Error type if operation failed (Conditionally Required)
    """

    _name = _Attribute[str]("tool_name")
    _tool_type = _Attribute[str | None]("tool_type")
    _agent_name = _Attribute[str | None]("agent_name")
    tool_result = _Attribute[AnyValue | None]("tool_call_result")
    arguments = _Attribute[AnyValue | None]("tool_call_arguments")
    tool_call_id = _Attribute[str | None]()
    tool_description = _Attribute[str | None]()

    def __init__(
        self,
        spans: _Spans,
        metrics: _Metrics,
        logger: Logger,
        completion_hook: CompletionHook,
        name: str,
        *,
        tool_type: str | None = None,
        agent_name: str | None = None,
        tool_call_id: str | None = None,
        tool_description: str | None = None,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        """Use handler.tool(name) instead of calling this directly.

        .. deprecated:: 1.2b0
            Passing ``tool_call_id`` or ``tool_description`` to the constructor
            is deprecated. Set ``invocation.tool_call_id`` and
            ``invocation.tool_description`` on the returned invocation instead.
        """
        _operation_name = GenAiOperationName.EXECUTE_TOOL.value
        self._semconv_attributes = ExecuteToolAttributes(
            operation_name=_operation_name,
            tool_name=name,
            tool_type=tool_type,
            agent_name=agent_name,
            tool_call_id=tool_call_id,
            tool_description=tool_description,
        )
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            span_name=f"{_operation_name} {name}" if name else _operation_name,
            content_capturing_mode=content_capturing_mode,
        )
        self._tool_span: ExecuteToolSpan = self._spans.execute_tool(
            self._span_name,
            operation_name=self._semconv_attributes.operation_name,
            tool_name=self._semconv_attributes.tool_name,
            tool_type=self._semconv_attributes.tool_type,
            agent_name=self._semconv_attributes.agent_name,
        )
        self._start(self._tool_span)

    @property
    def should_capture_content_on_span(self) -> bool:
        """Returns whether content capture is enabled on spans.

        .. deprecated:: 1.2b0
            Use :attr:`should_capture_content` instead.
        """
        return self._should_capture_content_on_span

    def _apply_finish(self, error: Error | None = None) -> None:
        attributes = self._semconv_attributes
        if error is not None:
            self._tool_span.set_error_details(error.type, error.message)
            attributes.error_type = error.type
        self._tool_span.apply(attributes)
        if self._should_capture_content_on_span:
            self._tool_span.set_tool_call_arguments(
                attributes.tool_call_arguments
            )
            self._tool_span.set_tool_call_result(attributes.tool_call_result)
        self._tool_span.set_attributes(self.attributes)
        self._record_metrics()

    def _record_metrics(self) -> None:
        duration_seconds = max(
            timeit.default_timer() - self._monotonic_start_s,
            0.0,
        )
        self._metrics.execute_tool_duration(
            duration_seconds,
            self._semconv_attributes,
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )
