# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
# Code generated from OpenTelemetry GenAI semantic conventions. DO NOT EDIT.

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum

from opentelemetry.context import Context
from opentelemetry.trace import SpanKind, Tracer
from opentelemetry.util.genai.semconv._span import _Span
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
from opentelemetry.util.genai.types import (
    InputMessage,
    OutputMessage,
    SystemInstructionPart,
    ToolDefinition,
)
from opentelemetry.util.types import AnyValue, AttributeValue


def _value(value: AttributeValue | Enum) -> AttributeValue:
    return value.value if isinstance(value, Enum) else value


class CreateAgentSpan(_Span):
    """`gen_ai.create_agent.client` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_agent_description(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_DESCRIPTION, value)

    def set_agent_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_ID, value)

    def set_agent_name(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_NAME, value)

    def set_agent_version(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_VERSION, value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_provider_name(
        self, value: Attr.GenAIProviderName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_PROVIDER_NAME, value)

    def set_request_model(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MODEL, value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_SYSTEM_INSTRUCTIONS, value)

    def set_server_address(self, value: str | None) -> None:
        self._set_attribute("server.address", value)

    def set_server_port(self, value: int | None) -> None:
        self._set_attribute("server.port", value)


class EmbeddingsSpan(_Span):
    """`gen_ai.embeddings.client` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_embeddings_dimension_count(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_EMBEDDINGS_DIMENSION_COUNT, value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_provider_name(
        self, value: Attr.GenAIProviderName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_PROVIDER_NAME, value)

    def set_request_encoding_formats(
        self, value: Sequence[str] | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_ENCODING_FORMATS, value)

    def set_request_model(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MODEL, value)

    def set_response_model(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_MODEL, value)

    def set_usage_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_INPUT_TOKENS, value)

    def set_server_address(self, value: str | None) -> None:
        self._set_attribute("server.address", value)

    def set_server_port(self, value: int | None) -> None:
        self._set_attribute("server.port", value)

    def apply(self, attributes: EmbeddingsAttributes) -> None:
        """Apply attributes that are not fixed at span creation."""
        self.set_error_type(attributes.error_type)
        self.set_embeddings_dimension_count(
            attributes.embeddings_dimension_count
        )
        self.set_request_encoding_formats(attributes.request_encoding_formats)
        self.set_response_model(attributes.response_model)
        self.set_usage_input_tokens(attributes.usage_input_tokens)


class ExecuteToolSpan(_Span):
    """`gen_ai.execute_tool.internal` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_agent_name(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_NAME, value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_tool_call_arguments(self, value: AnyValue | None) -> None:
        self._set_json_attribute(Attr.GEN_AI_TOOL_CALL_ARGUMENTS, value)

    def set_tool_call_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_TOOL_CALL_ID, value)

    def set_tool_call_result(self, value: AnyValue | None) -> None:
        self._set_json_attribute(Attr.GEN_AI_TOOL_CALL_RESULT, value)

    def set_tool_description(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_TOOL_DESCRIPTION, value)

    def set_tool_name(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_TOOL_NAME, value)

    def set_tool_type(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_TOOL_TYPE, value)

    def apply(self, attributes: ExecuteToolAttributes) -> None:
        """Apply attributes that are not fixed at span creation."""
        self.set_error_type(attributes.error_type)
        self.set_tool_call_id(attributes.tool_call_id)
        self.set_tool_description(attributes.tool_description)


class FetchResponseSpan(_Span):
    """`gen_ai.fetch_response.client` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_output_messages(
        self, value: Sequence[OutputMessage] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_OUTPUT_MESSAGES, value)

    def set_provider_name(
        self, value: Attr.GenAIProviderName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_PROVIDER_NAME, value)

    def set_request_stream_cursor(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_STREAM_CURSOR, value)

    def set_response_finish_reasons(self, value: Sequence[str] | None) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_FINISH_REASONS, value)

    def set_response_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_ID, value)

    def set_response_model(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_MODEL, value)

    def set_response_status(
        self, value: Attr.GenAIResponseStatus | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_STATUS, value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_SYSTEM_INSTRUCTIONS, value)

    def set_tool_definitions(
        self, value: Sequence[ToolDefinition] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_TOOL_DEFINITIONS, value)

    def set_server_address(self, value: str | None) -> None:
        self._set_attribute("server.address", value)

    def set_server_port(self, value: int | None) -> None:
        self._set_attribute("server.port", value)

    def apply(self, attributes: FetchResponseAttributes) -> None:
        """Apply attributes that are not fixed at span creation."""
        self.set_error_type(attributes.error_type)
        self.set_request_stream_cursor(attributes.request_stream_cursor)
        self.set_response_finish_reasons(attributes.response_finish_reasons)
        self.set_response_id(attributes.response_id)
        self.set_response_model(attributes.response_model)
        self.set_response_status(attributes.response_status)


