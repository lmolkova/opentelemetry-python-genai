# Memory Span

> **[Semantic Convention](https://github.com/open-telemetry/semantic-conventions-genai/blob/528c45308c35c4d0cc31d386238908b4a1e7fd8f/docs/gen-ai/gen-ai-spans.md#memory)**

## Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.operation.name | (none) |

## Conditionally Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.memory.record.id | (none) |
| gen_ai.memory.store.id | (none) |
| gen_ai.provider.name | (none) |
| server.port | (none) |

## Recommended

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.memory.record.count | (none) |
| server.address | (none) |

## Opt-In

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.memory.query.text | (none) |
| gen_ai.memory.records | (none) |
