# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
# Code generated from OpenTelemetry GenAI semantic conventions. DO NOT EDIT.

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict
from enum import Enum

from opentelemetry.context import Context
from opentelemetry.semconv.attributes import (
    server_attributes as ServerAttributes,
)
from opentelemetry.trace import SpanKind, Tracer
from opentelemetry.util.genai.semconv.gen_ai import attributes as Attr
from opentelemetry.util.genai.semconv.gen_ai._span import GenAISpan
from opentelemetry.util.genai.semconv.gen_ai.attributes import (
    GenAiOperationName,
    GenAiOutputType,
    GenAiProviderName,
    GenAiResponseStatus,
)
from opentelemetry.util.genai.types import (
    InputMessage,
    OutputMessage,
    SystemInstructionPart,
    ToolDefinition,
)
from opentelemetry.util.types import AnyValue, AttributeValue


def _value(value: AttributeValue | Enum) -> AttributeValue:
    return value.value if isinstance(value, Enum) else value


class InferenceSpan(GenAISpan):
    """`gen_ai.inference.client` span."""

    def set_usage_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_INPUT_TOKENS, value)

    def set_usage_output_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_OUTPUT_TOKENS, value)

    def set_usage_text_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_TEXT_INPUT_TOKENS, value)

    def set_usage_image_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_IMAGE_INPUT_TOKENS, value)

    def set_usage_audio_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_AUDIO_INPUT_TOKENS, value)

    def set_usage_text_cache_read_input_tokens(self, value: int) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_TEXT_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_image_cache_read_input_tokens(self, value: int) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_IMAGE_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_audio_cache_read_input_tokens(self, value: int) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_AUDIO_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_text_output_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_TEXT_OUTPUT_TOKENS, value)

    def set_usage_image_output_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_IMAGE_OUTPUT_TOKENS, value)

    def set_usage_audio_output_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_AUDIO_OUTPUT_TOKENS, value)

    def set_usage_cache_read_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS, value)

    def set_usage_cache_write_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_CACHE_WRITE_INPUT_TOKENS, value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart]
    ) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_SYSTEM_INSTRUCTIONS, [asdict(item) for item in value]
        )

    def set_input_messages(self, value: Sequence[InputMessage]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_INPUT_MESSAGES, [asdict(item) for item in value]
        )

    def set_output_messages(self, value: Sequence[OutputMessage]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_OUTPUT_MESSAGES, [asdict(item) for item in value]
        )

    def set_tool_definitions(self, value: Sequence[ToolDefinition]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_TOOL_DEFINITIONS, [asdict(item) for item in value]
        )

    def set_request_max_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MAX_TOKENS, value)

    def set_request_choice_count(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_CHOICE_COUNT, value)

    def set_request_temperature(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TEMPERATURE, value)

    def set_request_top_k(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TOP_K, value)

    def set_request_top_p(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TOP_P, value)

    def set_request_stop_sequences(self, value: Sequence[str]) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_STOP_SEQUENCES, value)

    def set_request_frequency_penalty(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_FREQUENCY_PENALTY, value)

    def set_request_presence_penalty(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_PRESENCE_PENALTY, value)

    def set_request_seed(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_SEED, value)

    def set_output_type(self, value: GenAiOutputType | str) -> None:
        self._set_attribute(Attr.GEN_AI_OUTPUT_TYPE, value)

    def set_request_stream(self, value: bool) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_STREAM, value)

    def set_request_reasoning_level(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_REASONING_LEVEL, value)

    def set_request_previous_response_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_PREVIOUS_RESPONSE_ID, value)

    def set_response_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_ID, value)

    def set_response_model(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_MODEL, value)

    def set_response_finish_reasons(self, value: Sequence[str]) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_FINISH_REASONS, value)

    def set_response_time_to_first_chunk(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK, value)

    def set_usage_reasoning_output_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_REASONING_OUTPUT_TOKENS, value)

    def set_prompt_name(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_PROMPT_NAME, value)

    def set_prompt_version(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_PROMPT_VERSION, value)

    def set_prompt_variable(self, name: str, value: str) -> None:
        self._set_attribute(f"{Attr.GEN_AI_PROMPT_VARIABLE}.{name}", value)

    def set_conversation_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_CONVERSATION_ID, value)

    def set_conversation_compacted(self, value: bool) -> None:
        self._set_attribute(Attr.GEN_AI_CONVERSATION_COMPACTED, value)


