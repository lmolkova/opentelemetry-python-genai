# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import timeit
from contextlib import AbstractContextManager
from contextvars import Token
from types import TracebackType
from typing import Any, TypeAlias, cast

from typing_extensions import Self

from opentelemetry.context import Context, attach, detach
from opentelemetry.trace import Span
from opentelemetry.util.genai.types import (
    Error,
)
from opentelemetry.util.genai.utils import (
    ContentCapturingMode,
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

    attributes: dict[str, AttributeValue]
    metric_attributes: dict[str, AttributeValue]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._context_token: ContextToken | None = None
        self._finished: bool = False

    @property
    def span(self) -> Span:
        """The underlying span.

        .. deprecated:: 1.3b0
            Use :attr:`context` instead.
        """
        return cast(Any, super()).span

    @property
    def context(self) -> Context:
        """The OpenTelemetry Context containing this invocation's span."""
        return cast(Any, super()).context

    @property
    def should_capture_content(self) -> bool:
        """Return True when message content should be captured for this invocation."""
        return cast(Any, super()).should_capture_content

    def _get_metric_attributes(self) -> dict[str, AttributeValue]:
        if hasattr(super(), "_get_metric_attributes"):
            return cast(Any, super())._get_metric_attributes()
        return dict(self.metric_attributes)

    def record_stream_chunk(self) -> None:
        """Mark the request as streamed and record one output chunk arriving."""
        if self._finished:
            return
        if hasattr(self, "_request_stream"):
            self._request_stream = True
        if hasattr(self, "_on_stream_chunk"):
            self._on_stream_chunk(timeit.default_timer())

    def start(
        self,
        name: str | None = None,
        *,
        context: Context | None = None,
        start_time: int | None = None,
        _attach_to_context: bool = True,
    ) -> Span:
        span: Span = cast(Any, super()).start(
            name=name, context=context, start_time=start_time
        )
        if _attach_to_context:
            self._context_token = attach(self.context)
        return span

    def finish(
        self,
        *,
        error: Error | BaseException | None = None,
        duration_s: float | None = None,
        end_time: int | None = None,
        content_capturing_mode: ContentCapturingMode | None = None,
        emit_event: bool | None = None,
        context: Context | None = None,
    ) -> None:
        """Apply finish telemetry. Finishes at most once."""
        if self._finished:
            return
        self._finished = True
        context_token, self._context_token = self._context_token, None
        self._on_finish(context=context)
        try:
            cast(Any, super()).finish(
                error=error,
                duration_s=duration_s,
                end_time=end_time,
                content_capturing_mode=content_capturing_mode,
                emit_event=emit_event,
                context=context,
            )
        finally:
            if context_token is not None:
                try:
                    detach(context_token)
                except Exception:  # pylint: disable=broad-except
                    pass

    def _on_finish(self, context: Context | None = None) -> None:
        pass

    def stop(self) -> None:
        """Finalize the invocation successfully and end its span."""
        self.finish()

    def fail(self, error: Error | BaseException) -> None:
        """Fail the invocation and end its span with error status."""
        self.finish(error=error)

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
