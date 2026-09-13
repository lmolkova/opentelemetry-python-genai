# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import cast

from opentelemetry._logs import Logger, LogRecord
from opentelemetry.context import Context
from opentelemetry.util.types import AnyValue


def _structured_value(value: object) -> AnyValue:
    if is_dataclass(value) and not isinstance(value, type):
        return _structured_value(asdict(value))
    if isinstance(value, Mapping):
        mapping = cast("Mapping[str, object]", value)
        return {name: _structured_value(item) for name, item in mapping.items()}
    if isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray)
    ):
        sequence = cast("Sequence[object]", value)
        return [_structured_value(item) for item in sequence]
    return cast("AnyValue", value)


class _Event:
    def __init__(
        self,
        logger: Logger,
        event_name: str,
        *,
        context: Context | None = None,
    ) -> None:
        self._logger = logger
        self._attributes: dict[str, AnyValue] = {}
        self._log_record = LogRecord(
            event_name=event_name,
            context=context,
            attributes=self._attributes,
        )

    @property
    def log_record(self) -> LogRecord:
        return self._log_record

    def set_attributes(self, attributes: Mapping[str, AnyValue]) -> None:
        self._attributes.update(attributes)

    def _set_attribute(self, name: str, value: AnyValue | Enum | None) -> None:
        if value is None:
            return
        if isinstance(value, Enum):
            value = cast("AnyValue", value.value)
        self._attributes[name] = value

    def _set_structured_attribute(
        self, name: str, value: object | None
    ) -> None:
        if value is None:
            return
        self._attributes[name] = _structured_value(value)

    def emit(self) -> None:
        self._logger.emit(self._log_record)


__all__ = ["_Event"]
