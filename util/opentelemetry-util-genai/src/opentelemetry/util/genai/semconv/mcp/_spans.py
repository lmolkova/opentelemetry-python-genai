# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
# Code generated from OpenTelemetry GenAI semantic conventions. DO NOT EDIT.

from __future__ import annotations

from enum import Enum

from opentelemetry.context import Context
from opentelemetry.trace import SpanKind, Tracer
from opentelemetry.util.genai.semconv._span import _Span
from opentelemetry.util.genai.semconv.mcp import attributes as Attr
from opentelemetry.util.types import AnyValue, AttributeValue


def _value(value: AttributeValue | Enum) -> AttributeValue:
    return value.value if isinstance(value, Enum) else value


class ClientSpan(_Span):
    """`mcp.client` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_gen_ai_operation_name(self, value: str | None) -> None:
        self._set_attribute("gen_ai.operation.name", value)

    def set_gen_ai_prompt_name(self, value: str | None) -> None:
        self._set_attribute("gen_ai.prompt.name", value)

    def set_prompt_variable(self, name: str, value: str | None) -> None:
        self._set_attribute("gen_ai.prompt.variable" + f".{name}", value)

    def set_gen_ai_tool_call_arguments(self, value: AnyValue | None) -> None:
        self._set_json_attribute("gen_ai.tool.call.arguments", value)

    def set_gen_ai_tool_call_result(self, value: AnyValue | None) -> None:
        self._set_json_attribute("gen_ai.tool.call.result", value)

    def set_gen_ai_tool_name(self, value: str | None) -> None:
        self._set_attribute("gen_ai.tool.name", value)

    def set_jsonrpc_protocol_version(self, value: str | None) -> None:
        self._set_attribute("jsonrpc.protocol.version", value)

    def set_jsonrpc_request_id(self, value: str | None) -> None:
        self._set_attribute("jsonrpc.request.id", value)

    def set_method_name(self, value: Attr.MCPMethodName | str | None) -> None:
        self._set_attribute(Attr.MCP_METHOD_NAME, value)

    def set_protocol_version(self, value: str | None) -> None:
        self._set_attribute(Attr.MCP_PROTOCOL_VERSION, value)

    def set_resource_uri(self, value: str | None) -> None:
        self._set_attribute(Attr.MCP_RESOURCE_URI, value)

    def set_session_id(self, value: str | None) -> None:
        self._set_attribute(Attr.MCP_SESSION_ID, value)

    def set_network_protocol_name(self, value: str | None) -> None:
        self._set_attribute("network.protocol.name", value)

    def set_network_protocol_version(self, value: str | None) -> None:
        self._set_attribute("network.protocol.version", value)

    def set_network_transport(self, value: str | None) -> None:
        self._set_attribute("network.transport", value)

    def set_rpc_response_status_code(self, value: str | None) -> None:
        self._set_attribute("rpc.response.status_code", value)

    def set_server_address(self, value: str | None) -> None:
        self._set_attribute("server.address", value)

    def set_server_port(self, value: int | None) -> None:
        self._set_attribute("server.port", value)


class ServerSpan(_Span):
    """`mcp.server` span."""

    def set_client_address(self, value: str | None) -> None:
        self._set_attribute("client.address", value)

    def set_client_port(self, value: int | None) -> None:
        self._set_attribute("client.port", value)

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_gen_ai_operation_name(self, value: str | None) -> None:
        self._set_attribute("gen_ai.operation.name", value)

    def set_gen_ai_prompt_name(self, value: str | None) -> None:
        self._set_attribute("gen_ai.prompt.name", value)

    def set_prompt_variable(self, name: str, value: str | None) -> None:
        self._set_attribute("gen_ai.prompt.variable" + f".{name}", value)

    def set_gen_ai_tool_call_arguments(self, value: AnyValue | None) -> None:
        self._set_json_attribute("gen_ai.tool.call.arguments", value)

    def set_gen_ai_tool_call_result(self, value: AnyValue | None) -> None:
        self._set_json_attribute("gen_ai.tool.call.result", value)

    def set_gen_ai_tool_name(self, value: str | None) -> None:
        self._set_attribute("gen_ai.tool.name", value)

    def set_jsonrpc_protocol_version(self, value: str | None) -> None:
        self._set_attribute("jsonrpc.protocol.version", value)

    def set_jsonrpc_request_id(self, value: str | None) -> None:
        self._set_attribute("jsonrpc.request.id", value)

    def set_method_name(self, value: Attr.MCPMethodName | str | None) -> None:
        self._set_attribute(Attr.MCP_METHOD_NAME, value)

    def set_protocol_version(self, value: str | None) -> None:
        self._set_attribute(Attr.MCP_PROTOCOL_VERSION, value)

    def set_resource_uri(self, value: str | None) -> None:
        self._set_attribute(Attr.MCP_RESOURCE_URI, value)

    def set_session_id(self, value: str | None) -> None:
        self._set_attribute(Attr.MCP_SESSION_ID, value)

    def set_network_protocol_name(self, value: str | None) -> None:
        self._set_attribute("network.protocol.name", value)

    def set_network_protocol_version(self, value: str | None) -> None:
        self._set_attribute("network.protocol.version", value)

    def set_network_transport(self, value: str | None) -> None:
        self._set_attribute("network.transport", value)

    def set_rpc_response_status_code(self, value: str | None) -> None:
        self._set_attribute("rpc.response.status_code", value)


class _Spans:
    """Creates spans following the mcp semantic conventions."""

    def __init__(self, tracer: Tracer) -> None:
        self._tracer = tracer

    def client(
        self,
        name: str,
        *,
        context: Context | None = None,
    ) -> ClientSpan:
        """Start a `mcp.client` span."""
        attributes: dict[str, AttributeValue] = {}
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return ClientSpan(span)

    def server(
        self,
        name: str,
        *,
        context: Context | None = None,
    ) -> ServerSpan:
        """Start a `mcp.server` span."""
        attributes: dict[str, AttributeValue] = {}
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.SERVER,
            attributes=attributes,
        )
        return ServerSpan(span)


__all__ = ["_Spans"]