class EmbeddingsSpan(GenAISpan):
    """`gen_ai.embeddings.client` span."""

    def set_request_encoding_formats(self, value: Sequence[str]) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_ENCODING_FORMATS, value)

    def set_usage_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_INPUT_TOKENS, value)

    def set_embeddings_dimension_count(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_EMBEDDINGS_DIMENSION_COUNT, value)

    def set_response_model(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_MODEL, value)


class RetrievalSpan(GenAISpan):
    """`gen_ai.retrieval.client` span."""

    def set_request_model(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MODEL, value)

    def set_operation_name(self, value: GenAiOperationName | str) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_server_address(self, value: str) -> None:
        self._set_attribute(ServerAttributes.SERVER_ADDRESS, value)

    def set_server_port(self, value: int) -> None:
        self._set_attribute(ServerAttributes.SERVER_PORT, value)

    def set_retrieval_query_text(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_RETRIEVAL_QUERY_TEXT, value)

    def set_retrieval_top_k(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_RETRIEVAL_TOP_K, value)

    def set_retrieval_documents(self, value: AnyValue) -> None:
        self._set_json_attribute(Attr.GEN_AI_RETRIEVAL_DOCUMENTS, value)

    def set_provider_name(self, value: GenAiProviderName | str) -> None:
        self._set_attribute(Attr.GEN_AI_PROVIDER_NAME, value)

    def set_data_source_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_DATA_SOURCE_ID, value)


class FetchResponseSpan(GenAISpan):
    """`gen_ai.fetch_response.client` span."""

    def set_response_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_ID, value)

    def set_request_stream_cursor(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_STREAM_CURSOR, value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart]
    ) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_SYSTEM_INSTRUCTIONS, [asdict(item) for item in value]
        )

    def set_output_messages(self, value: Sequence[OutputMessage]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_OUTPUT_MESSAGES, [asdict(item) for item in value]
        )

    def set_tool_definitions(self, value: Sequence[ToolDefinition]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_TOOL_DEFINITIONS, [asdict(item) for item in value]
        )

    def set_response_model(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_MODEL, value)

    def set_response_status(self, value: GenAiResponseStatus | str) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_STATUS, value)

    def set_response_finish_reasons(self, value: Sequence[str]) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_FINISH_REASONS, value)


class MemorySpan(GenAISpan):
    """`gen_ai.memory.client` span."""

    def set_operation_name(self, value: GenAiOperationName | str) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_server_address(self, value: str) -> None:
        self._set_attribute(ServerAttributes.SERVER_ADDRESS, value)

    def set_server_port(self, value: int) -> None:
        self._set_attribute(ServerAttributes.SERVER_PORT, value)

    def set_provider_name(self, value: GenAiProviderName | str) -> None:
        self._set_attribute(Attr.GEN_AI_PROVIDER_NAME, value)

    def set_memory_store_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_MEMORY_STORE_ID, value)

    def set_memory_record_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_MEMORY_RECORD_ID, value)

    def set_memory_record_count(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_MEMORY_RECORD_COUNT, value)

    def set_memory_query_text(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_MEMORY_QUERY_TEXT, value)

    def set_memory_records(self, value: AnyValue) -> None:
        self._set_json_attribute(Attr.GEN_AI_MEMORY_RECORDS, value)


class CreateAgentSpan(GenAISpan):
    """`gen_ai.create_agent.client` span."""

    def set_agent_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_ID, value)

    def set_agent_description(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_DESCRIPTION, value)

    def set_agent_version(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_VERSION, value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart]
    ) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_SYSTEM_INSTRUCTIONS, [asdict(item) for item in value]
        )


