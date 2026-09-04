# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Conformance scenario: google-genai tool execution."""

from google.genai import Client


def get_weather(location: str) -> str:
    """Get weather for location"""
    return "sunny"


client = Client()
client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the weather in Boston?",
    config={"tools": [get_weather]},
)
