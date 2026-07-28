# Invoke Agent Internal Span

> **[Semantic Convention](https://github.com/open-telemetry/semantic-conventions-genai/blob/528c45308c35c4d0cc31d386238908b4a1e7fd8f/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-internal-span)**

## Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.operation.name | [langchain], [openai-agents] |

## Conditionally Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.agent.description | (none) |
| gen_ai.agent.name | [langchain], [openai-agents] |
| gen_ai.agent.version | (none) |
| gen_ai.conversation.id | [langchain] |
| gen_ai.data_source.id | (none) |
| gen_ai.output.type | (none) |
| gen_ai.request.choice.count | (none) |
| gen_ai.request.model | (none) |
| gen_ai.request.seed | (none) |

## Recommended

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.request.frequency_penalty | (none) |
| gen_ai.request.max_tokens | (none) |
| gen_ai.request.presence_penalty | (none) |
| gen_ai.request.stop_sequences | (none) |
| gen_ai.request.temperature | (none) |
| gen_ai.request.top_p | (none) |
| gen_ai.response.finish_reasons | (none) |
| gen_ai.usage.cache_creation.input_tokens | (none) |
| gen_ai.usage.cache_read.input_tokens | (none) |
| gen_ai.usage.input_tokens | (none) |
| gen_ai.usage.output_tokens | (none) |

## Opt-In

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.input.messages | [langchain] |
| gen_ai.output.messages | [langchain] |
| gen_ai.system_instructions | (none) |
| gen_ai.tool.definitions | (none) |

[langchain]: ../../../instrumentation/opentelemetry-instrumentation-genai-langchain/tests/conformance
[openai-agents]: ../../../instrumentation/opentelemetry-instrumentation-genai-openai-agents/tests/conformance