class InvokeAgentClientSpan(GenAISpan):
    """`gen_ai.invoke_agent.client` span."""

    def set_usage_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_INPUT_TOKENS, value)

    def set_usage_output_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_OUTPUT_TOKENS, value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart]
    ) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_SYSTEM_INSTRUCTIONS, [asdict(item) for item in value]
        )

    def set_input_messages(self, value: Sequence[InputMessage]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_INPUT_MESSAGES, [asdict(item) for item in value]
        )

    def set_output_messages(self, value: Sequence[OutputMessage]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_OUTPUT_MESSAGES, [asdict(item) for item in value]
        )

    def set_tool_definitions(self, value: Sequence[ToolDefinition]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_TOOL_DEFINITIONS, [asdict(item) for item in value]
        )

    def set_request_max_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MAX_TOKENS, value)

    def set_request_choice_count(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_CHOICE_COUNT, value)

    def set_request_temperature(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TEMPERATURE, value)

    def set_request_top_p(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TOP_P, value)

    def set_request_stop_sequences(self, value: Sequence[str]) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_STOP_SEQUENCES, value)

    def set_request_frequency_penalty(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_FREQUENCY_PENALTY, value)

    def set_request_presence_penalty(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_PRESENCE_PENALTY, value)

    def set_request_seed(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_SEED, value)

    def set_output_type(self, value: GenAiOutputType | str) -> None:
        self._set_attribute(Attr.GEN_AI_OUTPUT_TYPE, value)

    def set_response_finish_reasons(self, value: Sequence[str]) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_FINISH_REASONS, value)

    def set_conversation_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_CONVERSATION_ID, value)

    def set_data_source_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_DATA_SOURCE_ID, value)

    def set_agent_description(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_DESCRIPTION, value)

    def set_usage_text_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_TEXT_INPUT_TOKENS, value)

    def set_usage_image_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_IMAGE_INPUT_TOKENS, value)

    def set_usage_audio_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_AUDIO_INPUT_TOKENS, value)

    def set_usage_text_cache_read_input_tokens(self, value: int) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_TEXT_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_image_cache_read_input_tokens(self, value: int) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_IMAGE_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_audio_cache_read_input_tokens(self, value: int) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_AUDIO_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_text_output_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_TEXT_OUTPUT_TOKENS, value)

    def set_usage_image_output_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_IMAGE_OUTPUT_TOKENS, value)

    def set_usage_audio_output_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_AUDIO_OUTPUT_TOKENS, value)

    def set_usage_cache_read_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS, value)

    def set_usage_cache_write_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_CACHE_WRITE_INPUT_TOKENS, value)

    def set_request_previous_response_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_PREVIOUS_RESPONSE_ID, value)

    def set_agent_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_ID, value)

    def set_agent_version(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_VERSION, value)


class InvokeAgentSpan(GenAISpan):
    """`gen_ai.invoke_agent.internal` span."""

    def set_usage_input_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_INPUT_TOKENS, value)

    def set_usage_output_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_OUTPUT_TOKENS, value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart]
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_SYSTEM_INSTRUCTIONS, value)

    def set_input_messages(self, value: Sequence[InputMessage]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_INPUT_MESSAGES, [asdict(item) for item in value]
        )

    def set_output_messages(self, value: Sequence[OutputMessage]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_OUTPUT_MESSAGES, [asdict(item) for item in value]
        )

    def set_tool_definitions(self, value: Sequence[ToolDefinition]) -> None:
        self._set_json_attribute(
            Attr.GEN_AI_TOOL_DEFINITIONS, [asdict(item) for item in value]
        )

    def set_request_max_tokens(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MAX_TOKENS, value)

    def set_request_choice_count(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_CHOICE_COUNT, value)

    def set_request_temperature(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TEMPERATURE, value)

    def set_request_top_p(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TOP_P, value)

    def set_request_stop_sequences(self, value: Sequence[str]) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_STOP_SEQUENCES, value)

    def set_request_frequency_penalty(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_FREQUENCY_PENALTY, value)

    def set_request_presence_penalty(self, value: float) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_PRESENCE_PENALTY, value)

    def set_request_seed(self, value: int) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_SEED, value)

    def set_output_type(self, value: GenAiOutputType | str) -> None:
        self._set_attribute(Attr.GEN_AI_OUTPUT_TYPE, value)

    def set_response_finish_reasons(self, value: Sequence[str]) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_FINISH_REASONS, value)

    def set_conversation_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_CONVERSATION_ID, value)

    def set_data_source_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_DATA_SOURCE_ID, value)

    def set_agent_description(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_DESCRIPTION, value)


