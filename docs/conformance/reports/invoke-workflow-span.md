# Invoke Workflow Span

> **[Semantic Convention](https://github.com/open-telemetry/semantic-conventions-genai/blob/528c45308c35c4d0cc31d386238908b4a1e7fd8f/docs/gen-ai/gen-ai-agent-spans.md#invoke-workflow-span)**

## Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.operation.name | [langchain], [openai-agents] |

## Conditionally Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.workflow.name | [langchain], [openai-agents] |

## Opt-In

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.input.messages | [langchain] |
| gen_ai.output.messages | [langchain] |

[langchain]: ../../../instrumentation/opentelemetry-instrumentation-genai-langchain/tests/conformance
[openai-agents]: ../../../instrumentation/opentelemetry-instrumentation-genai-openai-agents/tests/conformance
