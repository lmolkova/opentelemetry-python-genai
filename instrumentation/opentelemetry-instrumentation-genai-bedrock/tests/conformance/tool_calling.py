# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

import boto3

messages = [
    {
        "role": "user",
        "content": [
            {"text": "What is the weather in Seattle and San Francisco today?"}
        ],
    }
]
tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The name of the city",
                            }
                        },
                        "required": ["location"],
                    }
                },
            }
        }
    ]
}
client = boto3.client("bedrock-runtime", region_name="us-east-1")
client.converse(
    messages=messages,
    modelId="amazon.nova-micro-v1:0",
    toolConfig=tool_config,
)