class ExecuteToolSpan(GenAISpan):
    """`gen_ai.execute_tool.internal` span."""

    def set_tool_call_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_TOOL_CALL_ID, value)

    def set_tool_description(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_TOOL_DESCRIPTION, value)

    def set_tool_call_arguments(self, value: AnyValue) -> None:
        self._set_json_attribute(Attr.GEN_AI_TOOL_CALL_ARGUMENTS, value)

    def set_tool_call_result(self, value: AnyValue) -> None:
        self._set_json_attribute(Attr.GEN_AI_TOOL_CALL_RESULT, value)


class InvokeWorkflowSpan(GenAISpan):
    """`gen_ai.invoke_workflow.internal` span."""

    def set_workflow_name(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_WORKFLOW_NAME, value)

    def set_conversation_id(self, value: str) -> None:
        self._set_attribute(Attr.GEN_AI_CONVERSATION_ID, value)

    def set_input_messages(self, value: Sequence[InputMessage]) -> None:
        self._set_json_attribute(Attr.GEN_AI_INPUT_MESSAGES, value)

    def set_output_messages(self, value: Sequence[OutputMessage]) -> None:
        self._set_json_attribute(Attr.GEN_AI_OUTPUT_MESSAGES, value)


class PlanSpan(GenAISpan):
    """`gen_ai.plan.internal` span."""


