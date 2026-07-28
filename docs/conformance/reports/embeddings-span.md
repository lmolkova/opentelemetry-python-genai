# Embeddings Span

> **[Semantic Convention](https://github.com/open-telemetry/semantic-conventions-genai/blob/528c45308c35c4d0cc31d386238908b4a1e7fd8f/docs/gen-ai/gen-ai-spans.md#embeddings)**

## Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.operation.name | [google-genai], [openai] |
| gen_ai.provider.name | [google-genai], [openai] |

## Conditionally Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.request.model | [google-genai], [openai] |
| server.port | (none) |

## Recommended

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.embeddings.dimension.count | [google-genai], [openai] |
| gen_ai.request.encoding_formats | (none) |
| gen_ai.response.model | [openai] |
| gen_ai.usage.input_tokens | [google-genai], [openai] |
| server.address | [google-genai], [openai] |

[google-genai]: ../../../instrumentation/opentelemetry-instrumentation-google-genai/tests/conformance
[openai]: ../../../instrumentation/opentelemetry-instrumentation-genai-openai/tests/conformance
