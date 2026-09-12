# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from unittest.mock import MagicMock

from opentelemetry.metrics import Histogram, Meter
from opentelemetry.test.test_base import TestBase
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.util.genai.semconv.gen_ai import GenAiOperationName
from opentelemetry.util.genai.semconv.gen_ai._metrics import _Metrics
from opentelemetry.util.genai.semconv.gen_ai._spans import _Spans
from opentelemetry.util.genai.types import InputMessage, TextPart


class TestSpans(TestBase):
    def setUp(self) -> None:
        super().setUp()
        self.spans = _Spans(self.tracer_provider.get_tracer(__name__))

    def test_inference_span(self) -> None:
        with self.spans.inference(
            "chat model",
            provider_name="custom-provider",
            operation_name=GenAiOperationName.CHAT,
            request_model="model",
            server_address="example.com",
        ) as span:
            span.set_input_messages(
                [InputMessage(role="user", parts=[TextPart(content="hello")])]
            )
            span.set_request_temperature(0.7)
            span.set_response_finish_reasons(["custom-finish-reason"])
            span.set_attributes({"custom.attribute": "value"})

        (recorded,) = self.get_finished_spans()
        assert recorded.kind is SpanKind.CLIENT
        assert recorded.attributes is not None
        assert recorded.attributes["gen_ai.provider.name"] == "custom-provider"
        assert recorded.attributes["gen_ai.operation.name"] == "chat"
        assert recorded.attributes["gen_ai.request.model"] == "model"
        assert recorded.attributes["server.address"] == "example.com"
        assert recorded.attributes["gen_ai.request.temperature"] == 0.7
        assert recorded.attributes["gen_ai.response.finish_reasons"] == (
            "custom-finish-reason",
        )
        assert recorded.attributes["custom.attribute"] == "value"
        assert (
            json.loads(recorded.attributes["gen_ai.input.messages"])[0]["role"]
            == "user"
        )

    def test_context_manager_records_error_and_reraises(self) -> None:
        error = ValueError("bad request")

        with self.assertRaises(ValueError) as raised:
            with self.spans.retrieval("retrieval"):
                raise error

        assert raised.exception is error
        (recorded,) = self.get_finished_spans()
        assert recorded.status.status_code is StatusCode.ERROR
        assert recorded.status.description == "bad request"
        assert recorded.attributes is not None
        assert recorded.attributes["error.type"] == "ValueError"
        assert len(recorded.events) == 1
        assert recorded.events[0].name == "exception"

    def test_context_manager_makes_span_current(self) -> None:
        tracer = self.tracer_provider.get_tracer(__name__)

        with self.spans.retrieval("retrieval"):
            with tracer.start_as_current_span("child"):
                pass

        child, retrieval = self.get_finished_spans()
        assert child.parent is not None
        assert retrieval.context is not None
        assert child.parent.span_id == retrieval.context.span_id

    def test_explicit_error_type_does_not_end_span(self) -> None:
        span = self.spans.retrieval("retrieval")

        span.set_error_details("429", "rate limited")
        assert self.get_finished_spans() == []

        span.end()
        span.end()

        (recorded,) = self.get_finished_spans()
        assert recorded.status.description == "rate limited"
        assert recorded.attributes is not None
        assert recorded.attributes["error.type"] == "429"


class TestMetrics(TestBase):
    def _harvest_metrics(self) -> dict[str, list[object]]:
        return {
            metric.name: list(metric.data.data_points)
            for metric in self.get_sorted_metrics() or []
        }

    def test_metric_method_is_lazy_and_typed_attributes_win(self) -> None:
        metrics = _Metrics(self.meter_provider.get_meter(__name__))

        assert self._harvest_metrics() == {}

        metrics.client_operation_duration(
            1.25,
            operation_name="custom-operation",
            provider_name="custom-provider",
            request_model="model",
            attributes={
                "custom.attribute": "value",
                "gen_ai.request.model": "ignored",
            },
        )

        points = self._harvest_metrics()["gen_ai.client.operation.duration"]
        assert len(points) == 1
        assert points[0].sum == 1.25
        assert points[0].attributes["gen_ai.operation.name"] == (
            "custom-operation"
        )
        assert points[0].attributes["gen_ai.provider.name"] == (
            "custom-provider"
        )
        assert points[0].attributes["gen_ai.request.model"] == "model"
        assert points[0].attributes["custom.attribute"] == "value"

    def test_histogram_boundaries_are_passed_when_instrument_is_created(
        self,
    ) -> None:
        meter = MagicMock(spec=Meter)
        histogram = MagicMock(spec=Histogram)
        meter.create_histogram.return_value = histogram
        metrics = _Metrics(
            meter,
            client_operation_duration_boundaries=(0.1, 1.0, 10.0),
        )

        metrics.client_operation_duration(1.25, operation_name="chat")

        meter.create_histogram.assert_called_once_with(
            "gen_ai.client.operation.duration",
            unit="s",
            description="GenAI operation duration.",
            explicit_bucket_boundaries_advisory=(0.1, 1.0, 10.0),
        )
