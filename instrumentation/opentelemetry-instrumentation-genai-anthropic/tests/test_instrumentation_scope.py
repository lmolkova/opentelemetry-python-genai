# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from opentelemetry.instrumentation.genai.anthropic import __version__
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)

SCOPE = "opentelemetry.instrumentation.genai.anthropic"


def test_instrumentation_scope(
    span_exporter,
    metric_reader,
    log_exporter,
    anthropic_client,
    instrument_event_only,
    vcr,
):
    with vcr.use_cassette("test_sync_messages_create_basic.yaml"):
        anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": "Say hello in one word."}],
        )

    assert_instrumentation_scope(
        SCOPE,
        __version__,
        span_exporter=span_exporter,
        metric_reader=metric_reader,
        log_exporter=log_exporter,
    )
