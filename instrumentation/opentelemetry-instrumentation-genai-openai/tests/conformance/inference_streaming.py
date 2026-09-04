# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Conformance scenario: openai streaming chat completion (inference)."""

from openai import OpenAI

stream = OpenAI().chat.completions.create(
    messages=[{"role": "user", "content": "Say this is a test"}],
    model="gpt-4",
    stream=True,
    stream_options={"include_usage": True},
)
for _ in stream:
    pass
