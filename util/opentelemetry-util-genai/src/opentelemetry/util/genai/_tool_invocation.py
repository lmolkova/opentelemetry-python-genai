# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit

from opentelemetry._logs import Logger
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
from opentelemetry.util.types import AnyValue, AttributeValue


def _any_value_to_attribute_value(value: AnyValue) -> AttributeValue | None:
    """Serialize an AnyValue to an AttributeValue for OTel span attributes."""
    if value is None:
        return None
    if isinstance(value, (bool, str, bytes, int, float)):
        return value
    try:
        return gen_ai_json_dumps(value)
    except (TypeError, ValueError):
        return str(value)


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
        super().__init__(
            spans,
            metrics,
            logger,
            completion_hook,
            operation_name=_operation_name,
            span_name=f"{_operation_name} {name}" if name else _operation_name,
            content_capturing_mode=content_capturing_mode,
        )
        self._name: str = name
        self.tool_result: AnyValue | None = None
        # Since arguments and tool_result can be expensive to serialize,
        # it's recommended to check the content capture flag in the
        # instrumentation library before assigning these attributes
        # to the invocation.
        self.arguments: AnyValue | None = None
        self.tool_call_id: str | None = tool_call_id
        self.tool_description: str | None = tool_description
        self._tool_type: str | None = tool_type
        self._agent_name: str | None = agent_name
        self._start(
            self._spans.execute_tool(
                self._span_name,
                operation_name=self._operation_name,
                tool_name=self._name,
                tool_type=self._tool_type,
            )
        )

    @property
    def should_capture_content_on_span(self) -> bool:
        """Returns whether content capture is enabled on spans.

        .. deprecated:: 1.2b0
            Use :attr:`should_capture_content` instead.
        """
        return self._should_capture_content_on_span

    def _get_start_attributes(self) -> dict[str, AttributeValue]:
        """Return sampling-relevant attributes available at span creation time."""
        optional_attrs = (
            (Attr.GEN_AI_TOOL_NAME, self._name),
            (Attr.GEN_AI_TOOL_TYPE, self._tool_type),
        )
        return {
            Attr.GEN_AI_OPERATION_NAME: self._operation_name,
            **{k: v for k, v in optional_attrs if v is not None},
        }

    def _apply_finish(self, error: Error | None = None) -> None:
        if error is not None:
            self._apply_error_attributes(error)
        capture_content_on_span = self._should_capture_content_on_span
        optional_attrs = (
            (Attr.GEN_AI_TOOL_CALL_ID, self.tool_call_id),
            (Attr.GEN_AI_TOOL_DESCRIPTION, self.tool_description),
            (Attr.GEN_AI_AGENT_NAME, self._agent_name),
            (
                Attr.GEN_AI_TOOL_CALL_ARGUMENTS,
                _any_value_to_attribute_value(self.arguments)
                if capture_content_on_span and self.arguments is not None
                else None,
            ),
            (
                Attr.GEN_AI_TOOL_CALL_RESULT,
                _any_value_to_attribute_value(self.tool_result)
                if capture_content_on_span and self.tool_result is not None
                else None,
            ),
        )
        attributes: dict[str, AttributeValue] = {
            k: v for k, v in optional_attrs if v is not None
        }
        attributes.update(self.attributes)
        self.span.set_attributes(attributes)
        self._record_metrics()

    def _record_metrics(self) -> None:
        duration_seconds = max(
            timeit.default_timer() - self._monotonic_start_s,
            0.0,
        )
        self._metrics.execute_tool_duration(
            duration_seconds,
            tool_name=self._name,
            error_type=self._metric_error_type,
            tool_type=self._tool_type,
            agent_name=self._agent_name,
            additional_attributes=self.metric_attributes,
            context=self._span_context,
        )
