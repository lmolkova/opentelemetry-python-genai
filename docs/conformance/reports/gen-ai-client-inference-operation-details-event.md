# Inference Operation Details Event

> **[Semantic Convention](https://github.com/open-telemetry/semantic-conventions-genai/blob/528c45308c35c4d0cc31d386238908b4a1e7fd8f/docs/gen-ai/gen-ai-events.md#event-gen_aiclientinferenceoperationdetails)**

## Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.operation.name | [google-genai] |
| gen_ai.provider.name | [google-genai] |

## Conditionally Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.conversation.id | (none) |
| gen_ai.output.type | (none) |
| gen_ai.request.choice.count | (none) |
| gen_ai.request.model | [google-genai] |
| gen_ai.request.seed | (none) |
| gen_ai.request.stream | (none) |
| gen_ai.request.top_k | (none) |
| server.port | (none) |

## Recommended

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.conversation.compacted | (none) |
| gen_ai.request.frequency_penalty | (none) |
| gen_ai.request.max_tokens | (none) |
| gen_ai.request.presence_penalty | (none) |
| gen_ai.request.stop_sequences | (none) |
| gen_ai.request.temperature | (none) |
| gen_ai.request.top_p | (none) |
| gen_ai.response.finish_reasons | [google-genai] |
| gen_ai.response.id | [google-genai] |
| gen_ai.response.model | [google-genai] |
| gen_ai.response.time_to_first_chunk | (none) |
| gen_ai.usage.cache_creation.input_tokens | (none) |
| gen_ai.usage.cache_read.input_tokens | [google-genai] |
| gen_ai.usage.input_tokens | [google-genai] |
| gen_ai.usage.output_tokens | [google-genai] |
| gen_ai.usage.reasoning.output_tokens | [google-genai] |
| server.address | [google-genai] |

## Opt-In

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.input.messages | (none) |
| gen_ai.output.messages | (none) |
| gen_ai.system_instructions | (none) |
| gen_ai.tool.definitions | [google-genai] |

[google-genai]: ../../../instrumentation/opentelemetry-instrumentation-google-genai/tests/conformance
