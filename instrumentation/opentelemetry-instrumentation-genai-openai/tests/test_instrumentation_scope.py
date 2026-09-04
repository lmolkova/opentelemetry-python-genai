# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from opentelemetry.instrumentation.genai.openai import __version__
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)

from .test_utils import DEFAULT_MODEL, USER_ONLY_PROMPT

SCOPE = "opentelemetry.instrumentation.genai.openai"


def test_instrumentation_scope(
    span_exporter,
    metric_reader,
    log_exporter,
    openai_client,
    instrument_event_only,
    vcr,
):
    with vcr.use_cassette("test_chat_completion_with_content.yaml"):
        openai_client.chat.completions.create(
            messages=USER_ONLY_PROMPT,
            model=DEFAULT_MODEL,
            stream=False,
        )

    assert_instrumentation_scope(
        SCOPE,
        __version__,
        span_exporter=span_exporter,
        metric_reader=metric_reader,
        log_exporter=log_exporter,
    )
