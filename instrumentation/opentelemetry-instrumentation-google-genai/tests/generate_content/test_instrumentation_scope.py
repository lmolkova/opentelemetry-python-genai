# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Telemetry must be attributed to this instrumentation, not to util-genai."""

from opentelemetry.instrumentation.google_genai.version import __version__
from opentelemetry.test_util_genai.assertions import (
    assert_instrumentation_scope,
)

from .base import TestCase

SCOPE = "opentelemetry.instrumentation.google_genai"


class TestInstrumentationScope(TestCase):
    def test_instrumentation_scope(self):
        self.configure_valid_response(text="Yep, it works!")
        self.client.models.generate_content(
            model="gemini-2.0-flash", contents="Does this work?"
        )

        scopes = [
            *(
                span.instrumentation_scope
                for span in self.otel.get_finished_spans()
            ),
            *(log.scope for log in self.otel.get_finished_logs()),
            *(metric.scope for metric in self.otel.get_metrics_data()),
        ]
        assert_instrumentation_scope(SCOPE, __version__, scopes=scopes)
