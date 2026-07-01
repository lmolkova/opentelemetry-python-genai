# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""End-to-end test: a nested LangGraph workflow emits ``gen_ai.workflow.nested``.

An outer graph contains an inner (sub)graph as one of its nodes. The outer graph
is the top-level workflow and must NOT carry ``gen_ai.workflow.nested``; the
inner subgraph is nested and must carry ``gen_ai.workflow.nested = True``.
"""

from typing import Annotated, TypedDict

import pytest
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from opentelemetry.semconv._incubating.attributes import gen_ai_attributes

_GEN_AI_WORKFLOW_NESTED = "gen_ai.workflow.nested"


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    research: str


def _build_nested_graph(llm: ChatOpenAI):
    def researcher(state: GraphState) -> dict:
        response = llm.invoke(
            [
                SystemMessage(
                    content="You are a research assistant. Provide 2-3 factual sentences."
                ),
                HumanMessage(content=state["messages"][-1].content),
            ]
        )
        return {"research": response.content, "messages": [response]}

    inner_builder = StateGraph(GraphState)
    inner_builder.add_node("researcher", researcher)
    inner_builder.add_edge(START, "researcher")
    inner_builder.add_edge("researcher", END)
    inner_graph = inner_builder.compile()

    def summariser(state: GraphState) -> dict:
        response = llm.invoke(
            [
                SystemMessage(
                    content="You are an expert summariser. Condense the text below into one clear sentence."
                ),
                HumanMessage(content=state["research"]),
            ]
        )
        return {"messages": [response]}

    outer_builder = StateGraph(GraphState)
    outer_builder.add_node("data_gathering", inner_graph)
    outer_builder.add_node("summariser", summariser)
    outer_builder.add_edge(START, "data_gathering")
    outer_builder.add_edge("data_gathering", "summariser")
    outer_builder.add_edge("summariser", END)
    return outer_builder.compile()


# span_exporter, start_instrumentation and vcr are fixtures defined in conftest.py
@pytest.mark.vcr()
def test_nested_langgraph_workflow_sets_nested_attribute(
    span_exporter,
    start_instrumentation,
    monkeypatch,
    vcr,
):
    monkeypatch.setenv(
        "OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental"
    )

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
        max_tokens=200,
        seed=42,
    )
    graph = _build_nested_graph(llm)

    with vcr.use_cassette("nested_workflow_conformance.yaml"):
        graph.invoke(
            {
                "messages": [
                    HumanMessage(content="What is the capital of France?")
                ],
                "research": "",
            }
        )

    spans = span_exporter.get_finished_spans()

    operation = gen_ai_attributes.GEN_AI_OPERATION_NAME
    workflow_spans = [
        span
        for span in spans
        if span.attributes.get(operation) == "invoke_workflow"
    ]
    chat_spans = [
        span for span in spans if span.attributes.get(operation) == "chat"
    ]

    assert len(workflow_spans) == 2, (
        "Expected one workflow span for the outer graph and one for the inner "
        f"subgraph; saw {[s.name for s in spans]}"
    )
    assert len(chat_spans) == 2, (
        "Expected two chat spans (researcher and summariser); "
        f"saw {[s.name for s in spans]}"
    )

    nested_spans = [
        span
        for span in workflow_spans
        if span.attributes.get(_GEN_AI_WORKFLOW_NESTED) is True
    ]
    top_level_spans = [
        span
        for span in workflow_spans
        if _GEN_AI_WORKFLOW_NESTED not in span.attributes
    ]

    assert len(nested_spans) == 1, (
        "Exactly one workflow (the inner subgraph) must be marked nested"
    )
    assert len(top_level_spans) == 1, (
        "The top-level workflow must not carry gen_ai.workflow.nested"
    )
