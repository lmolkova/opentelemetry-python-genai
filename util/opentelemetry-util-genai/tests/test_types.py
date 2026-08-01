# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import asdict, dataclass

import pytest

from opentelemetry.util.genai.types import (
    InputMessage,
    Text,
    ToolCallRequest,
)


def test_message_models_are_keyword_only() -> None:
    with pytest.raises(TypeError):
        Text("hello")


def test_subclass_may_add_required_field() -> None:
    """Producers extend the semconv models by subclassing.

    The semconv message schemas are open (``extra="allow"``), so an
    instrumentation must be able to carry provider-specific fields on a
    standard part. ``kw_only`` is what makes that possible: without it a
    subclass cannot declare a field without a default, because the base
    classes already have defaulted fields.
    """

    @dataclass(kw_only=True)
    class ProviderText(Text):
        signature: str

    part = ProviderText(content="hello", signature="abc")

    assert asdict(part) == {
        "content": "hello",
        "type": "text",
        "signature": "abc",
    }


def test_subclass_is_usable_as_a_message_part() -> None:
    @dataclass(kw_only=True)
    class ProviderToolCall(ToolCallRequest):
        cache_control: str

    part = ProviderToolCall(
        arguments={"a": 1}, name="f", id="call_1", cache_control="ephemeral"
    )
    message = InputMessage(role="user", parts=[part])

    assert isinstance(message.parts[0], ToolCallRequest)
    assert asdict(message)["parts"][0]["cache_control"] == "ephemeral"
