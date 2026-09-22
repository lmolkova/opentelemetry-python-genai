# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Context helpers for GenAI inference attributes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from opentelemetry.context import Context, get_value, set_value
from opentelemetry.util.types import AttributeValue

INFERENCE_CONTEXT_KEY: Final[str] = "opentelemetry.genai.inference_context"
_INFERENCE_CONTEXT_KEY = INFERENCE_CONTEXT_KEY


@dataclass
class InferenceContextData:
    """Typed data passed from inner inference invocations to the outer invocation."""

    provider: str | None = None
    request_model: str | None = None
    response_model: str | None = None
    server_address: str | None = None
    server_port: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    request_stream: bool | None = None
    ttfc_seconds: float | None = None
    attributes: dict[str, AttributeValue] = field(
        default_factory=dict[str, AttributeValue]
    )
    metric_attributes: dict[str, AttributeValue] = field(
        default_factory=dict[str, AttributeValue]
    )


__all__ = [
    "INFERENCE_CONTEXT_KEY",
    "InferenceContextData",
    "get_inference_context_data",
    "set_inference_context_data",
]


def set_inference_context_data(
    data: InferenceContextData,
    context: Context | None = None,
) -> Context:
    """Return a Context with the given inference context data attached.

    Args:
        data: The mutable inference context data object.
        context: The context to attach to. Defaults to the current context.

    Returns:
        A new Context containing the inference context data.
    """
    return set_value(_INFERENCE_CONTEXT_KEY, data, context=context)


def get_inference_context_data(
    context: Context | None = None,
) -> InferenceContextData | None:
    """Return the active inference context data from context, if any.

    Args:
        context: The context to inspect. Defaults to the current context.

    Returns:
        The active inference context data, or None if not set.
    """
    data = get_value(_INFERENCE_CONTEXT_KEY, context=context)
    if isinstance(data, InferenceContextData):
        return data
    return None
