# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Conformance scenario: anthropic chat with tool calls."""

from anthropic import Anthropic

client = Anthropic()
client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=256,
    messages=[
        {
            "role": "user",
            "content": "What is the weather in SF?",
        }
    ],
    tools=[
        {
            "name": "get_weather",
            "description": "Get weather by city",
            "input_schema": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        }
    ],
    tool_choice={"type": "tool", "name": "get_weather"},
)
