# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from opentelemetry.instrumentation.genai.smolagents import __version__
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)

from .test_utils import MESSAGES, transformers_model

SCOPE = "opentelemetry.instrumentation.genai.smolagents"


def test_instrumentation_scope(
    instrument_event_only, span_exporter, metric_reader, log_exporter
) -> None:
    model = transformers_model(
        prompt_ids=[1, 2, 3], generated_ids=[4, 5], text="In Paris"
    )
    model.generate(messages=MESSAGES)

    assert_instrumentation_scope(
        SCOPE,
        __version__,
        span_exporter=span_exporter,
        metric_reader=metric_reader,
        log_exporter=log_exporter,
    )
