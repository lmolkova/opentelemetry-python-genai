# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
# Code generated from OpenTelemetry GenAI semantic conventions. DO NOT EDIT.

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from opentelemetry.util.genai.semconv.gen_ai import attributes as Attr
from opentelemetry.util.genai.types import (
    InputMessage,
    OutputMessage,
    SystemInstructionPart,
    ToolDefinition,
)
from opentelemetry.util.types import AnyValue


@dataclass(kw_only=True)
class EmbeddingsAttributes:
    """Typed attributes for the related GenAI span."""

    operation_name: Attr.GenAIOperationName | str
    provider_name: Attr.GenAIProviderName | str
    error_type: str | None = None
    embeddings_dimension_count: int | None = None
    request_encoding_formats: Sequence[str] | None = None
    request_model: str | None = None
    response_model: str | None = None
    usage_input_tokens: int | None = None
    server_address: str | None = None
    server_port: int | None = None


@dataclass(kw_only=True)
class ExecuteToolAttributes:
    """Typed attributes for the related GenAI span."""

    operation_name: Attr.GenAIOperationName | str
    tool_name: str
    error_type: str | None = None
    agent_name: str | None = None
    tool_call_arguments: AnyValue | None = None
    tool_call_id: str | None = None
    tool_call_result: AnyValue | None = None
    tool_description: str | None = None
    tool_type: str | None = None


@dataclass(kw_only=True)
class FetchResponseAttributes:
    """Typed attributes for the related GenAI span."""

    operation_name: Attr.GenAIOperationName | str
    provider_name: Attr.GenAIProviderName | str
    response_id: str
    error_type: str | None = None
    output_messages: Sequence[OutputMessage] | None = None
    request_stream_cursor: str | None = None
    response_finish_reasons: Sequence[str] | None = None
    response_model: str | None = None
    response_status: Attr.GenAIResponseStatus | str | None = None
    system_instructions: Sequence[SystemInstructionPart] | None = None
    tool_definitions: Sequence[ToolDefinition] | None = None
    server_address: str | None = None
    server_port: int | None = None
    request_model: str | None = None


@dataclass(kw_only=True)
class InferenceAttributes:
    """Typed attributes for the related GenAI span."""

    operation_name: Attr.GenAIOperationName | str
    provider_name: Attr.GenAIProviderName | str
    error_type: str | None = None
    conversation_compacted: bool | None = None
    conversation_id: str | None = None
    input_messages: Sequence[InputMessage] | None = None
    output_messages: Sequence[OutputMessage] | None = None
    output_type: Attr.GenAIOutputType | str | None = None
    prompt_name: str | None = None
    prompt_variable: Mapping[str, object] | None = None
    prompt_version: str | None = None
    request_choice_count: int | None = None
    request_frequency_penalty: float | None = None
    request_max_tokens: int | None = None
    request_model: str | None = None
    request_presence_penalty: float | None = None
    request_previous_response_id: str | None = None
    request_reasoning_level: str | None = None
    request_seed: int | None = None
    request_stop_sequences: Sequence[str] | None = None
    request_stream: bool | None = None
    request_temperature: float | None = None
    request_top_k: int | None = None
    request_top_p: float | None = None
    response_finish_reasons: Sequence[str] | None = None
    response_id: str | None = None
    response_model: str | None = None
    response_time_to_first_chunk: float | None = None
    system_instructions: Sequence[SystemInstructionPart] | None = None
    tool_definitions: Sequence[ToolDefinition] | None = None
    usage_audio_cache_read_input_tokens: int | None = None
    usage_audio_input_tokens: int | None = None
    usage_audio_output_tokens: int | None = None
    usage_cache_read_input_tokens: int | None = None
    usage_cache_write_input_tokens: int | None = None
    usage_image_cache_read_input_tokens: int | None = None
    usage_image_input_tokens: int | None = None
    usage_image_output_tokens: int | None = None
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None
    usage_reasoning_output_tokens: int | None = None
    usage_text_cache_read_input_tokens: int | None = None
    usage_text_input_tokens: int | None = None
    usage_text_output_tokens: int | None = None
    server_address: str | None = None
    server_port: int | None = None


