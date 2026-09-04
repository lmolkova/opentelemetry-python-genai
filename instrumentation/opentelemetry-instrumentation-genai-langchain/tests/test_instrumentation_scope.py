# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from langchain_core.messages import HumanMessage, SystemMessage

from opentelemetry.instrumentation.genai.langchain import (
    LangChainInstrumentor,
    __version__,
)
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)
from opentelemetry.test_util_genai.instrumentor import instrument

from .test_llm_call import _openai_cassette_name

SCOPE = "opentelemetry.instrumentation.genai.langchain"


def test_instrumentation_scope(
    span_exporter,
    metric_reader,
    log_exporter,
    tracer_provider,
    meter_provider,
    logger_provider,
    chat_openai_gpt_3_5_turbo_model,
    vcr,
):
    with instrument(
        LangChainInstrumentor(),
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
        logger_provider=logger_provider,
        content_capture="SPAN_AND_EVENT",
        emit_event=True,
    ):
        with vcr.use_cassette(
            _openai_cassette_name(
                chat_openai_gpt_3_5_turbo_model,
                "test_chat_openai_gpt_3_5_turbo_model_llm_call",
            )
        ):
            chat_openai_gpt_3_5_turbo_model.invoke(
                [
                    SystemMessage(content="You are a helpful assistant!"),
                    HumanMessage(content="What is the capital of France?"),
                ]
            )

    assert_instrumentation_scope(
        SCOPE,
        __version__,
        span_exporter=span_exporter,
        metric_reader=metric_reader,
        log_exporter=log_exporter,
    )
