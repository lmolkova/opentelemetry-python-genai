# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

_REAL_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAIAAADYYG7QAAAARklEQVR42u3X"
    "QQ0AIAwAsSnZG4lInJxJwMRICGlyAvq9yF1PFUBAQEBAQBdAXWskICAgICAg"
    "ICAgICAgIOcKBAQEBPQd6ACUHHNEU5qggAAAAABJRU5ErkJggg=="
)

_ANTHROPIC_FILE_ID = "file_011CNhaGCM5eyZmDsFmQJVQe"

# 1. OpenAI with image_url data URI
openai_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1,
    max_tokens=100,
)
openai_llm.invoke(
    [
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "What is in this image?",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{_REAL_PNG_B64}"
                    },
                },
            ]
        ),
    ]
)

# 2. OpenAI with image payload
openai_llm.invoke(
    [
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "What is in this image?",
                },
                {
                    "type": "image",
                    "base64": _REAL_PNG_B64,
                    "mime_type": "image/png",
                },
            ]
        ),
    ]
)

# 3. OpenAI Responses API with input_image
openai_responses_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1,
    max_tokens=100,
    use_responses_api=True,
    include_response_headers=True,
)
openai_responses_llm.invoke(
    [
        HumanMessage(
            content=[
                {
                    "type": "input_text",
                    "text": "What is in this image?",
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{_REAL_PNG_B64}",
                },
            ]
        ),
    ]
)

# 4. Anthropic with base64 image
anthropic_llm = ChatAnthropic(
    model="claude-sonnet-4-5",
    temperature=0.1,
    max_tokens=1024,
)
anthropic_llm.invoke(
    [
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "What is in this image?",
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": _REAL_PNG_B64,
                    },
                },
            ]
        ),
    ]
)

# 5. Anthropic with file reference
anthropic_llm.invoke(
    [
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "What is in this image?",
                },
                {
                    "type": "image",
                    "source": {
                        "type": "file",
                        "file_id": _ANTHROPIC_FILE_ID,
                    },
                },
            ]
        ),
    ]
)
