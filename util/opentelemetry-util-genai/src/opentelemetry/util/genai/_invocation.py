# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit
from abc import abstractmethod
from contextlib import AbstractContextManager
from contextvars import Token
from types import TracebackType
from typing import TypeAlias, cast

from typing_extensions import Self

from opentelemetry._logs import Logger, LogRecord
from opentelemetry.context import Context, attach, detach
from opentelemetry.trace import INVALID_SPAN as _INVALID_SPAN
from opentelemetry.trace import Span, set_span_in_context
from opentelemetry.util.genai.completion_hook import (
    CompletionHook,
    _NoOpCompletionHook,
)
from opentelemetry.util.genai.semconv._span import _Span
from opentelemetry.util.genai.semconv.gen_ai._events import _Events
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import _Spans
from opentelemetry.util.genai.types import (
    Error,
    ErrorTypeResolver,
    InputMessage,
    MessagePart,
    OutputMessage,
    SystemInstructionPart,
    ToolDefinition,
)
from opentelemetry.util.genai.utils import (
    ContentCapturingMode,
    get_content_capturing_mode,
)
from opentelemetry.util.types import AttributeValue

ContextToken: TypeAlias = Token[Context]


class GenAIInvocation(AbstractContextManager["GenAIInvocation"]):
    """
    Base class for all GenAI invocation types. Manages the lifecycle of a single
    GenAI operation (LLM call, embedding, tool execution, workflow, etc.).

    Use the factory methods on TelemetryHandler (inference, embedding,
    workflow, tool) rather than constructing invocations directly.
    """

    def __init__(
        self,
        # Individual components instead of TelemetryHandler to avoid a circular
        # import between handler.py and the invocation modules.
        spans: _Spans,
        metrics: _Metrics,
        logger: Logger,
        completion_hook: CompletionHook,
        span_name: str,
        attributes: dict[str, AttributeValue] | None = None,
        metric_attributes: dict[str, AttributeValue] | None = None,
        error_type_resolver: ErrorTypeResolver | None = None,
        *,
        content_capturing_mode: ContentCapturingMode | None = None,
    ) -> None:
        self._spans = spans
        self._metrics: _Metrics = metrics
        self._events = _Events(logger)
        self._completion_hook = completion_hook
        self._error_type_resolver = error_type_resolver
        self._content_capturing_mode: ContentCapturingMode = (
            get_content_capturing_mode()
            if content_capturing_mode is None
            else content_capturing_mode
        )
        self.attributes: dict[str, AttributeValue] = (
            {} if attributes is None else attributes
        )
        """Additional attributes to set on spans and/or events. Not set on metrics."""
        self.metric_attributes: dict[str, AttributeValue] = (
            {} if metric_attributes is None else metric_attributes
        )
        """Additional attributes to set on metrics. Must be low cardinality. Not set on spans or events."""
        self.span: Span = _INVALID_SPAN
        self._span_context: Context
        self._span_name: str = span_name
        self._context_token: ContextToken | None = None
        self._monotonic_start_s: float

    @property
    def should_capture_content(self) -> bool:
        """Return True when message content should be captured for this invocation."""
        return self._content_capturing_mode in (
            ContentCapturingMode.SPAN_ONLY,
            ContentCapturingMode.EVENT_ONLY,
            ContentCapturingMode.SPAN_AND_EVENT,
        ) or not isinstance(self._completion_hook, _NoOpCompletionHook)

    @property
    def _should_capture_content_on_span(self) -> bool:
        return self._content_capturing_mode in (
            ContentCapturingMode.SPAN_ONLY,
            ContentCapturingMode.SPAN_AND_EVENT,
        )

    @property
    def _should_capture_content_on_event(self) -> bool:
        return self._content_capturing_mode in (
            ContentCapturingMode.EVENT_ONLY,
            ContentCapturingMode.SPAN_AND_EVENT,
        )

    def _start(self, span: _Span) -> None:
        self.span = span.span
        self._span_context = set_span_in_context(self.span)
        self._monotonic_start_s = timeit.default_timer()
        self._context_token = attach(self._span_context)

    def _call_completion_hook(
        self,
        *,
        inputs: list[InputMessage] | None = None,
        outputs: list[OutputMessage] | None = None,
        system_instruction: list[SystemInstructionPart]
        | list[MessagePart]
        | None = None,
        tool_definitions: list[ToolDefinition] | None = None,
        log_record: LogRecord | None = None,
    ) -> None:
        """Invoke the completion hook with the invocation's content.

        Subclasses pass whichever content fields they carry; the wrapper substitutes []
        for unspecified list fields
        """
        self._completion_hook.on_completion(
            inputs=inputs or [],
            outputs=outputs or [],
            system_instruction=cast(
                "list[MessagePart]", system_instruction or []
            ),
            tool_definitions=tool_definitions,
            span=self.span,
            log_record=log_record,
        )

    @abstractmethod
    def _apply_finish(self, error: Error | None = None) -> None:
        """Apply finish telemetry (attributes, metrics, events)."""

    def _finish(self, error: Error | None = None) -> None:
        """Apply finish telemetry and end the span. Finishes at most once."""
        if self._context_token is None:
            return
        # Clear up front so a nested or repeated finish is a no-op even if
        # _apply_finish raises.
        context_token, self._context_token = self._context_token, None
        try:
            self._apply_finish(error)
        finally:
            try:
                detach(context_token)
            except Exception:  # pylint: disable=broad-except
                pass
            self.span.end()

    def stop(self) -> None:
        """Finalize the invocation successfully and end its span."""
        self._finish()

    def fail(self, error: Error | BaseException) -> None:
        """Fail the invocation and end its span with error status."""
        if isinstance(error, BaseException):
            error = Error.from_exception(error, self._error_type_resolver)
        self._finish(error)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_value is not None:
            self.fail(exc_value)
        else:
            self.stop()