class _Spans:
    """Creates spans following the GenAI semantic conventions."""

    def __init__(self, tracer: Tracer) -> None:
        self._tracer = tracer

    def inference(
        self,
        name: str,
        *,
        operation_name: GenAiOperationName | str,
        provider_name: GenAiProviderName | str,
        request_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        context: Context | None = None,
    ) -> InferenceSpan:
        """Start a `gen_ai.inference.client` span."""
        attributes: dict[str, AttributeValue] = {}
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if server_address is not None:
            attributes[ServerAttributes.SERVER_ADDRESS] = _value(
                server_address
            )
        if server_port is not None:
            attributes[ServerAttributes.SERVER_PORT] = _value(server_port)
        attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return InferenceSpan(span)

    def embeddings(
        self,
        name: str,
        *,
        operation_name: GenAiOperationName | str,
        provider_name: GenAiProviderName | str,
        request_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        context: Context | None = None,
    ) -> EmbeddingsSpan:
        """Start a `gen_ai.embeddings.client` span."""
        attributes: dict[str, AttributeValue] = {}
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if server_address is not None:
            attributes[ServerAttributes.SERVER_ADDRESS] = _value(
                server_address
            )
        if server_port is not None:
            attributes[ServerAttributes.SERVER_PORT] = _value(server_port)
        attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return EmbeddingsSpan(span)

    def retrieval(
        self,
        name: str,
        *,
        operation_name: GenAiOperationName | str,
        data_source_id: str | None = None,
        provider_name: GenAiProviderName | str | None = None,
        request_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        context: Context | None = None,
    ) -> RetrievalSpan:
        """Start a `gen_ai.retrieval.client` span."""
        attributes: dict[str, AttributeValue] = {
            Attr.GEN_AI_OPERATION_NAME: _value(operation_name)
        }
        if data_source_id is not None:
            attributes[Attr.GEN_AI_DATA_SOURCE_ID] = _value(data_source_id)
        if provider_name is not None:
            attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if server_address is not None:
            attributes[ServerAttributes.SERVER_ADDRESS] = _value(
                server_address
            )
        if server_port is not None:
            attributes[ServerAttributes.SERVER_PORT] = _value(server_port)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return RetrievalSpan(span)

    def fetch_response(
        self,
        name: str,
        *,
        operation_name: GenAiOperationName | str,
        provider_name: GenAiProviderName | str,
        response_id: str,
        request_stream: bool | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        context: Context | None = None,
    ) -> FetchResponseSpan:
        """Start a `gen_ai.fetch_response.client` span."""
        attributes: dict[str, AttributeValue] = {}
        if server_address is not None:
            attributes[ServerAttributes.SERVER_ADDRESS] = _value(
                server_address
            )
        if server_port is not None:
            attributes[ServerAttributes.SERVER_PORT] = _value(server_port)
        attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        attributes[Attr.GEN_AI_RESPONSE_ID] = _value(response_id)
        if request_stream is not None:
            attributes[Attr.GEN_AI_REQUEST_STREAM] = _value(request_stream)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return FetchResponseSpan(span)

    def memory(
        self,
        name: str,
        *,
        context: Context | None = None,
    ) -> MemorySpan:
        """Start a `gen_ai.memory.client` span."""
        attributes: dict[str, AttributeValue] = {}
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return MemorySpan(span)

    def create_agent(
        self,
        name: str,
        *,
        operation_name: GenAiOperationName | str,
        provider_name: GenAiProviderName | str,
        request_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        agent_name: str | None = None,
        context: Context | None = None,
    ) -> CreateAgentSpan:
        """Start a `gen_ai.create_agent.client` span."""
        attributes: dict[str, AttributeValue] = {}
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if server_address is not None:
            attributes[ServerAttributes.SERVER_ADDRESS] = _value(
                server_address
            )
        if server_port is not None:
            attributes[ServerAttributes.SERVER_PORT] = _value(server_port)
        attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if agent_name is not None:
            attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return CreateAgentSpan(span)

    def invoke_agent_client(
        self,
        name: str,
        *,
        operation_name: GenAiOperationName | str,
        provider_name: GenAiProviderName | str,
        agent_name: str | None = None,
        request_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        context: Context | None = None,
    ) -> InvokeAgentClientSpan:
        """Start a `gen_ai.invoke_agent.client` span."""
        attributes: dict[str, AttributeValue] = {}
        if agent_name is not None:
            attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if server_address is not None:
            attributes[ServerAttributes.SERVER_ADDRESS] = _value(
                server_address
            )
        if server_port is not None:
            attributes[ServerAttributes.SERVER_PORT] = _value(server_port)
        attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return InvokeAgentClientSpan(span)

    def invoke_agent(
        self,
        name: str,
        *,
        operation_name: GenAiOperationName | str,
        agent_name: str | None = None,
        request_model: str | None = None,
        context: Context | None = None,
    ) -> InvokeAgentSpan:
        """Start a `gen_ai.invoke_agent.internal` span."""
        attributes: dict[str, AttributeValue] = {}
        if agent_name is not None:
            attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )
        return InvokeAgentSpan(span)

    def execute_tool(
        self,
        name: str,
        *,
        tool_name: str,
        operation_name: GenAiOperationName | str,
        tool_type: str | None = None,
        agent_name: str | None = None,
        context: Context | None = None,
    ) -> ExecuteToolSpan:
        """Start a `gen_ai.execute_tool.internal` span."""
        attributes: dict[str, AttributeValue] = {}
        attributes[Attr.GEN_AI_TOOL_NAME] = _value(tool_name)
        if tool_type is not None:
            attributes[Attr.GEN_AI_TOOL_TYPE] = _value(tool_type)
        if agent_name is not None:
            attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )
        return ExecuteToolSpan(span)

    def invoke_workflow(
        self,
        name: str,
        *,
        operation_name: GenAiOperationName | str,
        workflow_name: str | None = None,
        context: Context | None = None,
    ) -> InvokeWorkflowSpan:
        """Start a `gen_ai.invoke_workflow.internal` span."""
        attributes: dict[str, AttributeValue] = {}
        attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if workflow_name is not None:
            attributes[Attr.GEN_AI_WORKFLOW_NAME] = _value(workflow_name)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )
        return InvokeWorkflowSpan(span)

    def plan(
        self,
        name: str,
        *,
        operation_name: GenAiOperationName | str,
        agent_name: str | None = None,
        context: Context | None = None,
    ) -> PlanSpan:
        """Start a `gen_ai.plan.internal` span."""
        attributes: dict[str, AttributeValue] = {}
        attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if agent_name is not None:
            attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )
        return PlanSpan(span)


__all__ = ["_Spans"]
