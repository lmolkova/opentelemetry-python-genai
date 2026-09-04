# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, max_tokens=100)

# 1. Unnamed agent
unnamed_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="You are a helpful assistant.",
)
unnamed_agent.invoke(
    {"messages": [{"role": "user", "content": "Say this is a test"}]}
)

# 2. Named agent
named_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="You are a helpful assistant.",
    name="weather_assistant",
)
named_agent.invoke(
    {"messages": [{"role": "user", "content": "Say this is a test"}]}
)
