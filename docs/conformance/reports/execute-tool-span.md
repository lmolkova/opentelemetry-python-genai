# Execute Tool Span

> **[Semantic Convention](https://github.com/open-telemetry/semantic-conventions-genai/blob/528c45308c35c4d0cc31d386238908b4a1e7fd8f/docs/gen-ai/gen-ai-spans.md#execute-tool-span)**

## Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.operation.name | [langchain], [openai-agents] |
| gen_ai.tool.name | [langchain], [openai-agents] |

## Recommended

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.tool.call.id | [langchain] |
| gen_ai.tool.description | [langchain] |
| gen_ai.tool.type | [langchain], [openai-agents] |

## Opt-In

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.tool.call.arguments | [langchain] |
| gen_ai.tool.call.result | [langchain], [openai-agents] |

[langchain]: ../../../instrumentation/opentelemetry-instrumentation-genai-langchain/tests/conformance
[openai-agents]: ../../../instrumentation/opentelemetry-instrumentation-genai-openai-agents/tests/conformance
