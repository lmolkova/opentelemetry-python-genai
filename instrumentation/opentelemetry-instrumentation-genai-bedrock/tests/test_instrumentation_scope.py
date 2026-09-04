# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from opentelemetry.instrumentation.genai.bedrock import __version__
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)

SCOPE = "opentelemetry.instrumentation.genai.bedrock"


def test_instrumentation_scope(
    bedrock_client,
    instrument_with_content,
    span_exporter,
    metric_reader,
    vcr,
) -> None:
    with vcr.use_cassette("test_converse_no_content.yaml"):
        bedrock_client.converse(
            messages=[
                {"role": "user", "content": [{"text": "Say this is a test"}]}
            ],
            modelId="amazon.nova-micro-v1:0",
            inferenceConfig={
                "maxTokens": 10,
                "temperature": 0.8,
                "topP": 1,
                "stopSequences": ["|"],
            },
        )

    assert_instrumentation_scope(
        SCOPE,
        __version__,
        span_exporter=span_exporter,
        metric_reader=metric_reader,
    )
