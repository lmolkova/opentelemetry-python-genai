# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Conformance scenario: anthropic streaming chat (inference)."""

from anthropic import Anthropic

client = Anthropic()
with client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Say hello in one word.",
        }
    ],
    stream=True,
) as stream:
    for _ in stream:
        pass
