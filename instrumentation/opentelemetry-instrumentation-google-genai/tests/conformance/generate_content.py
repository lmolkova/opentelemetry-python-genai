# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Conformance scenario: google-genai generate_content."""

from google.genai import Client

client = Client()
client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say this is a test",
)
