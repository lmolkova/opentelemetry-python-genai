# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Mapping
from contextlib import AbstractContextManager
from enum import Enum
from types import TracebackType
from typing import cast

from typing_extensions import Self

from opentelemetry.semconv.attributes import error_attributes
from opentelemetry.trace import Span, Status, StatusCode, use_span
from opentelemetry.util.genai.utils import fq_exception_type, gen_ai_json_dumps
from opentelemetry.util.types import AttributeValue


class _Span:
    def __init__(self, span: Span) -> None:
        self._span = span
        self._scope: AbstractContextManager[Span] | None = None
        self._ended = False

    @property
    def span(self) -> Span:
        return self._span

    def __enter__(self) -> Self:
        self._scope = use_span(
            self._span,
            end_on_exit=False,
            record_exception=False,
            set_status_on_exception=False,
        )
        self._scope.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if exc_value is not None:
                self.set_error(exc_value)
        finally:
            if self._scope is not None:
                self._scope.__exit__(None, None, None)
                self._scope = None
            self.end()

    def set_attributes(self, attributes: Mapping[str, AttributeValue]) -> None:
        for name, value in attributes.items():
            self._span.set_attribute(name, value)

    def _set_attribute(
        self, name: str, value: AttributeValue | Enum | None
    ) -> None:
        if value is None:
            return
        if isinstance(value, Enum):
            value = cast("AttributeValue", value.value)
        self._span.set_attribute(name, value)

    def _set_json_attribute(self, name: str, value: object | None) -> None:
        if value is None:
            return
        if isinstance(value, (bool, str, bytes, int, float)):
            self._span.set_attribute(name, value)
            return
        self._span.set_attribute(name, gen_ai_json_dumps(value))

    def set_error(self, error: BaseException, /) -> None:
        self._span.record_exception(error)
        self.set_error_details(fq_exception_type(error), str(error))

    def set_error_details(
        self,
        error_type: str,
        error_message: str | None = None,
        /,
    ) -> None:
        self._span.set_status(Status(StatusCode.ERROR, error_message))
        self._span.set_attribute(error_attributes.ERROR_TYPE, error_type)

    def end(self) -> None:
        if self._ended:
            return
        self._ended = True
        self._span.end()


__all__ = ["_Span"]