class InferenceSpan(_Span):
    """`gen_ai.inference.client` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_conversation_compacted(self, value: bool | None) -> None:
        self._set_attribute(Attr.GEN_AI_CONVERSATION_COMPACTED, value)

    def set_conversation_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_CONVERSATION_ID, value)

    def set_input_messages(self, value: Sequence[InputMessage] | None) -> None:
        self._set_json_attribute(Attr.GEN_AI_INPUT_MESSAGES, value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_output_messages(
        self, value: Sequence[OutputMessage] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_OUTPUT_MESSAGES, value)

    def set_output_type(
        self, value: Attr.GenAIOutputType | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OUTPUT_TYPE, value)

    def set_prompt_name(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_PROMPT_NAME, value)

    def set_prompt_variable(self, name: str, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_PROMPT_VARIABLE + f".{name}", value)

    def set_prompt_version(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_PROMPT_VERSION, value)

    def set_provider_name(
        self, value: Attr.GenAIProviderName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_PROVIDER_NAME, value)

    def set_request_choice_count(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_CHOICE_COUNT, value)

    def set_request_frequency_penalty(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_FREQUENCY_PENALTY, value)

    def set_request_max_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MAX_TOKENS, value)

    def set_request_model(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MODEL, value)

    def set_request_presence_penalty(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_PRESENCE_PENALTY, value)

    def set_request_previous_response_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_PREVIOUS_RESPONSE_ID, value)

    def set_request_reasoning_level(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_REASONING_LEVEL, value)

    def set_request_seed(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_SEED, value)

    def set_request_stop_sequences(self, value: Sequence[str] | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_STOP_SEQUENCES, value)

    def set_request_stream(self, value: bool | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_STREAM, value)

    def set_request_temperature(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TEMPERATURE, value)

    def set_request_top_k(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TOP_K, value)

    def set_request_top_p(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TOP_P, value)

    def set_response_finish_reasons(self, value: Sequence[str] | None) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_FINISH_REASONS, value)

    def set_response_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_ID, value)

    def set_response_model(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_MODEL, value)

    def set_response_time_to_first_chunk(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK, value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_SYSTEM_INSTRUCTIONS, value)

    def set_tool_definitions(
        self, value: Sequence[ToolDefinition] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_TOOL_DEFINITIONS, value)

    def set_usage_audio_cache_read_input_tokens(
        self, value: int | None
    ) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_AUDIO_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_audio_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_AUDIO_INPUT_TOKENS, value)

    def set_usage_audio_output_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_AUDIO_OUTPUT_TOKENS, value)

    def set_usage_cache_read_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS, value)

    def set_usage_cache_write_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_CACHE_WRITE_INPUT_TOKENS, value)

    def set_usage_image_cache_read_input_tokens(
        self, value: int | None
    ) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_IMAGE_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_image_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_IMAGE_INPUT_TOKENS, value)

    def set_usage_image_output_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_IMAGE_OUTPUT_TOKENS, value)

    def set_usage_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_INPUT_TOKENS, value)

    def set_usage_output_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_OUTPUT_TOKENS, value)

    def set_usage_reasoning_output_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_REASONING_OUTPUT_TOKENS, value)

    def set_usage_text_cache_read_input_tokens(
        self, value: int | None
    ) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_TEXT_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_text_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_TEXT_INPUT_TOKENS, value)

    def set_usage_text_output_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_TEXT_OUTPUT_TOKENS, value)

    def set_server_address(self, value: str | None) -> None:
        self._set_attribute("server.address", value)

    def set_server_port(self, value: int | None) -> None:
        self._set_attribute("server.port", value)

    def apply(self, attributes: InferenceAttributes) -> None:
        """Apply attributes that are not fixed at span creation."""
        self.set_error_type(attributes.error_type)
        self.set_conversation_compacted(
            attributes.conversation_compacted or None
        )
        self.set_conversation_id(attributes.conversation_id)
        self.set_output_type(attributes.output_type)
        self.set_prompt_name(attributes.prompt_name)
        self.set_prompt_version(attributes.prompt_version)
        self.set_request_choice_count(attributes.request_choice_count)
        self.set_request_frequency_penalty(
            attributes.request_frequency_penalty
        )
        self.set_request_max_tokens(attributes.request_max_tokens)
        self.set_request_presence_penalty(attributes.request_presence_penalty)
        self.set_request_previous_response_id(
            attributes.request_previous_response_id
        )
        self.set_request_reasoning_level(attributes.request_reasoning_level)
        self.set_request_seed(attributes.request_seed)
        self.set_request_stop_sequences(attributes.request_stop_sequences)
        self.set_request_stream(attributes.request_stream)
        self.set_request_temperature(attributes.request_temperature)
        self.set_request_top_k(attributes.request_top_k)
        self.set_request_top_p(attributes.request_top_p)
        self.set_response_finish_reasons(attributes.response_finish_reasons)
        self.set_response_id(attributes.response_id)
        self.set_response_model(attributes.response_model)
        self.set_response_time_to_first_chunk(
            attributes.response_time_to_first_chunk
        )
        self.set_usage_audio_cache_read_input_tokens(
            attributes.usage_audio_cache_read_input_tokens or None
        )
        self.set_usage_audio_input_tokens(
            attributes.usage_audio_input_tokens or None
        )
        self.set_usage_audio_output_tokens(
            attributes.usage_audio_output_tokens or None
        )
        self.set_usage_cache_read_input_tokens(
            attributes.usage_cache_read_input_tokens or None
        )
        self.set_usage_cache_write_input_tokens(
            attributes.usage_cache_write_input_tokens or None
        )
        self.set_usage_image_cache_read_input_tokens(
            attributes.usage_image_cache_read_input_tokens or None
        )
        self.set_usage_image_input_tokens(
            attributes.usage_image_input_tokens or None
        )
        self.set_usage_image_output_tokens(
            attributes.usage_image_output_tokens or None
        )
        self.set_usage_input_tokens(attributes.usage_input_tokens)
        self.set_usage_output_tokens(attributes.usage_output_tokens)
        self.set_usage_reasoning_output_tokens(
            attributes.usage_reasoning_output_tokens or None
        )
        self.set_usage_text_cache_read_input_tokens(
            attributes.usage_text_cache_read_input_tokens or None
        )
        self.set_usage_text_input_tokens(
            attributes.usage_text_input_tokens or None
        )
        self.set_usage_text_output_tokens(
            attributes.usage_text_output_tokens or None
        )


class InvokeAgentClientSpan(_Span):
    """`gen_ai.invoke_agent.client` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_agent_description(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_DESCRIPTION, value)

    def set_agent_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_ID, value)

    def set_agent_name(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_NAME, value)

    def set_agent_version(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_VERSION, value)

    def set_conversation_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_CONVERSATION_ID, value)

    def set_data_source_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_DATA_SOURCE_ID, value)

    def set_input_messages(self, value: Sequence[InputMessage] | None) -> None:
        self._set_json_attribute(Attr.GEN_AI_INPUT_MESSAGES, value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_output_messages(
        self, value: Sequence[OutputMessage] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_OUTPUT_MESSAGES, value)

    def set_output_type(
        self, value: Attr.GenAIOutputType | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OUTPUT_TYPE, value)

    def set_provider_name(
        self, value: Attr.GenAIProviderName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_PROVIDER_NAME, value)

    def set_request_choice_count(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_CHOICE_COUNT, value)

    def set_request_frequency_penalty(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_FREQUENCY_PENALTY, value)

    def set_request_max_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MAX_TOKENS, value)

    def set_request_model(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MODEL, value)

    def set_request_presence_penalty(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_PRESENCE_PENALTY, value)

    def set_request_previous_response_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_PREVIOUS_RESPONSE_ID, value)

    def set_request_seed(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_SEED, value)

    def set_request_stop_sequences(self, value: Sequence[str] | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_STOP_SEQUENCES, value)

    def set_request_temperature(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TEMPERATURE, value)

    def set_request_top_p(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TOP_P, value)

    def set_response_finish_reasons(self, value: Sequence[str] | None) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_FINISH_REASONS, value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_SYSTEM_INSTRUCTIONS, value)

    def set_tool_definitions(
        self, value: Sequence[ToolDefinition] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_TOOL_DEFINITIONS, value)

    def set_usage_audio_cache_read_input_tokens(
        self, value: int | None
    ) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_AUDIO_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_audio_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_AUDIO_INPUT_TOKENS, value)

    def set_usage_audio_output_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_AUDIO_OUTPUT_TOKENS, value)

    def set_usage_cache_read_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS, value)

    def set_usage_cache_write_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_CACHE_WRITE_INPUT_TOKENS, value)

    def set_usage_image_cache_read_input_tokens(
        self, value: int | None
    ) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_IMAGE_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_image_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_IMAGE_INPUT_TOKENS, value)

    def set_usage_image_output_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_IMAGE_OUTPUT_TOKENS, value)

    def set_usage_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_INPUT_TOKENS, value)

    def set_usage_output_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_OUTPUT_TOKENS, value)

    def set_usage_text_cache_read_input_tokens(
        self, value: int | None
    ) -> None:
        self._set_attribute(
            Attr.GEN_AI_USAGE_TEXT_CACHE_READ_INPUT_TOKENS, value
        )

    def set_usage_text_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_TEXT_INPUT_TOKENS, value)

    def set_usage_text_output_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_TEXT_OUTPUT_TOKENS, value)

    def set_server_address(self, value: str | None) -> None:
        self._set_attribute("server.address", value)

    def set_server_port(self, value: int | None) -> None:
        self._set_attribute("server.port", value)

    def apply(self, attributes: InvokeAgentClientAttributes) -> None:
        """Apply attributes that are not fixed at span creation."""
        self.set_error_type(attributes.error_type)
        self.set_agent_description(attributes.agent_description)
        self.set_agent_id(attributes.agent_id)
        self.set_agent_version(attributes.agent_version)
        self.set_conversation_id(attributes.conversation_id)
        self.set_data_source_id(attributes.data_source_id)
        self.set_output_type(attributes.output_type)
        self.set_request_choice_count(attributes.request_choice_count)
        self.set_request_frequency_penalty(
            attributes.request_frequency_penalty
        )
        self.set_request_max_tokens(attributes.request_max_tokens)
        self.set_request_presence_penalty(attributes.request_presence_penalty)
        self.set_request_previous_response_id(
            attributes.request_previous_response_id
        )
        self.set_request_seed(attributes.request_seed)
        self.set_request_stop_sequences(attributes.request_stop_sequences)
        self.set_request_temperature(attributes.request_temperature)
        self.set_request_top_p(attributes.request_top_p)
        self.set_response_finish_reasons(attributes.response_finish_reasons)
        self.set_usage_audio_cache_read_input_tokens(
            attributes.usage_audio_cache_read_input_tokens or None
        )
        self.set_usage_audio_input_tokens(
            attributes.usage_audio_input_tokens or None
        )
        self.set_usage_audio_output_tokens(
            attributes.usage_audio_output_tokens or None
        )
        self.set_usage_cache_read_input_tokens(
            attributes.usage_cache_read_input_tokens or None
        )
        self.set_usage_cache_write_input_tokens(
            attributes.usage_cache_write_input_tokens or None
        )
        self.set_usage_image_cache_read_input_tokens(
            attributes.usage_image_cache_read_input_tokens or None
        )
        self.set_usage_image_input_tokens(
            attributes.usage_image_input_tokens or None
        )
        self.set_usage_image_output_tokens(
            attributes.usage_image_output_tokens or None
        )
        self.set_usage_input_tokens(attributes.usage_input_tokens)
        self.set_usage_output_tokens(attributes.usage_output_tokens)
        self.set_usage_text_cache_read_input_tokens(
            attributes.usage_text_cache_read_input_tokens or None
        )
        self.set_usage_text_input_tokens(
            attributes.usage_text_input_tokens or None
        )
        self.set_usage_text_output_tokens(
            attributes.usage_text_output_tokens or None
        )


