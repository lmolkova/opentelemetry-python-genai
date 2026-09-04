# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Conformance scenario: openai-v2 embeddings."""

from openai import OpenAI

OpenAI().embeddings.create(
    input="The quick brown fox jumps over the lazy dog",
    model="text-embedding-3-small",
    encoding_format="float",
)
