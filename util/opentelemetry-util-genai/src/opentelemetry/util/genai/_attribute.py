# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Generic, TypeVar, cast, overload

AttributeT = TypeVar("AttributeT")


class _Attribute(Generic[AttributeT]):
    def __init__(self, name: str | None = None) -> None:
        self._name = name

    def __set_name__(self, owner: type[object], name: str) -> None:
        if self._name is None:
            self._name = name

    @overload
    def __get__(
        self, instance: None, owner: type[object]
    ) -> _Attribute[AttributeT]: ...

    @overload
    def __get__(self, instance: object, owner: type[object]) -> AttributeT: ...

    def __get__(
        self, instance: object | None, owner: type[object]
    ) -> AttributeT | _Attribute[AttributeT]:
        if instance is None:
            return self
        attributes = getattr(instance, "_semconv_attributes")
        return cast("AttributeT", getattr(attributes, cast("str", self._name)))

    def __set__(self, instance: object, value: AttributeT) -> None:
        attributes = getattr(instance, "_semconv_attributes")
        setattr(attributes, cast("str", self._name), value)
