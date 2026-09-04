# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from portkey_ai import Portkey

from opentelemetry.instrumentation.genai.portkey import __version__
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)

from .test_chat_completions import (
    _create_mock_chat_completion,
    _setup_mock_chat,
)

SCOPE = "opentelemetry.instrumentation.genai.portkey"


def test_instrumentation_scope(
    instrument_portkey, span_exporter, metric_reader
):
    client = Portkey(
        api_key="test_pk",
        provider="openai",
        base_url="https://api.portkey.ai/v1",
    )
    _setup_mock_chat(client, _create_mock_chat_completion())
    client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello!"}],
        model="gpt-4o",
    )

    assert_instrumentation_scope(
        SCOPE,
        __version__,
        span_exporter=span_exporter,
        metric_reader=metric_reader,
    )
