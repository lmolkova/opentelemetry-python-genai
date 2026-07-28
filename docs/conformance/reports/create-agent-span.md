# Create Agent Span

> **[Semantic Convention](https://github.com/open-telemetry/semantic-conventions-genai/blob/528c45308c35c4d0cc31d386238908b4a1e7fd8f/docs/gen-ai/gen-ai-agent-spans.md#create-agent-span)**

## Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.operation.name | (none) |
| gen_ai.provider.name | (none) |

## Conditionally Required

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.agent.description | (none) |
| gen_ai.agent.id | (none) |
| gen_ai.agent.name | (none) |
| gen_ai.agent.version | (none) |
| gen_ai.request.model | (none) |
| server.port | (none) |

## Recommended

| Attribute | Supporting Libraries |
| --- | --- |
| server.address | (none) |

## Opt-In

| Attribute | Supporting Libraries |
| --- | --- |
| gen_ai.system_instructions | (none) |
