# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from unittest.mock import patch

from agno.agent import Agent
from agno.models.response import ModelResponse

from opentelemetry.instrumentation.genai.agno import __version__
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)

from tests.mock_model import MockModel

SCOPE = "opentelemetry.instrumentation.genai.agno"


def test_instrumentation_scope(
    instrument_agno, span_exporter, metric_reader
) -> None:
    agent = Agent(name="test-agent", model=MockModel(id="mock-model"))
    with (
        patch.object(Agent, "run", wraps=agent.run),
        patch(
            "agno.models.base.Model.response",
            return_value=ModelResponse(content="Hello back!"),
        ),
    ):
        agent.run("hello world")

    assert_instrumentation_scope(
        SCOPE,
        __version__,
        span_exporter=span_exporter,
        metric_reader=metric_reader,
    )
