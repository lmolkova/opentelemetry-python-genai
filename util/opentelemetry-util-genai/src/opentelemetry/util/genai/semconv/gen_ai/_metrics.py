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
from opentelemetry.util.genai.semconv.gen_ai import attributes as Attr
from opentelemetry.util.genai.semconv.gen_ai.attribute_sets import (
    EmbeddingsAttributes,
    ExecuteToolAttributes,
    FetchResponseAttributes,
    InferenceAttributes,
    InvokeAgentAttributes,
    InvokeAgentClientAttributes,
    InvokeWorkflowAttributes,
    RetrievalAttributes,
)
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
    """Records metrics following the gen_ai semantic conventions."""

    def __init__(
        self,
        meter: Meter,
        *,
        client_operation_duration_boundaries: Sequence[float] | None = None,
        client_operation_time_per_output_chunk_boundaries: Sequence[float]
        | None = None,
        client_operation_time_to_first_chunk_boundaries: Sequence[float]
        | None = None,
        client_token_usage_boundaries: Sequence[float] | None = None,
        execute_tool_duration_boundaries: Sequence[float] | None = None,
        invoke_agent_duration_boundaries: Sequence[float] | None = None,
        invoke_agent_inference_calls_boundaries: Sequence[float] | None = None,
        invoke_agent_tool_calls_boundaries: Sequence[float] | None = None,
        invoke_workflow_duration_boundaries: Sequence[float] | None = None,
        server_request_duration_boundaries: Sequence[float] | None = None,
        server_time_per_output_token_boundaries: Sequence[float] | None = None,
        server_time_to_first_token_boundaries: Sequence[float] | None = None,
    ) -> None:
        self._meter = meter
        self._boundaries = {
            "gen_ai.client.operation.duration": client_operation_duration_boundaries
            if client_operation_duration_boundaries is not None
            else [
                0.01,
                0.02,
                0.04,
                0.08,
                0.16,
                0.32,
                0.64,
                1.28,
                2.56,
                5.12,
                10.24,
                20.48,
                40.96,
                81.92,
            ],
            "gen_ai.client.operation.time_per_output_chunk": client_operation_time_per_output_chunk_boundaries
            if client_operation_time_per_output_chunk_boundaries is not None
            else [
                0.01,
                0.02,
                0.04,
                0.08,
                0.16,
                0.32,
                0.64,
                1.28,
                2.56,
                5.12,
                10.24,
                20.48,
                40.96,
                81.92,
            ],
            "gen_ai.client.operation.time_to_first_chunk": client_operation_time_to_first_chunk_boundaries
            if client_operation_time_to_first_chunk_boundaries is not None
            else [
                0.01,
                0.02,
                0.04,
                0.08,
                0.16,
                0.32,
                0.64,
                1.28,
                2.56,
                5.12,
                10.24,
                20.48,
                40.96,
                81.92,
            ],
            "gen_ai.client.token.usage": client_token_usage_boundaries
            if client_token_usage_boundaries is not None
            else [
                1,
                4,
                16,
                64,
                256,
                1024,
                4096,
                16384,
                65536,
                262144,
                1048576,
                4194304,
                16777216,
                67108864,
            ],
            "gen_ai.execute_tool.duration": execute_tool_duration_boundaries
            if execute_tool_duration_boundaries is not None
            else [
                0.01,
                0.02,
                0.04,
                0.08,
                0.16,
                0.32,
                0.64,
                1.28,
                2.56,
                5.12,
                10.24,
                20.48,
                40.96,
                81.92,
            ],
            "gen_ai.invoke_agent.duration": invoke_agent_duration_boundaries
            if invoke_agent_duration_boundaries is not None
            else [
                0.1,
                0.2,
                0.4,
                0.8,
                1.6,
                3.2,
                6.4,
                12.8,
                25.6,
                51.2,
                102.4,
                204.8,
                409.6,
            ],
            "gen_ai.invoke_agent.inference_calls": invoke_agent_inference_calls_boundaries,
            "gen_ai.invoke_agent.tool_calls": invoke_agent_tool_calls_boundaries,
            "gen_ai.invoke_workflow.duration": invoke_workflow_duration_boundaries
            if invoke_workflow_duration_boundaries is not None
            else [1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600, 7200],
            "gen_ai.server.request.duration": server_request_duration_boundaries,
            "gen_ai.server.time_per_output_token": server_time_per_output_token_boundaries,
            "gen_ai.server.time_to_first_token": server_time_to_first_token_boundaries,
        }

    def client_operation_duration(
        self,
        value: float,
        attributes: EmbeddingsAttributes
        | FetchResponseAttributes
        | InferenceAttributes
        | InvokeAgentClientAttributes
        | RetrievalAttributes,
        *,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.client.operation.duration` from aggregate attributes."""
        self.client_operation_duration_explicit(
            value,
            error_type=attributes.error_type,
            operation_name=attributes.operation_name,
            provider_name=attributes.provider_name,
            request_model=attributes.request_model,
            response_model=attributes.response_model,
            server_address=attributes.server_address,
            server_port=attributes.server_port,
            additional_attributes=additional_attributes,
            context=context,
        )

    def client_operation_duration_explicit(
        self,
        value: float,
        *,
        operation_name: Attr.GenAIOperationName | str,
        error_type: str | None = None,
        provider_name: Attr.GenAIProviderName | str | None = None,
        request_model: str | None = None,
        response_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.client.operation.duration`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if error_type is not None:
            typed_attributes["error.type"] = _value(error_type)
        if operation_name is not None:
            typed_attributes[Attr.GEN_AI_OPERATION_NAME] = _value(
                operation_name
            )
        if provider_name is not None:
            typed_attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            typed_attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if response_model is not None:
            typed_attributes[Attr.GEN_AI_RESPONSE_MODEL] = _value(
                response_model
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
            "gen_ai.client.operation.duration",
            unit="s",
            description="GenAI operation duration.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.client.operation.duration"
            ],
        )

    def client_operation_time_per_output_chunk(
        self,
        value: float,
        attributes: FetchResponseAttributes
        | InferenceAttributes
        | InvokeAgentClientAttributes,
        *,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.client.operation.time_per_output_chunk` from aggregate attributes."""
        self.client_operation_time_per_output_chunk_explicit(
            value,
            operation_name=attributes.operation_name,
            provider_name=attributes.provider_name,
            request_model=attributes.request_model,
            response_model=attributes.response_model,
            server_address=attributes.server_address,
            server_port=attributes.server_port,
            additional_attributes=additional_attributes,
            context=context,
        )

    def client_operation_time_per_output_chunk_explicit(
        self,
        value: float,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        request_model: str | None = None,
        response_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.client.operation.time_per_output_chunk`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if operation_name is not None:
            typed_attributes[Attr.GEN_AI_OPERATION_NAME] = _value(
                operation_name
            )
        if provider_name is not None:
            typed_attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            typed_attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if response_model is not None:
            typed_attributes[Attr.GEN_AI_RESPONSE_MODEL] = _value(
                response_model
            )
        if server_address is not None:
            typed_attributes["server.address"] = _value(server_address)
        if server_port is not None:
            typed_attributes["server.port"] = _value(server_port)
        self._client_operation_time_per_output_chunk_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _client_operation_time_per_output_chunk_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.client.operation.time_per_output_chunk",
            unit="s",
            description="Time per output chunk, recorded for each chunk received after the first one, measured as the time elapsed from the end of the previous chunk to the end of the current chunk.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.client.operation.time_per_output_chunk"
            ],
        )

    def client_operation_time_to_first_chunk(
        self,
        value: float,
        attributes: FetchResponseAttributes
        | InferenceAttributes
        | InvokeAgentClientAttributes,
        *,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.client.operation.time_to_first_chunk` from aggregate attributes."""
        self.client_operation_time_to_first_chunk_explicit(
            value,
            operation_name=attributes.operation_name,
            provider_name=attributes.provider_name,
            request_model=attributes.request_model,
            response_model=attributes.response_model,
            server_address=attributes.server_address,
            server_port=attributes.server_port,
            additional_attributes=additional_attributes,
            context=context,
        )

    def client_operation_time_to_first_chunk_explicit(
        self,
        value: float,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        request_model: str | None = None,
        response_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.client.operation.time_to_first_chunk`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if operation_name is not None:
            typed_attributes[Attr.GEN_AI_OPERATION_NAME] = _value(
                operation_name
            )
        if provider_name is not None:
            typed_attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            typed_attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if response_model is not None:
            typed_attributes[Attr.GEN_AI_RESPONSE_MODEL] = _value(
                response_model
            )
        if server_address is not None:
            typed_attributes["server.address"] = _value(server_address)
        if server_port is not None:
            typed_attributes["server.port"] = _value(server_port)
        self._client_operation_time_to_first_chunk_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _client_operation_time_to_first_chunk_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.client.operation.time_to_first_chunk",
            unit="s",
            description="Time to receive the first chunk, measured from when the client issues the generation request to when the first chunk is received in the response stream.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.client.operation.time_to_first_chunk"
            ],
        )

    def client_token_usage(
        self,
        value: int,
        attributes: EmbeddingsAttributes
        | InferenceAttributes
        | InvokeAgentClientAttributes,
        *,
        token_type: Attr.GenAITokenType | str,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.client.token.usage` from aggregate attributes."""
        self.client_token_usage_explicit(
            value,
            operation_name=attributes.operation_name,
            provider_name=attributes.provider_name,
            request_model=attributes.request_model,
            response_model=attributes.response_model,
            token_type=token_type,
            server_address=attributes.server_address,
            server_port=attributes.server_port,
            additional_attributes=additional_attributes,
            context=context,
        )

    def client_token_usage_explicit(
        self,
        value: int,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        token_type: Attr.GenAITokenType | str,
        request_model: str | None = None,
        response_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.client.token.usage`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if operation_name is not None:
            typed_attributes[Attr.GEN_AI_OPERATION_NAME] = _value(
                operation_name
            )
        if provider_name is not None:
            typed_attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            typed_attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if response_model is not None:
            typed_attributes[Attr.GEN_AI_RESPONSE_MODEL] = _value(
                response_model
            )
        if token_type is not None:
            typed_attributes[Attr.GEN_AI_TOKEN_TYPE] = _value(token_type)
        if server_address is not None:
            typed_attributes["server.address"] = _value(server_address)
        if server_port is not None:
            typed_attributes["server.port"] = _value(server_port)
        self._client_token_usage_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _client_token_usage_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.client.token.usage",
            unit="{token}",
            description="Number of input and output tokens used.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.client.token.usage"
            ],
        )

    def execute_tool_duration(
        self,
        value: float,
        attributes: ExecuteToolAttributes,
        *,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.execute_tool.duration` from aggregate attributes."""
        self.execute_tool_duration_explicit(
            value,
            error_type=attributes.error_type,
            agent_name=attributes.agent_name,
            tool_name=attributes.tool_name,
            tool_type=attributes.tool_type,
            additional_attributes=additional_attributes,
            context=context,
        )

    def execute_tool_duration_explicit(
        self,
        value: float,
        *,
        tool_name: str,
        error_type: str | None = None,
        agent_name: str | None = None,
        tool_type: str | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.execute_tool.duration`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if error_type is not None:
            typed_attributes["error.type"] = _value(error_type)
        if agent_name is not None:
            typed_attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        if tool_name is not None:
            typed_attributes[Attr.GEN_AI_TOOL_NAME] = _value(tool_name)
        if tool_type is not None:
            typed_attributes[Attr.GEN_AI_TOOL_TYPE] = _value(tool_type)
        self._execute_tool_duration_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _execute_tool_duration_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.execute_tool.duration",
            unit="s",
            description="The duration of a single tool execution.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.execute_tool.duration"
            ],
        )

    def invoke_agent_duration(
        self,
        value: float,
        attributes: InvokeAgentAttributes,
        *,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.invoke_agent.duration` from aggregate attributes."""
        self.invoke_agent_duration_explicit(
            value,
            error_type=attributes.error_type,
            agent_name=attributes.agent_name,
            request_model=attributes.request_model,
            additional_attributes=additional_attributes,
            context=context,
        )

    def invoke_agent_duration_explicit(
        self,
        value: float,
        *,
        error_type: str | None = None,
        agent_name: str | None = None,
        request_model: str | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.invoke_agent.duration`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if error_type is not None:
            typed_attributes["error.type"] = _value(error_type)
        if agent_name is not None:
            typed_attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        if request_model is not None:
            typed_attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        self._invoke_agent_duration_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _invoke_agent_duration_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.invoke_agent.duration",
            unit="s",
            description="The end-to-end duration of a single in-process agent invocation, from the moment the invocation starts until the agent emits the last chunk of its final response or terminates with an error.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.invoke_agent.duration"
            ],
        )

    def invoke_agent_inference_calls(
        self,
        value: int,
        attributes: InvokeAgentAttributes,
        *,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.invoke_agent.inference_calls` from aggregate attributes."""
        self.invoke_agent_inference_calls_explicit(
            value,
            agent_name=attributes.agent_name,
            additional_attributes=additional_attributes,
            context=context,
        )

    def invoke_agent_inference_calls_explicit(
        self,
        value: int,
        *,
        agent_name: str | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.invoke_agent.inference_calls`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if agent_name is not None:
            typed_attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        self._invoke_agent_inference_calls_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _invoke_agent_inference_calls_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.invoke_agent.inference_calls",
            unit="{inference_call}",
            description="The number of inference (model) calls a GenAI agent makes during a single invocation.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.invoke_agent.inference_calls"
            ],
        )

    def invoke_agent_tool_calls(
        self,
        value: int,
        attributes: InvokeAgentAttributes,
        *,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.invoke_agent.tool_calls` from aggregate attributes."""
        self.invoke_agent_tool_calls_explicit(
            value,
            agent_name=attributes.agent_name,
            additional_attributes=additional_attributes,
            context=context,
        )

    def invoke_agent_tool_calls_explicit(
        self,
        value: int,
        *,
        agent_name: str | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.invoke_agent.tool_calls`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if agent_name is not None:
            typed_attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        self._invoke_agent_tool_calls_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _invoke_agent_tool_calls_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.invoke_agent.tool_calls",
            unit="{tool_call}",
            description="The number of tool calls a GenAI agent makes during a single invocation.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.invoke_agent.tool_calls"
            ],
        )

    def invoke_workflow_duration(
        self,
        value: float,
        attributes: InvokeWorkflowAttributes,
        *,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.invoke_workflow.duration` from aggregate attributes."""
        self.invoke_workflow_duration_explicit(
            value,
            error_type=attributes.error_type,
            workflow_name=attributes.workflow_name,
            additional_attributes=additional_attributes,
            context=context,
        )

    def invoke_workflow_duration_explicit(
        self,
        value: float,
        *,
        error_type: str | None = None,
        workflow_name: str | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.invoke_workflow.duration`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if error_type is not None:
            typed_attributes["error.type"] = _value(error_type)
        if workflow_name is not None:
            typed_attributes[Attr.GEN_AI_WORKFLOW_NAME] = _value(workflow_name)
        self._invoke_workflow_duration_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _invoke_workflow_duration_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.invoke_workflow.duration",
            unit="s",
            description="Records duration of GenAI workflow.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.invoke_workflow.duration"
            ],
        )

    def server_request_duration(
        self,
        value: float,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        error_type: str | None = None,
        request_model: str | None = None,
        response_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.server.request.duration`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if error_type is not None:
            typed_attributes["error.type"] = _value(error_type)
        if operation_name is not None:
            typed_attributes[Attr.GEN_AI_OPERATION_NAME] = _value(
                operation_name
            )
        if provider_name is not None:
            typed_attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            typed_attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if response_model is not None:
            typed_attributes[Attr.GEN_AI_RESPONSE_MODEL] = _value(
                response_model
            )
        if server_address is not None:
            typed_attributes["server.address"] = _value(server_address)
        if server_port is not None:
            typed_attributes["server.port"] = _value(server_port)
        self._server_request_duration_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _server_request_duration_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.server.request.duration",
            unit="s",
            description="Generative AI server request duration such as time-to-last byte or last output token.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.server.request.duration"
            ],
        )

    def server_time_per_output_token(
        self,
        value: float,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        request_model: str | None = None,
        response_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.server.time_per_output_token`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if operation_name is not None:
            typed_attributes[Attr.GEN_AI_OPERATION_NAME] = _value(
                operation_name
            )
        if provider_name is not None:
            typed_attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            typed_attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if response_model is not None:
            typed_attributes[Attr.GEN_AI_RESPONSE_MODEL] = _value(
                response_model
            )
        if server_address is not None:
            typed_attributes["server.address"] = _value(server_address)
        if server_port is not None:
            typed_attributes["server.port"] = _value(server_port)
        self._server_time_per_output_token_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _server_time_per_output_token_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.server.time_per_output_token",
            unit="s",
            description="Time per output token generated after the first token for successful responses.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.server.time_per_output_token"
            ],
        )

    def server_time_to_first_token(
        self,
        value: float,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        request_model: str | None = None,
        response_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        additional_attributes: Mapping[str, AttributeValue] | None = None,
        context: Context | None = None,
    ) -> None:
        """Record `gen_ai.server.time_to_first_token`."""
        typed_attributes: dict[str, AttributeValue] = {}
        if operation_name is not None:
            typed_attributes[Attr.GEN_AI_OPERATION_NAME] = _value(
                operation_name
            )
        if provider_name is not None:
            typed_attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            typed_attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if response_model is not None:
            typed_attributes[Attr.GEN_AI_RESPONSE_MODEL] = _value(
                response_model
            )
        if server_address is not None:
            typed_attributes["server.address"] = _value(server_address)
        if server_port is not None:
            typed_attributes["server.port"] = _value(server_port)
        self._server_time_to_first_token_instrument.record(
            value,
            attributes=_combine_attributes(
                typed_attributes, additional_attributes
            ),
            context=context,
        )

    @cached_property
    def _server_time_to_first_token_instrument(self) -> Histogram:
        return self._meter.create_histogram(
            "gen_ai.server.time_to_first_token",
            unit="s",
            description="Time to generate first token for successful responses.",
            explicit_bucket_boundaries_advisory=self._boundaries[
                "gen_ai.server.time_to_first_token"
            ],
        )


__all__ = ["_Metrics"]