@dataclass(kw_only=True)
class InvokeAgentClientAttributes:
    """Typed attributes for the related GenAI span."""

    operation_name: Attr.GenAIOperationName | str
    provider_name: Attr.GenAIProviderName | str
    error_type: str | None = None
    agent_description: str | None = None
    agent_id: str | None = None
    agent_name: str | None = None
    agent_version: str | None = None
    conversation_id: str | None = None
    data_source_id: str | None = None
    input_messages: Sequence[InputMessage] | None = None
    output_messages: Sequence[OutputMessage] | None = None
    output_type: Attr.GenAIOutputType | str | None = None
    request_choice_count: int | None = None
    request_frequency_penalty: float | None = None
    request_max_tokens: int | None = None
    request_model: str | None = None
    request_presence_penalty: float | None = None
    request_previous_response_id: str | None = None
    request_seed: int | None = None
    request_stop_sequences: Sequence[str] | None = None
    request_temperature: float | None = None
    request_top_p: float | None = None
    response_finish_reasons: Sequence[str] | None = None
    system_instructions: Sequence[SystemInstructionPart] | None = None
    tool_definitions: Sequence[ToolDefinition] | None = None
    usage_audio_cache_read_input_tokens: int | None = None
    usage_audio_input_tokens: int | None = None
    usage_audio_output_tokens: int | None = None
    usage_cache_read_input_tokens: int | None = None
    usage_cache_write_input_tokens: int | None = None
    usage_image_cache_read_input_tokens: int | None = None
    usage_image_input_tokens: int | None = None
    usage_image_output_tokens: int | None = None
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None
    usage_text_cache_read_input_tokens: int | None = None
    usage_text_input_tokens: int | None = None
    usage_text_output_tokens: int | None = None
    server_address: str | None = None
    server_port: int | None = None
    response_model: str | None = None


@dataclass(kw_only=True)
class InvokeAgentAttributes:
    """Typed attributes for the related GenAI span."""

    operation_name: Attr.GenAIOperationName | str
    error_type: str | None = None
    agent_description: str | None = None
    agent_name: str | None = None
    conversation_id: str | None = None
    data_source_id: str | None = None
    input_messages: Sequence[InputMessage] | None = None
    output_messages: Sequence[OutputMessage] | None = None
    output_type: Attr.GenAIOutputType | str | None = None
    request_choice_count: int | None = None
    request_frequency_penalty: float | None = None
    request_max_tokens: int | None = None
    request_model: str | None = None
    request_presence_penalty: float | None = None
    request_seed: int | None = None
    request_stop_sequences: Sequence[str] | None = None
    request_temperature: float | None = None
    request_top_p: float | None = None
    response_finish_reasons: Sequence[str] | None = None
    system_instructions: Sequence[SystemInstructionPart] | None = None
    tool_definitions: Sequence[ToolDefinition] | None = None
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None


@dataclass(kw_only=True)
class InvokeWorkflowAttributes:
    """Typed attributes for the related GenAI span."""

    operation_name: Attr.GenAIOperationName | str
    error_type: str | None = None
    conversation_id: str | None = None
    input_messages: Sequence[InputMessage] | None = None
    output_messages: Sequence[OutputMessage] | None = None
    workflow_name: str | None = None


@dataclass(kw_only=True)
class RetrievalAttributes:
    """Typed attributes for the related GenAI span."""

    operation_name: Attr.GenAIOperationName | str
    error_type: str | None = None
    data_source_id: str | None = None
    provider_name: Attr.GenAIProviderName | str | None = None
    request_model: str | None = None
    retrieval_documents: AnyValue | None = None
    retrieval_query_text: str | None = None
    retrieval_top_k: int | None = None
    server_address: str | None = None
    server_port: int | None = None
    response_model: str | None = None


__all__ = [
    "EmbeddingsAttributes",
    "ExecuteToolAttributes",
    "FetchResponseAttributes",
    "InferenceAttributes",
    "InvokeAgentAttributes",
    "InvokeAgentClientAttributes",
    "InvokeWorkflowAttributes",
    "RetrievalAttributes",
]
