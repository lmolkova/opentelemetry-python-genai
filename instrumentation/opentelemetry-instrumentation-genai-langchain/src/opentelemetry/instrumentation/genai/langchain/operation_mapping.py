# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Callback-to-semconv operation mapping for LangChain callbacks.

Maps each LangChain callback to the correct GenAI semantic convention
operation name.  Direct callbacks (``on_chat_model_start``,
``on_llm_start``, ``on_tool_start``, ``on_retriever_start``) have a
fixed 1-to-1 mapping.  ``on_chain_start`` requires heuristic
classification because LangChain emits this callback for agents,
workflows, and internal plumbing alike.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from opentelemetry.semconv._incubating.attributes import (
    gen_ai_attributes as GenAI,
)

__all__ = [
    "OperationName",
    "classify_chain_run",
    "resolve_agent_name",
]

# ---------------------------------------------------------------------------
# Operation name constants (sourced from the GenAI semconv enum where
# available, with string fallbacks for values not yet in the enum).
# ---------------------------------------------------------------------------


class OperationName:
    """Canonical GenAI semantic convention operation names."""

    INVOKE_AGENT: str = GenAI.GenAiOperationNameValues.INVOKE_AGENT.value
    INVOKE_WORKFLOW: str = GenAI.GenAiOperationNameValues.INVOKE_WORKFLOW.value


# ---------------------------------------------------------------------------
# LangGraph markers – names and prefixes produced by LangGraph that must
# be recognized when classifying ``on_chain_start`` callbacks.
# ---------------------------------------------------------------------------

LANGGRAPH_NODE_KEY = "langgraph_node"
LANGGRAPH_START_NODE = "__start__"
MIDDLEWARE_PREFIX = "Middleware."
LANGGRAPH_IDENTIFIER = "LangGraph"

# Metadata keys used by callers to override classification.
_META_AGENT_SPAN = "otel_agent_span"
_META_WORKFLOW_SPAN = "otel_workflow_span"
_META_AGENT_NAME = "agent_name"
_META_AGENT_TYPE = "agent_type"
_META_OTEL_TRACE = "otel_trace"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def resolve_agent_name(
    serialized: dict[str, Any],
    metadata: Optional[dict[str, Any]],
    kwargs: dict[str, Any],
) -> Optional[str]:
    """Derive the best-effort agent name from callback arguments.

    Checks (in priority order):
    1. ``metadata["agent_name"]``
    2. ``kwargs["name"]``
    3. ``serialized["name"]``
    4. ``metadata["langgraph_node"]`` (if present and not a start node)
    """
    if metadata:
        name = metadata.get(_META_AGENT_NAME)
        if name:
            return str(name)

    name = kwargs.get("name")
    if name:
        return str(name)

    name = serialized.get("name") if serialized else None
    if name:
        return str(name)

    if metadata:
        node = metadata.get(LANGGRAPH_NODE_KEY)
        if node and node != LANGGRAPH_START_NODE:
            return str(node)

    return None


def _has_agent_signals(metadata: Optional[dict[str, Any]]) -> bool:
    """Return True when metadata contains any signal that the chain is an agent."""
    if not metadata:
        return False
    return bool(
        metadata.get(_META_AGENT_SPAN)
        or metadata.get(_META_AGENT_NAME)
        or metadata.get(_META_AGENT_TYPE)
    )


def _is_langgraph_graph(
    serialized: dict[str, Any],
    kwargs: dict[str, Any],
) -> bool:
    """Return True if the chain is a LangGraph graph (``Pregel``) invocation.

    LangGraph reports the graph itself under the ``LangGraph`` identifier as the
    run name (``kwargs['name']`` at runtime, or ``serialized['name']`` /
    ``serialized['graph']['id']`` in the serialized repr). Individual graph
    nodes are reported under the node name instead, so this reliably
    distinguishes a (sub)graph invocation from a node invocation.
    """
    name = kwargs.get("name")
    if not name and serialized:
        name = serialized.get("name")
    if name and LANGGRAPH_IDENTIFIER in str(name):
        return True

    if serialized and isinstance(serialized.get("graph"), dict):
        graph_id = serialized["graph"].get("id", "")
        if LANGGRAPH_IDENTIFIER in str(graph_id):
            return True

    return False


def _looks_like_workflow(
    serialized: dict[str, Any],
    metadata: Optional[dict[str, Any]],
    kwargs: dict[str, Any],
    parent_run_id: Optional[UUID],
) -> bool:
    """Return True if the chain looks like a workflow/graph.

    Both top-level graphs and nested subgraphs are treated as workflows, so a
    multi-graph pipeline produces one ``invoke_workflow`` span per graph. A
    nested subgraph is distinguished from a top-level workflow later, when the
    span is created, by inspecting the run tree.
    """
    # An explicit workflow override is authoritative.
    if metadata and metadata.get(_META_WORKFLOW_SPAN):
        return True

    # A LangGraph graph invocation, whether top-level or a nested subgraph.
    if _is_langgraph_graph(serialized, kwargs):
        return True

    # A root-level chain with no serialized data to inspect. We have zero
    # information about it, but prefer emitting a span for the outermost
    # invocation rather than silently dropping it.
    if parent_run_id is None and not serialized:
        return True

    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _should_ignore_chain(
    metadata: Optional[dict[str, Any]],
    agent_name: Optional[str],
    kwargs: dict[str, Any],
) -> bool:
    """Return True if the chain callback should be silently suppressed.

    Suppression happens when:
    * The node is the LangGraph ``__start__`` node.
    * The name carries the ``Middleware.`` prefix.
    * ``metadata["otel_trace"]`` is explicitly ``False``.
    * ``metadata["otel_agent_span"]`` is explicitly ``False`` and no other
      agent signals are present.
    """
    if metadata:
        node = metadata.get(LANGGRAPH_NODE_KEY)
        if node == LANGGRAPH_START_NODE:
            return True

        if metadata.get(_META_OTEL_TRACE) is False:
            return True

        if (
            metadata.get(_META_AGENT_SPAN) is False
            and not metadata.get(_META_AGENT_NAME)
            and not metadata.get(_META_AGENT_TYPE)
        ):
            return True

    if agent_name and agent_name.startswith(MIDDLEWARE_PREFIX):
        return True

    name_from_kwargs = kwargs.get("name", "")
    if isinstance(name_from_kwargs, str) and name_from_kwargs.startswith(
        MIDDLEWARE_PREFIX
    ):
        return True

    return False


def classify_chain_run(
    serialized: dict[str, Any],
    metadata: Optional[dict[str, Any]],
    kwargs: dict[str, Any],
    parent_run_id: Optional[UUID] = None,
) -> Optional[str]:
    """Classify a ``on_chain_start`` callback into a semconv operation.

    Returns one of the :class:`OperationName` constants, or ``None`` when
    the chain should be suppressed (no span emitted).

    Classification order:
    1. Check for explicit suppression signals.
    2. Check for agent signals → ``invoke_agent``.
    3. Check for workflow signals → ``invoke_workflow``.
    4. Default: ``None`` (suppress – unclassified chains are not emitted).
    """
    agent_name = resolve_agent_name(serialized, metadata, kwargs)

    # 1. Suppress known noise.
    if _should_ignore_chain(metadata, agent_name, kwargs):
        return None

    # 2. Agent detection.
    if _has_agent_signals(metadata):
        return OperationName.INVOKE_AGENT

    # 3. Workflow / orchestration detection.
    if _looks_like_workflow(serialized, metadata, kwargs, parent_run_id):
        return OperationName.INVOKE_WORKFLOW

    # 4. Default: suppress unclassified chains.
    return None
