# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from typing import cast

from opentelemetry._logs import Logger, LogRecord
from opentelemetry.context import Context
from opentelemetry.util.types import AnyValue


class GenAIEvent:
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

    def emit(self) -> None:
        self._logger.emit(self._log_record)


__all__ = ["GenAIEvent"]
