---
name: write-conformance-tests
description: Author GenAI conformance-test scenarios for an OpenTelemetry instrumentation package - conformance.yaml configuration, standalone scenario scripts under tests/conformance/, declared gaps, span/metric expectations, and genai-mock-server. Use when adding or updating conformance tests for any instrumentation, whether greenfield or ported.
---

# Write GenAI conformance tests

Conformance tests validate that an instrumentation package emits telemetry
matching the [GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai)
via Weaver live-check. They apply to **any** instrumentation package -
greenfield or ported - and don't depend on how the package was built.

Conformance testing is driven by the shared runner from
[`semantic-conventions-conformance`](https://github.com/open-telemetry/semantic-conventions-conformance)
(`genai-conformance`). Each instrumentation package provides:

1. `tests/conformance/conformance.yaml` - declares the runner, mock server, environment,
   declared gaps (`expected_violations`), and per-scenario span/metric expectations.
2. `tests/conformance/<scenario>.py` - standalone Python scenario scripts executed under
   `opentelemetry-instrument`.
3. `tests/conformance/data.json` - committed coverage file recording emitted spans, metrics,
   events, and findings from the run.

For the always-on rules that hold even without this skill loaded, see the **Conformance tests**
section of [AGENTS.md](../../../AGENTS.md).

## One scenario per operation

Put one scenario per emitted semconv operation under `tests/conformance/`.
Write a scenario for **every** semconv operation the library emits, even one
currently blocked by a util-genai or semconv gap. Skipping the scenario hides
the gap; writing it records the gap (see [Declared gaps](#declared-gaps)). 
**Never** drop a scenario file because it would fail today.

## Recommended scenarios

Cover the scenarios below that apply to the library. Skip a row only when the
library genuinely can't perform that operation (e.g. an inference-only
client has no `embeddings` scenario).

**LLM client instrumentations:**

| Scenario | File | Covers |
|---|---|---|
| Inference | `inference.py` | A `chat` operation. |
| Streaming | `streaming.py` | A streamed `chat` operation, draining the stream completely. |
| Tool calling | `tool_calling.py` | A `chat` turn where the model returns tool calls and a follow-up turn feeds tool results back. Asserts tool calls and tool results are present on input/output messages. Do **not** expect `execute_tool` spans unless the client library itself instruments tool execution - most don't; tool execution is the caller's code. |
| Multimodal content | `multimodal.py` | A `chat` turn carrying the non-text parts the client accepts (inline image/audio bytes, media URLs, file refs, …), asserting each round-trips onto the messages. |
| Reasoning | `reasoning.py` | A `chat` turn against a reasoning model where the response carries reasoning/thinking content. |
| Embeddings | `embeddings.py` | An `embeddings` operation. |

**Agent / orchestration instrumentations:**

| Scenario | File | Covers |
|---|---|---|
| Agent invocation | `invoke_agent.py` | An `invoke_agent` run. |
| Tool calling | `automatic_tool_calling.py` | An `invoke_agent` run that calls at least one tool - expects `invoke_agent` plus nested `execute_tool` / `chat` spans. |
| Multi-agent orchestration | `multi_agent.py` | One agent handing off to or invoking another - expects nested `invoke_agent` spans under the orchestrator. |
| Workflows | `workflow.py` | An `invoke_workflow` run wrapping the agent/tool spans it drives. |

## Message-part coverage

Weaver validates a part's *shape*, not *which* part types a scenario
exercised. Exercise **every non-text part type the library can
emit** and assert it landed on a message. Cover only what the package
instruments: check its message serializer for which
`opentelemetry.util.genai.types` parts it produces.

| Part `type` | util-genai type | Emitted when the library accepts… |
|---|---|---|
| `text` | `TextPart` | plain text (always) |
| `tool_call` / `tool_call_response` | `ToolCallRequestPart` / `ToolCallResponsePart` | function/tool calling - covered by `tool_calling.py` |
| `server_tool_call` / `server_tool_call_response` | `ServerToolCallPart` / `ServerToolCallResponsePart` | vendor server-side tools (web_search, code_interpreter, …) |
| `reasoning` | `ReasoningPart` | reasoning / thinking items |
| `blob` | `BlobPart` | inline image/audio/video **bytes** (`modality` distinguishes them) |
| `uri` | `UriPart` | an external media **URL** (`modality`) |
| `file` | `FilePart` | a **file reference** / id (`modality`) |
| `generic` | `GenericPart` | a provider item with no semconv mapping - flag, don't drop |

Group by shared scenario - typically one `multimodal.py` for the
image/audio/file/url inputs the client accepts, `tool_calling.py` for tool
parts, and `reasoning.py` for `reasoning` parts (a reasoning model emits
those on output messages, not input).

If a part type the library accepts can't round-trip yet (a util-genai/semconv
gap), still write the scenario and record it as a
[declared gap](#declared-gaps) - never silently omit the part.

## Standalone scenario scripts

Each scenario is a standalone Python script under `tests/conformance/<scenario>.py`.
The script does **not** import pytest, Weaver, or manually wire SDK Tracer/Meter providers.
Instead, the runner executes it under `opentelemetry-instrument python <scenario>.py`, which
automatically initializes OpenTelemetry and forwards telemetry to Weaver.

The script initializes the library client pointing to `${MOCK_SERVER_URL}` (injected via `env`)
and executes the target operation:

```python
# tests/conformance/inference.py
from openai import OpenAI

client = OpenAI()
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say this is a test"}],
)
```

Keep scripts minimal and self-contained:
- No hardcoded external network calls.
- Consume configuration from environment variables declared in `conformance.yaml`.
- Drain streams completely in streaming scenarios.

## The `conformance.yaml` configuration

`tests/conformance/conformance.yaml` is the declarative configuration for the test package.
It defines:
- `runner`: always `genai-conformance`.
- `instrumented_library`: name of the underlying SDK (e.g. `openai`, `anthropic`).
- `instrumentation_library`: name of the instrumentation package (e.g. `opentelemetry-instrumentation-genai-openai`).
- `server`: mock server startup command, usually `genai-mock-server --port ${PORT}`.
- `env`: environment variables injected into the scenario execution environment.
- `scenarios`: dictionary of scenario configurations with per-scenario expectations and declared gaps (`expected_violations`).

Example:

```yaml
# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

runner: genai-conformance
instrumented_library: openai
instrumentation_library: opentelemetry-instrumentation-genai-openai

server:
  run: genai-mock-server --port ${PORT}

env:
  OPENAI_BASE_URL: ${MOCK_SERVER_URL}/v1
  OPENAI_API_KEY: test_openai_api_key
  OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT: SPAN_ONLY

scenarios:
  inference:
    run: opentelemetry-instrument python inference.py
    spans:
      - match:
          attributes:
            gen_ai.operation.name: chat
        expect:
          count: 1
    metrics:
      - gen_ai.client.operation.duration
      - gen_ai.client.token.usage

  tool_calling:
    run: opentelemetry-instrument python tool_calling.py
    spans:
      - match:
          attributes:
            gen_ai.operation.name: chat
        expect:
          count: 2
    metrics:
      - gen_ai.client.operation.duration
      - gen_ai.client.token.usage
```

## Span and metric expectations

The runner validates scenario telemetry strictly:

1. **Span counts**: `expect.count` defines the exact number of matching spans.
   Any extra undeclared spans cause the scenario to fail.
2. **Span attributes**: under `expect.attributes`, matchers check attribute presence or values:
   ```yaml
   attributes:
     gen_ai.request.stream:
       equals: true
     gen_ai.response.id:
       present: true
   ```
3. **Metrics**: listed under `metrics:` must appear in the emitted telemetry.
   Missing expected metrics or extra undeclared metrics fail the test.

## Declared gaps

Known semconv departures or util-genai gaps are declared under `expected_violations:` in `conformance.yaml`.
Each entry requires:
- `id`: Weaver advice/violation rule ID (e.g. `genai_expected_attribute_missing`, `genai_operation_name_unknown`, `missing_attribute`).
- `context`: specific key-value pairs identifying the gap (e.g. `operation`, `missing_attribute`, `attribute_key`).
- `reason`: short explanation of why the violation exists.

```yaml
expected_violations:
  - id: genai_expected_attribute_missing
    context:
      operation: chat
      missing_attribute: server.address
    reason: underlying client does not expose remote address
```

The runner strictly enforces declared violations:
- Any **undeclared** violation reported by Weaver fails the run.
- Any **declared** violation that Weaver no longer reports fails the run with:
  `"... is no longer reported, remove it"`.
This ensures gaps are tracked and resolved as soon as fixes land.

## Mock server vs. Cassettes

Conformance tests run against `genai-mock-server` (provided by `semantic-conventions-conformance`),
**not** VCR cassettes. VCR cassettes are used solely for unit tests.

- The runner launches `genai-mock-server --port ${PORT}` on a random free port and exposes
  `${MOCK_SERVER_URL}` and `${PORT}` to `conformance.yaml` `env`.
- If an instrumentation requires a mock server capability or endpoint not yet supported by
  `genai-mock-server` (e.g. a new vendor endpoint or protocol), contribute the mock handler
  to `tools/gen-ai/mock-server` in the `semantic-conventions-conformance` repository.
- Pure agent or in-memory frameworks (e.g. smolagents) that use in-process dummy models may run
  without `server:` in `conformance.yaml`.

## Coverage data file (`data.json`)

When all scenarios in `conformance.yaml` pass, the runner writes a summarized coverage report
to `tests/conformance/data.json`. This file records:
- Emitted spans and their carried attributes.
- Emitted metrics and events.
- Recorded findings / violations.

Commit `data.json` alongside `conformance.yaml`. Reviewing diffs in `data.json` makes telemetry
changes visible during PR reviews.

## Running

Run conformance tests using tox:

```sh
uv run tox -e py314-test-instrumentation-genai-<lib>-conformance
```

The `*-conformance` tox env invokes `pytest` directly on `tests/conformance/conformance.yaml`:

```sh
pytest instrumentation/<pkg>/tests/conformance/conformance.yaml
```

The unit test envs (`*-{oldest,latest}`) ignore the `tests/conformance` directory so they do not
require conformance tools or the Weaver binary.

