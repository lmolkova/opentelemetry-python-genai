# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Tests for Anthropic message parameter extraction."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from opentelemetry.instrumentation.genai.anthropic.messages_extractors import (
    extract_params,
    set_invocation_response_attributes,
)
from opentelemetry.instrumentation.genai.anthropic.utils import (
    _convert_content_block_to_part,
)


def test_extract_params_reads_sampling_params_from_extra_body():
    params = extract_params(
        extra_body={"temperature": 0.7, "top_p": 0.9, "top_k": 40}
    )

    assert params.temperature == 0.7
    assert params.top_p == 0.9
    assert params.top_k == 40


def test_extract_params_prefers_named_sampling_params():
    params = extract_params(
        temperature=0.2,
        top_p=0.3,
        top_k=10,
        extra_body={"temperature": 0.7, "top_p": 0.9, "top_k": 40},
    )

    assert params.temperature == 0.2
    assert params.top_p == 0.3
    assert params.top_k == 10


def test_extract_params_ignores_non_numeric_extra_body_sampling_params():
    params = extract_params(
        extra_body={"temperature": "high", "top_p": True, "top_k": 2.5}
    )

    assert params.temperature is None
    assert params.top_p is None
    assert params.top_k is None


def test_extract_params_ignores_non_mapping_extra_body():
    params = extract_params(extra_body="temperature=0.7")

    assert params.temperature is None
    assert params.top_p is None
    assert params.top_k is None


def test_set_invocation_response_attributes_records_cache_tokens():
    invocation = MagicMock()
    message = SimpleNamespace(
        id="msg_123",
        model="claude-3-7-sonnet-20250219",
        stop_reason="end_turn",
        usage=SimpleNamespace(
            input_tokens=10,
            output_tokens=20,
            cache_creation_input_tokens=15,
            cache_read_input_tokens=5,
        ),
    )
    set_invocation_response_attributes(
        invocation, message, capture_content=False
    )
    assert invocation.input_tokens == 30
    assert invocation.output_tokens == 20
    assert invocation.cache_write_input_tokens == 15
    assert invocation.cache_read_input_tokens == 5


def test_convert_beta_mcp_tool_result_block_serializable():
    try:
        from anthropic.types.beta import BetaMCPToolResultBlock, BetaTextBlock

        has_beta_mcp = hasattr(BetaMCPToolResultBlock, "model_fields")
    except (ImportError, AttributeError):
        has_beta_mcp = False

    if not has_beta_mcp:
        pytest.skip("BetaMCPToolResultBlock not supported")

    block = BetaMCPToolResultBlock(
        content=[BetaTextBlock(text="tool output", type="text")],
        is_error=False,
        tool_use_id="tool_123",
        type="mcp_tool_result",
    )
    part = _convert_content_block_to_part(block)
    assert part is not None
    assert part.id == "tool_123"
    assert part.response == [
        {"citations": None, "text": "tool output", "type": "text"}
    ]


def test_convert_dict_mcp_tool_use_and_result():
    part_use = _convert_content_block_to_part(
        {
            "type": "mcp_tool_use",
            "id": "call_1",
            "name": "read",
            "input": {"path": "a.txt"},
        }
    )
    assert part_use is not None
    assert part_use.id == "call_1"
    assert part_use.name == "read"
    assert part_use.arguments == {"path": "a.txt"}

    server_use = _convert_content_block_to_part(
        {
            "type": "server_tool_use",
            "id": "call_srv",
            "name": "web_search",
            "input": {"query": "otel"},
        }
    )
    assert server_use is not None
    assert server_use.id == "call_srv"
    assert server_use.name == "web_search"
    assert server_use.arguments == {"query": "otel"}

    part_res = _convert_content_block_to_part(
        {
            "type": "mcp_tool_result",
            "tool_use_id": "call_1",
            "content": "file contents",
        }
    )
    assert part_res is not None
    assert part_res.id == "call_1"
    assert part_res.response == "file contents"

    search_res = _convert_content_block_to_part(
        {
            "type": "web_search_tool_result",
            "tool_use_id": "call_srv",
            "content": "search results",
        }
    )
    assert search_res is not None
    assert search_res.id == "call_srv"
    assert search_res.response == "search results"


def test_convert_beta_blocks_when_available():
    try:
        from anthropic.types.beta import (
            BetaRedactedThinkingBlock,
            BetaServerToolUseBlock,
            BetaTextBlock,
            BetaThinkingBlock,
            BetaToolUseBlock,
        )
    except (ImportError, AttributeError):
        pytest.skip("Beta block types not available")

    # Text block
    text_part = _convert_content_block_to_part(
        BetaTextBlock(text="hello beta", type="text")
    )
    assert text_part is not None
    assert text_part.content == "hello beta"

    # Tool use block
    tool_part = _convert_content_block_to_part(
        BetaToolUseBlock(
            id="t_1", name="search", input={"q": "otel"}, type="tool_use"
        )
    )
    assert tool_part is not None
    assert tool_part.id == "t_1"
    assert tool_part.name == "search"
    assert tool_part.arguments == {"q": "otel"}

    # Server tool use block
    server_tool_part = _convert_content_block_to_part(
        BetaServerToolUseBlock(
            id="st_1",
            name="web_search",
            input={"q": "otel"},
            type="server_tool_use",
        )
    )
    assert server_tool_part is not None
    assert server_tool_part.id == "st_1"
    assert server_tool_part.name == "web_search"

    # Thinking block
    thinking_part = _convert_content_block_to_part(
        BetaThinkingBlock(
            thinking="deep thought", signature="sig", type="thinking"
        )
    )
    assert thinking_part is not None
    assert thinking_part.content == "deep thought"

    # Redacted thinking block
    redacted_part = _convert_content_block_to_part(
        BetaRedactedThinkingBlock(
            data="redacted_data", type="redacted_thinking"
        )
    )
    assert redacted_part is not None
    assert redacted_part.content == "redacted_data"

    try:
        from anthropic.types.beta import (
            BetaMCPToolUseBlock,
            BetaWebSearchResultBlock,
            BetaWebSearchToolResultBlock,
        )

        mcp_use = _convert_content_block_to_part(
            BetaMCPToolUseBlock(
                id="mcp_1",
                name="read_file",
                input={"path": "x.py"},
                server_name="fs",
                type="mcp_tool_use",
            )
        )
        assert mcp_use is not None
        assert mcp_use.id == "mcp_1"
        assert mcp_use.name == "read_file"
        assert mcp_use.arguments == {"path": "x.py"}

        search_block = _convert_content_block_to_part(
            BetaWebSearchToolResultBlock(
                content=[
                    BetaWebSearchResultBlock(
                        type="web_search_result",
                        url="https://example.com",
                        title="Title",
                        encrypted_content="enc",
                    )
                ],
                tool_use_id="ws_1",
                type="web_search_tool_result",
            )
        )
        assert search_block is not None
        assert search_block.id == "ws_1"
        assert isinstance(search_block.response, list)
    except (ImportError, AttributeError):
        pass
