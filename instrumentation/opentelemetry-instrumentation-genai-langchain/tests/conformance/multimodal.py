# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

_REAL_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1,
    max_tokens=100,
)

messages = [
    HumanMessage(
        content=[
            {
                "type": "text",
                "text": "What is in this image?",
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{_REAL_PNG_B64}"},
            },
        ]
    ),
]

llm.invoke(messages)
