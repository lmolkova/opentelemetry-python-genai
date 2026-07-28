# Inference Span

> **[Semantic Convention](https://github.com/open-telemetry/semantic-conventions-genai/blob/528c45308c35c4d0cc31d386238908b4a1e7fd8f/docs/gen-ai/gen-ai-spans.md#inference)**

## Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.operation.name | [anthropic], [crewai], [google-genai], [langchain], [openai] |
| gen_ai.provider.name | [anthropic], [crewai], [google-genai], [langchain], [openai] |

## Conditionally Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.conversation.id | (none) |
| gen_ai.output.type | [crewai] |
| gen_ai.request.choice.count | (none) |
| gen_ai.request.model | [anthropic], [crewai], [google-genai], [langchain], [openai] |
| gen_ai.request.seed | [langchain] |
| gen_ai.request.stream | (none) |
| gen_ai.request.top_k | (none) |
| server.port | (none) |

## Recommended

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.conversation.compacted | (none) |
| gen_ai.request.frequency_penalty | [langchain] |
| gen_ai.request.max_tokens | [anthropic], [langchain] |
| gen_ai.request.presence_penalty | [langchain] |
| gen_ai.request.stop_sequences | [langchain] |
| gen_ai.request.temperature | [langchain] |
| gen_ai.request.top_p | [langchain] |
| gen_ai.response.finish_reasons | [anthropic], [crewai], [google-genai], [langchain], [openai] |
| gen_ai.response.id | [anthropic], [crewai], [google-genai], [langchain], [openai] |
| gen_ai.response.model | [anthropic], [crewai], [google-genai], [langchain], [openai] |
| gen_ai.response.time_to_first_chunk | (none) |
| gen_ai.usage.cache_creation.input_tokens | [anthropic] |
| gen_ai.usage.cache_read.input_tokens | [anthropic], [openai] |
| gen_ai.usage.input_tokens | [anthropic], [crewai], [google-genai], [langchain], [openai] |
| gen_ai.usage.output_tokens | [anthropic], [crewai], [google-genai], [langchain], [openai] |
| gen_ai.usage.reasoning.output_tokens | [google-genai] |
| server.address | [anthropic], [crewai], [google-genai], [openai] |

## Opt-In

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.input.messages | [anthropic], [crewai], [google-genai], [langchain], [openai] |
| gen_ai.output.messages | [anthropic], [crewai], [google-genai], [langchain], [openai] |
| gen_ai.system_instructions | [openai] |
| gen_ai.tool.definitions | [crewai], [google-genai], [langchain], [openai] |

[anthropic]: ../../../instrumentation/opentelemetry-instrumentation-genai-anthropic/tests/conformance
[crewai]: ../../../instrumentation/opentelemetry-instrumentation-genai-crewai/tests/conformance
[google-genai]: ../../../instrumentation/opentelemetry-instrumentation-google-genai/tests/conformance
[langchain]: ../../../instrumentation/opentelemetry-instrumentation-genai-langchain/tests/conformance
[openai]: ../../../instrumentation/opentelemetry-instrumentation-genai-openai/tests/conformance
