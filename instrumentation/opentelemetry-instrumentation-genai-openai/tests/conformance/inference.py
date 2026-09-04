# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Conformance scenario: openai-v2 chat completion (inference)."""

from openai import OpenAI

OpenAI().chat.completions.create(
    messages=[{"role": "user", "content": "Say this is a test"}],
    model="gpt-4o-mini",
    stream=False,
)
