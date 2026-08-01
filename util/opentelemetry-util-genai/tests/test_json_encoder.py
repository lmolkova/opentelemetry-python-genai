# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import unittest
from dataclasses import dataclass

from opentelemetry.util.genai.types import RetrievalDocument, Text
from opentelemetry.util.genai.utils import gen_ai_json_dumps


class GenAiJsonDumpsTest(unittest.TestCase):
    def test_bytes_are_base64_encoded(self) -> None:
        self.assertEqual(gen_ai_json_dumps({"b": b"\x89PNG"}), '{"b":"iVBORw=="}')

    def test_dataclass_is_serialized(self) -> None:
        self.assertEqual(
            gen_ai_json_dumps(Text(content="hi")),
            '{"content":"hi","type":"text"}',
        )

    def test_sequence_of_dataclasses_is_serialized(self) -> None:
        self.assertEqual(
            gen_ai_json_dumps([RetrievalDocument(id="doc_1", score=0.5)]),
            '[{"id":"doc_1","score":0.5}]',
        )

    def test_nested_dataclasses_are_serialized(self) -> None:
        @dataclass
        class Wrapper:
            part: Text

        self.assertEqual(
            gen_ai_json_dumps(Wrapper(part=Text(content="hi"))),
            '{"part":{"content":"hi","type":"text"}}',
        )

    def test_unsupported_type_is_dropped(self) -> None:
        """Serialization must not raise into the instrumented call."""

        class Custom:
            pass

        with self.assertLogs(
            "opentelemetry.util.genai.utils", level="DEBUG"
        ) as logs:
            serialized = gen_ai_json_dumps({"a": 1, "b": Custom()})

        self.assertEqual(serialized, '{"a":1,"b":null}')
        self.assertIn("Custom", logs.output[0])
