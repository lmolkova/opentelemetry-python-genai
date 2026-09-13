# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
# Code generated from OpenTelemetry GenAI semantic conventions. DO NOT EDIT.

from __future__ import annotations

from collections import ChainMap
from collections.abc import Mapping, MutableMapping, Sequence
from enum import Enum
from functools import cached_property
from typing import cast

from opentelemetry.context import Context
from opentelemetry.metrics import Histogram, Meter
from opentelemetry.util.genai.semconv.mcp import attributes as Attr
from opentelemetry.util.types import AttributeValue


def _value(value: AttributeValue | Enum) -> AttributeValue:
    return value.value if isinstance(value, Enum) else value


def _combine_attributes(
    typed_attributes: dict[str, AttributeValue],
    additional_attributes: Mapping[str, AttributeValue] | None,
) -> Mapping[str, AttributeValue]:
    if not additional_attributes:
        return typed_attributes
    if not typed_attributes:
        return additional_attributes
    return ChainMap(
        typed_attributes,
        cast("MutableMapping[str, AttributeValue]", additional_attributes),
    )


class _Metrics:
    """Records metrics following the mcp semantic conventions."""

    def __init__(
        self,
        meter: Meter,
        *,
        client_operation_duration_boundaries: Sequence[float] | None = None,
        client_session_duration_boundaries: Sequence[float] | None = None,
        server_operation_duration_boundaries: Sequence[float] | None = None,
        server_session_duration_boundaries: Sequence[float] | None = None,
    ) -> None:
        self._meter = meter
        self._boundaries = {
            "mcp.client.operation.duration": client_operation_duration_boundaries,
            "mcp.client.session.duration": client_session_duration_boundaries,
            "mcp.server.operation.duration": server_operation_duration_boundaries,
            "mcp.server.session.duration": server_session_duration_boundaries,
        }

    def client_operation_duration(
        self,
        value: float,
        *,
        method_name: Attr.MCPMethodName | str,
        error_type: str | None = None,
        gen_ai_operation_name: str | None = None,
        gen_ai_prompt_name: str | None = None,
        gen_ai_prompt_variable: Mapping[str, object] | None = None,
        gen_ai_tool_name: str | None = None,
        jsonrpc_protocol_version: str | None = None,
        protocol_version: str | None = None,
        resource_uri: str | None = None,
        network_protocol_name: str | None = None,
        network_protocol_version: str | None = None,
        network_transport: str | None = None,
        rpc_response_status_code: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `mcp.client.operation.duration`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if error_type is not None:
            typed_attributes["error.type"] = _value(error_type)
        if gen_ai_operation_name is not None:
            typed_attributes["gen_ai.operation.name"] = _value(
                gen_ai_operation_name
            )
        if gen_ai_prompt_name is not None:
            typed_attributes["gen_ai.prompt.name"] = _value(gen_ai_prompt_name)
        if gen_ai_prompt_variable is not None:
            typed_attributes["gen_ai.prompt.variable"] = _value(
                gen_ai_prompt_variable
            )
        if gen_ai_tool_name is not None:
            typed_attributes["gen_ai.tool.name"] = _value(gen_ai_tool_name)
        if jsonrpc_protocol_version is not None:
            typed_attributes["jsonrpc.protocol.version"] = _value(
                jsonrpc_protocol_version
            )
        if method_name is not None:
            typed_attributes[Attr.MCP_METHOD_NAME] = _value(method_name)
        if protocol_version is not None:
            typed_attributes[Attr.MCP_PROTOCOL_VERSION] = _value(
                protocol_version
            )
        if resource_uri is not None:
            typed_attributes[Attr.MCP_RESOURCE_URI] = _value(resource_uri)
        if network_protocol_name is not None:
            typed_attributes["network.protocol.name"] = _value(
                network_protocol_name
            )
        if network_protocol_version is not None:
            typed_attributes["network.protocol.version"] = _value(
                network_protocol_version
            )
        if network_transport is not None:
            typed_attributes["network.transport"] = _value(network_transport)
        if rpc_response_status_code is not None:
            typed_attributes["rpc.response.status_code"] = _value(
                rpc_response_status_code
            )
        if server_address is not None:
            typed_attributes["server.address"] = _value(server_address)
        if server_port is not None:
            typed_attributes["server.port"] = _value(server_port)
        self._client_operation_duration_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _client_operation_duration_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "mcp.client.operation.duration",
            unit="s",
            description="The duration of the MCP request or notification as observed on the sender from the time it was sent until the response or ack is received.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "mcp.client.operation.duration"
            ],
        )

    def client_session_duration(
        self,
        value: float,
        *,
        error_type: str | None = None,
        jsonrpc_protocol_version: str | None = None,
        protocol_version: str | None = None,
        network_protocol_name: str | None = None,
        network_protocol_version: str | None = None,
        network_transport: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `mcp.client.session.duration`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if error_type is not None:
            typed_attributes["error.type"] = _value(error_type)
        if jsonrpc_protocol_version is not None:
            typed_attributes["jsonrpc.protocol.version"] = _value(
                jsonrpc_protocol_version
            )
        if protocol_version is not None:
            typed_attributes[Attr.MCP_PROTOCOL_VERSION] = _value(
                protocol_version
            )
        if network_protocol_name is not None:
            typed_attributes["network.protocol.name"] = _value(
                network_protocol_name
            )
        if network_protocol_version is not None:
            typed_attributes["network.protocol.version"] = _value(
                network_protocol_version
            )
        if network_transport is not None:
            typed_attributes["network.transport"] = _value(network_transport)
        if server_address is not None:
            typed_attributes["server.address"] = _value(server_address)
        if server_port is not None:
            typed_attributes["server.port"] = _value(server_port)
        self._client_session_duration_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _client_session_duration_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "mcp.client.session.duration",
            unit="s",
            description="The duration of the MCP session as observed on the MCP client.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "mcp.client.session.duration"
            ],
        )

    def server_operation_duration(
        self,
        value: float,
        *,
        method_name: Attr.MCPMethodName | str,
        error_type: str | None = None,
        gen_ai_operation_name: str | None = None,
        gen_ai_prompt_name: str | None = None,
        gen_ai_prompt_variable: Mapping[str, object] | None = None,
        gen_ai_tool_name: str | None = None,
        jsonrpc_protocol_version: str | None = None,
        protocol_version: str | None = None,
        resource_uri: str | None = None,
        network_protocol_name: str | None = None,
        network_protocol_version: str | None = None,
        network_transport: str | None = None,
        rpc_response_status_code: str | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `mcp.server.operation.duration`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if error_type is not None:
            typed_attributes["error.type"] = _value(error_type)
        if gen_ai_operation_name is not None:
            typed_attributes["gen_ai.operation.name"] = _value(
                gen_ai_operation_name
            )
        if gen_ai_prompt_name is not None:
            typed_attributes["gen_ai.prompt.name"] = _value(gen_ai_prompt_name)
        if gen_ai_prompt_variable is not None:
            typed_attributes["gen_ai.prompt.variable"] = _value(
                gen_ai_prompt_variable
            )
        if gen_ai_tool_name is not None:
            typed_attributes["gen_ai.tool.name"] = _value(gen_ai_tool_name)
        if jsonrpc_protocol_version is not None:
            typed_attributes["jsonrpc.protocol.version"] = _value(
                jsonrpc_protocol_version
            )
        if method_name is not None:
            typed_attributes[Attr.MCP_METHOD_NAME] = _value(method_name)
        if protocol_version is not None:
            typed_attributes[Attr.MCP_PROTOCOL_VERSION] = _value(
                protocol_version
            )
        if resource_uri is not None:
            typed_attributes[Attr.MCP_RESOURCE_URI] = _value(resource_uri)
        if network_protocol_name is not None:
            typed_attributes["network.protocol.name"] = _value(
                network_protocol_name
            )
        if network_protocol_version is not None:
            typed_attributes["network.protocol.version"] = _value(
                network_protocol_version
            )
        if network_transport is not None:
            typed_attributes["network.transport"] = _value(network_transport)
        if rpc_response_status_code is not None:
            typed_attributes["rpc.response.status_code"] = _value(
                rpc_response_status_code
            )
        self._server_operation_duration_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _server_operation_duration_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "mcp.server.operation.duration",
            unit="s",
            description="MCP request or notification duration as observed on the receiver from the time it was received until the result or ack is sent.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "mcp.server.operation.duration"
            ],
        )

    def server_session_duration(
        self,
        value: float,
        *,
        error_type: str | None = None,
        jsonrpc_protocol_version: str | None = None,
        protocol_version: str | None = None,
        network_protocol_name: str | None = None,
        network_protocol_version: str | None = None,
        network_transport: str | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `mcp.server.session.duration`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if error_type is not None:
            typed_attributes["error.type"] = _value(error_type)
        if jsonrpc_protocol_version is not None:
            typed_attributes["jsonrpc.protocol.version"] = _value(
                jsonrpc_protocol_version
            )
        if protocol_version is not None:
            typed_attributes[Attr.MCP_PROTOCOL_VERSION] = _value(
                protocol_version
            )
        if network_protocol_name is not None:
            typed_attributes["network.protocol.name"] = _value(
                network_protocol_name
            )
        if network_protocol_version is not None:
            typed_attributes["network.protocol.version"] = _value(
                network_protocol_version
            )
        if network_transport is not None:
            typed_attributes["network.transport"] = _value(network_transport)
        self._server_session_duration_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _server_session_duration_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "mcp.server.session.duration",
            unit="s",
            description="The duration of the MCP session as observed on the MCP server.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "mcp.server.session.duration"
            ],
        )


__all__ = ["_Metrics"]