class InvokeAgentSpan(_Span):
    """`gen_ai.invoke_agent.internal` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_agent_description(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_DESCRIPTION, value)

    def set_agent_name(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_NAME, value)

    def set_conversation_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_CONVERSATION_ID, value)

    def set_data_source_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_DATA_SOURCE_ID, value)

    def set_input_messages(self, value: Sequence[InputMessage] | None) -> None:
        self._set_json_attribute(Attr.GEN_AI_INPUT_MESSAGES, value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_output_messages(
        self, value: Sequence[OutputMessage] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_OUTPUT_MESSAGES, value)

    def set_output_type(
        self, value: Attr.GenAIOutputType | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OUTPUT_TYPE, value)

    def set_request_choice_count(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_CHOICE_COUNT, value)

    def set_request_frequency_penalty(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_FREQUENCY_PENALTY, value)

    def set_request_max_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MAX_TOKENS, value)

    def set_request_model(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MODEL, value)

    def set_request_presence_penalty(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_PRESENCE_PENALTY, value)

    def set_request_seed(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_SEED, value)

    def set_request_stop_sequences(self, value: Sequence[str] | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_STOP_SEQUENCES, value)

    def set_request_temperature(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TEMPERATURE, value)

    def set_request_top_p(self, value: float | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_TOP_P, value)

    def set_response_finish_reasons(self, value: Sequence[str] | None) -> None:
        self._set_attribute(Attr.GEN_AI_RESPONSE_FINISH_REASONS, value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_SYSTEM_INSTRUCTIONS, value)

    def set_tool_definitions(
        self, value: Sequence[ToolDefinition] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_TOOL_DEFINITIONS, value)

    def set_usage_input_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_INPUT_TOKENS, value)

    def set_usage_output_tokens(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_USAGE_OUTPUT_TOKENS, value)

    def apply(self, attributes: InvokeAgentAttributes) -> None:
        """Apply attributes that are not fixed at span creation."""
        self.set_error_type(attributes.error_type)
        self.set_agent_description(attributes.agent_description)
        self.set_conversation_id(attributes.conversation_id)
        self.set_data_source_id(attributes.data_source_id)
        self.set_output_type(attributes.output_type)
        self.set_request_choice_count(attributes.request_choice_count)
        self.set_request_frequency_penalty(
            attributes.request_frequency_penalty
        )
        self.set_request_max_tokens(attributes.request_max_tokens)
        self.set_request_presence_penalty(attributes.request_presence_penalty)
        self.set_request_seed(attributes.request_seed)
        self.set_request_stop_sequences(attributes.request_stop_sequences)
        self.set_request_temperature(attributes.request_temperature)
        self.set_request_top_p(attributes.request_top_p)
        self.set_response_finish_reasons(attributes.response_finish_reasons)
        self.set_usage_input_tokens(attributes.usage_input_tokens)
        self.set_usage_output_tokens(attributes.usage_output_tokens)


class InvokeWorkflowSpan(_Span):
    """`gen_ai.invoke_workflow.internal` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_conversation_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_CONVERSATION_ID, value)

    def set_input_messages(self, value: Sequence[InputMessage] | None) -> None:
        self._set_json_attribute(Attr.GEN_AI_INPUT_MESSAGES, value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_output_messages(
        self, value: Sequence[OutputMessage] | None
    ) -> None:
        self._set_json_attribute(Attr.GEN_AI_OUTPUT_MESSAGES, value)

    def set_workflow_name(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_WORKFLOW_NAME, value)

    def apply(self, attributes: InvokeWorkflowAttributes) -> None:
        """Apply attributes that are not fixed at span creation."""
        self.set_error_type(attributes.error_type)
        self.set_conversation_id(attributes.conversation_id)
        self.set_workflow_name(attributes.workflow_name)


class MemorySpan(_Span):
    """`gen_ai.memory.client` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_memory_query_text(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_MEMORY_QUERY_TEXT, value)

    def set_memory_record_count(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_MEMORY_RECORD_COUNT, value)

    def set_memory_record_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_MEMORY_RECORD_ID, value)

    def set_memory_records(self, value: AnyValue | None) -> None:
        self._set_json_attribute(Attr.GEN_AI_MEMORY_RECORDS, value)

    def set_memory_store_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_MEMORY_STORE_ID, value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_provider_name(
        self, value: Attr.GenAIProviderName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_PROVIDER_NAME, value)

    def set_server_address(self, value: str | None) -> None:
        self._set_attribute("server.address", value)

    def set_server_port(self, value: int | None) -> None:
        self._set_attribute("server.port", value)


class PlanSpan(_Span):
    """`gen_ai.plan.internal` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_agent_name(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_AGENT_NAME, value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)


class RetrievalSpan(_Span):
    """`gen_ai.retrieval.client` span."""

    def set_error_type(self, value: str | None) -> None:
        self._set_attribute("error.type", value)

    def set_data_source_id(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_DATA_SOURCE_ID, value)

    def set_operation_name(
        self, value: Attr.GenAIOperationName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_OPERATION_NAME, value)

    def set_provider_name(
        self, value: Attr.GenAIProviderName | str | None
    ) -> None:
        self._set_attribute(Attr.GEN_AI_PROVIDER_NAME, value)

    def set_request_model(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_REQUEST_MODEL, value)

    def set_retrieval_documents(self, value: AnyValue | None) -> None:
        self._set_json_attribute(Attr.GEN_AI_RETRIEVAL_DOCUMENTS, value)

    def set_retrieval_query_text(self, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_RETRIEVAL_QUERY_TEXT, value)

    def set_retrieval_top_k(self, value: int | None) -> None:
        self._set_attribute(Attr.GEN_AI_RETRIEVAL_TOP_K, value)

    def set_server_address(self, value: str | None) -> None:
        self._set_attribute("server.address", value)

    def set_server_port(self, value: int | None) -> None:
        self._set_attribute("server.port", value)

    def apply(self, attributes: RetrievalAttributes) -> None:
        """Apply attributes that are not fixed at span creation."""
        self.set_error_type(attributes.error_type)
        self.set_data_source_id(attributes.data_source_id)
        self.set_operation_name(attributes.operation_name)
        self.set_provider_name(attributes.provider_name)
        self.set_request_model(attributes.request_model)
        self.set_retrieval_top_k(attributes.retrieval_top_k)
        self.set_server_address(attributes.server_address)
        self.set_server_port(attributes.server_port)


class _Spans:
    """Creates spans following the gen_ai semantic conventions."""

    def __init__(self, tracer: Tracer) -> None:
        self._tracer = tracer

    def create_agent(
        self,
        name: str,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        agent_name: str | None = None,
        request_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        context: Context | None = None,
    ) -> CreateAgentSpan:
        """Start a `gen_ai.create_agent.client` span."""
        attributes: dict[str, AttributeValue] = {}
        if agent_name is not None:
            attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        if operation_name is not None:
            attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if provider_name is not None:
            attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if server_address is not None:
            attributes["server.address"] = _value(server_address)
        if server_port is not None:
            attributes["server.port"] = _value(server_port)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return CreateAgentSpan(span)

    def embeddings(
        self,
        name: str,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        request_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        context: Context | None = None,
    ) -> EmbeddingsSpan:
        """Start a `gen_ai.embeddings.client` span."""
        attributes: dict[str, AttributeValue] = {}
        if operation_name is not None:
            attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if provider_name is not None:
            attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if server_address is not None:
            attributes["server.address"] = _value(server_address)
        if server_port is not None:
            attributes["server.port"] = _value(server_port)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return EmbeddingsSpan(span)

    def execute_tool(
        self,
        name: str,
        *,
        operation_name: Attr.GenAIOperationName | str,
        tool_name: str,
        agent_name: str | None = None,
        tool_type: str | None = None,
        context: Context | None = None,
    ) -> ExecuteToolSpan:
        """Start a `gen_ai.execute_tool.internal` span."""
        attributes: dict[str, AttributeValue] = {}
        if agent_name is not None:
            attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        if operation_name is not None:
            attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if tool_name is not None:
            attributes[Attr.GEN_AI_TOOL_NAME] = _value(tool_name)
        if tool_type is not None:
            attributes[Attr.GEN_AI_TOOL_TYPE] = _value(tool_type)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )
        return ExecuteToolSpan(span)

    def fetch_response(
        self,
        name: str,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        server_address: str | None = None,
        server_port: int | None = None,
        context: Context | None = None,
    ) -> FetchResponseSpan:
        """Start a `gen_ai.fetch_response.client` span."""
        attributes: dict[str, AttributeValue] = {}
        if operation_name is not None:
            attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if provider_name is not None:
            attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if server_address is not None:
            attributes["server.address"] = _value(server_address)
        if server_port is not None:
            attributes["server.port"] = _value(server_port)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return FetchResponseSpan(span)

    def inference(
        self,
        name: str,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        request_model: str | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        context: Context | None = None,
    ) -> InferenceSpan:
        """Start a `gen_ai.inference.client` span."""
        attributes: dict[str, AttributeValue] = {}
        if operation_name is not None:
            attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if provider_name is not None:
            attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if server_address is not None:
            attributes["server.address"] = _value(server_address)
        if server_port is not None:
            attributes["server.port"] = _value(server_port)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return InferenceSpan(span)

    def invoke_agent_client(
        self,
        name: str,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
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
        if operation_name is not None:
            attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if provider_name is not None:
            attributes[Attr.GEN_AI_PROVIDER_NAME] = _value(provider_name)
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        if server_address is not None:
            attributes["server.address"] = _value(server_address)
        if server_port is not None:
            attributes["server.port"] = _value(server_port)
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
        operation_name: Attr.GenAIOperationName | str,
        agent_name: str | None = None,
        request_model: str | None = None,
        context: Context | None = None,
    ) -> InvokeAgentSpan:
        """Start a `gen_ai.invoke_agent.internal` span."""
        attributes: dict[str, AttributeValue] = {}
        if agent_name is not None:
            attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        if operation_name is not None:
            attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        if request_model is not None:
            attributes[Attr.GEN_AI_REQUEST_MODEL] = _value(request_model)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )
        return InvokeAgentSpan(span)

    def invoke_workflow(
        self,
        name: str,
        *,
        operation_name: Attr.GenAIOperationName | str,
        context: Context | None = None,
    ) -> InvokeWorkflowSpan:
        """Start a `gen_ai.invoke_workflow.internal` span."""
        attributes: dict[str, AttributeValue] = {}
        if operation_name is not None:
            attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )
        return InvokeWorkflowSpan(span)

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

    def plan(
        self,
        name: str,
        *,
        operation_name: Attr.GenAIOperationName | str,
        agent_name: str | None = None,
        context: Context | None = None,
    ) -> PlanSpan:
        """Start a `gen_ai.plan.internal` span."""
        attributes: dict[str, AttributeValue] = {}
        if agent_name is not None:
            attributes[Attr.GEN_AI_AGENT_NAME] = _value(agent_name)
        if operation_name is not None:
            attributes[Attr.GEN_AI_OPERATION_NAME] = _value(operation_name)
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )
        return PlanSpan(span)

    def retrieval(
        self,
        name: str,
        *,
        context: Context | None = None,
    ) -> RetrievalSpan:
        """Start a `gen_ai.retrieval.client` span."""
        attributes: dict[str, AttributeValue] = {}
        span = self._tracer.start_span(
            name,
            context=context,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        )
        return RetrievalSpan(span)


__all__ = ["_Spans"]
