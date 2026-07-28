# Retrieval Span

> **[Semantic Convention](https://github.com/open-telemetry/semantic-conventions-genai/blob/528c45308c35c4d0cc31d386238908b4a1e7fd8f/docs/gen-ai/gen-ai-spans.md#retrievals)**

## Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.operation.name | (none) |

## Conditionally Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.data_source.id | (none) |
| gen_ai.provider.name | (none) |
| gen_ai.request.model | (none) |
| server.port | (none) |

## Recommended

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.retrieval.top_k | (none) |
| server.address | (none) |

## Opt-In

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.retrieval.documents | (none) |
| gen_ai.retrieval.query.text | (none) |
