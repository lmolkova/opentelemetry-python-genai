# GenAI Semantic Convention Coverage

Which semantic convention attributes each instrumentation package in this repo
emits, per GenAI signal type. The pages under [reports/](reports/) mirror the
layout of the reference reports published by
[semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai/tree/main/reference/reports),
so the two can be compared side by side.

## How this is generated

The conformance tests (`uv run tox -e py3XX-test-instrumentation-genai-<lib>-conformance`)
validate emitted telemetry against the pinned GenAI semconv registry using Weaver
live-check. Each run records the package's attribute coverage to
`instrumentation/<pkg>/tests/conformance/data.json`. Regenerate the pages below
from those files with:

```sh
uv run python scripts/update_conformance_reports.py
```

Requirement levels and span classification come from the registry revision
pinned as `SEMCONV_GENAI_REF` in [versions.env](../../versions.env), so bumping
that pin can change these pages.

## Reading the tables

- Coverage reflects **what the conformance scenarios exercise**, not everything
  an instrumentation is capable of emitting. Most scenarios issue a single
  minimal request, so attributes like `gen_ai.request.temperature` read as
  unsupported for packages that would emit them given a richer request.
  Broadening the scenarios is the way to close those gaps.
- `data.json` is rewritten from a full conformance env run. A run filtered with
  `-k` produces a partial file — check the diff before committing.

<!-- status:begin -->
### Spans

| Span | Libraries |
| --- | --- |
| [Create Agent](reports/create-agent-span.md) | (none) |
| [Invoke Agent Client](reports/invoke-agent-client-span.md) | (none) |
| [Invoke Agent Internal](reports/invoke-agent-internal-span.md) | langchain, openai-agents |
| [Invoke Workflow](reports/invoke-workflow-span.md) | langchain, openai-agents |
| [Plan](reports/plan-span.md) | (none) |
| [Inference](reports/inference-span.md) | anthropic, crewai, google-genai, langchain, openai |
| [Embeddings](reports/embeddings-span.md) | google-genai, openai |
| [Retrieval](reports/retrieval-span.md) | (none) |
| [Memory](reports/memory-span.md) | (none) |
| [Execute Tool](reports/execute-tool-span.md) | langchain, openai-agents |

### Events

| Event | Libraries |
| --- | --- |
| [Inference Operation Details](reports/gen-ai-client-inference-operation-details-event.md) | google-genai |
| [Evaluation Result](reports/gen-ai-evaluation-result-event.md) | (none) |
<!-- status:end -->
