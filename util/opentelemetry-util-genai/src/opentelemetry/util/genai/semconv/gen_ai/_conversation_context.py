# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
# Code generated from OpenTelemetry GenAI semantic conventions. DO NOT EDIT.

from __future__ import annotations

from opentelemetry.context import (
    Context,
    create_key,
    get_value,
    set_value,
)

_CONVERSATION_ID_KEY = create_key("opentelemetry.util.genai.conversation_id")


def get_ambient_conversation_id(
    context: Context | None = None,
) -> str | None:
    value = get_value(_CONVERSATION_ID_KEY, context=context)
    return value if isinstance(value, str) else None


def with_conversation_id(
    conversation_id: str,
    context: Context | None = None,
) -> Context:
    return set_value(_CONVERSATION_ID_KEY, conversation_id, context=context)


__all__ = [
    "get_ambient_conversation_id",
    "with_conversation_id",
]
