# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
# Code generated from OpenTelemetry GenAI semantic conventions. DO NOT EDIT.

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from opentelemetry.util.genai.semconv.gen_ai.attributes import (
    GenAiOperationName,
    GenAiOutputType,
    GenAiProviderName,
    GenAiTokenType,
)
from opentelemetry.util.genai.types import (
    InputMessage,
    OutputMessage,
    SystemInstructionPart,
    ToolDefinition,
)
from opentelemetry.util.types import AnyValue


@dataclass(kw_only=True)
class InferenceAttributes:
    """Typed superset of attributes used by GenAI inference telemetry."""

    operation_name: GenAiOperationName | str
    provider_name: GenAiProviderName | str
    request_model: str | None = None
    server_address: str | None = None
    server_port: int | None = None
    conversation_id: str | None = None
    request_stream: bool | None = None
    request_temperature: float | None = None
    request_top_p: float | None = None
    request_top_k: int | None = None
    request_frequency_penalty: float | None = None
    request_presence_penalty: float | None = None
    request_max_tokens: int | None = None
    request_stop_sequences: Sequence[str] | None = None
    request_seed: int | None = None
    request_choice_count: int | None = None
    request_reasoning_level: str | None = None
    request_previous_response_id: str | None = None
    response_finish_reasons: Sequence[str] | None = None
    response_model: str | None = None
    response_id: str | None = None
    response_time_to_first_chunk: float | None = None
    output_type: GenAiOutputType | str | None = None
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None
    usage_cache_write_input_tokens: int | None = None
    usage_cache_read_input_tokens: int | None = None
    usage_reasoning_output_tokens: int | None = None
    usage_text_input_tokens: int | None = None
    usage_image_input_tokens: int | None = None
    usage_audio_input_tokens: int | None = None
    usage_text_output_tokens: int | None = None
    usage_image_output_tokens: int | None = None
    usage_audio_output_tokens: int | None = None
    usage_text_cache_read_input_tokens: int | None = None
    usage_image_cache_read_input_tokens: int | None = None
    usage_audio_cache_read_input_tokens: int | None = None
    token_type: GenAiTokenType | str | None = None
    conversation_compacted: bool | None = None
    prompt_name: str | None = None
    prompt_version: str | None = None
    prompt_variables: Mapping[str, object] | None = None
    input_messages: Sequence[InputMessage] | None = None
    output_messages: Sequence[OutputMessage] | None = None
    system_instructions: Sequence[SystemInstructionPart] | None = None
    tool_definitions: Sequence[ToolDefinition] | None = None
    error_type: str | None = None


@dataclass(kw_only=True)
class EmbeddingAttributes:
    """Typed superset of attributes used by GenAI embedding telemetry."""

    operation_name: GenAiOperationName | str
    provider_name: GenAiProviderName | str
    request_model: str | None = None
    server_address: str | None = None
    server_port: int | None = None
    request_encoding_formats: Sequence[str] | None = None
    embeddings_dimension_count: int | None = None
    response_model: str | None = None
    usage_input_tokens: int | None = None
    error_type: str | None = None


@dataclass(kw_only=True)
class RetrievalAttributes:
    """Typed superset of attributes used by GenAI retrieval telemetry."""

    operation_name: GenAiOperationName | str
    data_source_id: str | None = None
    provider_name: GenAiProviderName | str | None = None
    request_model: str | None = None
    response_model: str | None = None
    server_address: str | None = None
    server_port: int | None = None
    retrieval_top_k: int | None = None
    retrieval_query_text: str | None = None
    retrieval_documents: AnyValue | None = None
    error_type: str | None = None


@dataclass(kw_only=True)
class FetchResponseAttributes:
    """Typed superset of attributes used by GenAI fetch-response telemetry."""

    operation_name: GenAiOperationName | str
    provider_name: GenAiProviderName | str
    response_id: str
    request_model: str | None = None
    request_stream: bool | None = None
    server_address: str | None = None
    server_port: int | None = None
    request_stream_cursor: str | None = None
    response_model: str | None = None
    response_status: str | None = None
    response_finish_reasons: Sequence[str] | None = None
    response_time_to_first_chunk: float | None = None
    output_messages: Sequence[OutputMessage] | None = None
    system_instructions: Sequence[SystemInstructionPart] | None = None
    tool_definitions: Sequence[ToolDefinition] | None = None
    error_type: str | None = None


@dataclass(kw_only=True)
class LocalAgentAttributes:
    """Typed superset of attributes used by local GenAI agent telemetry."""

    operation_name: GenAiOperationName | str
    request_model: str | None = None
    agent_name: str | None = None
    agent_description: str | None = None
    conversation_id: str | None = None
    data_source_id: str | None = None
    output_type: GenAiOutputType | str | None = None
    request_temperature: float | None = None
    request_top_p: float | None = None
    request_frequency_penalty: float | None = None
    request_presence_penalty: float | None = None
    request_max_tokens: int | None = None
    request_stop_sequences: Sequence[str] | None = None
    request_seed: int | None = None
    request_choice_count: int | None = None
    response_finish_reasons: Sequence[str] | None = None
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None
    input_messages: Sequence[InputMessage] | None = None
    output_messages: Sequence[OutputMessage] | None = None
    system_instructions: Sequence[SystemInstructionPart] | None = None
    tool_definitions: Sequence[ToolDefinition] | None = None
    error_type: str | None = None


@dataclass(kw_only=True)
class RemoteAgentAttributes:
    """Typed superset of attributes used by remote GenAI agent telemetry."""

    operation_name: GenAiOperationName | str
    provider_name: GenAiProviderName | str
    request_model: str | None = None
    response_model: str | None = None
    server_address: str | None = None
    server_port: int | None = None
    agent_name: str | None = None
    agent_id: str | None = None
    agent_version: str | None = None
    agent_description: str | None = None
    conversation_id: str | None = None
    data_source_id: str | None = None
    output_type: GenAiOutputType | str | None = None
    request_stream: bool | None = None
    request_temperature: float | None = None
    request_top_p: float | None = None
    request_frequency_penalty: float | None = None
    request_presence_penalty: float | None = None
    request_max_tokens: int | None = None
    request_stop_sequences: Sequence[str] | None = None
    request_seed: int | None = None
    request_choice_count: int | None = None
    request_previous_response_id: str | None = None
    response_finish_reasons: Sequence[str] | None = None
    response_time_to_first_chunk: float | None = None
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None
    usage_cache_write_input_tokens: int | None = None
    usage_cache_read_input_tokens: int | None = None
    input_messages: Sequence[InputMessage] | None = None
    output_messages: Sequence[OutputMessage] | None = None
    system_instructions: Sequence[SystemInstructionPart] | None = None
    tool_definitions: Sequence[ToolDefinition] | None = None
    error_type: str | None = None


@dataclass(kw_only=True)
class ToolAttributes:
    """Typed superset of attributes used by GenAI tool telemetry."""

    operation_name: GenAiOperationName | str
    tool_name: str
    tool_type: str | None = None
    agent_name: str | None = None
    tool_call_id: str | None = None
    tool_description: str | None = None
    tool_call_arguments: AnyValue | None = None
    tool_call_result: AnyValue | None = None
    error_type: str | None = None


@dataclass(kw_only=True)
class WorkflowAttributes:
    """Typed superset of attributes used by GenAI workflow telemetry."""

    operation_name: GenAiOperationName | str
    workflow_name: str | None = None
    conversation_id: str | None = None
    input_messages: Sequence[InputMessage] | None = None
    output_messages: Sequence[OutputMessage] | None = None
    error_type: str | None = None


__all__ = [
    "EmbeddingAttributes",
    "FetchResponseAttributes",
    "InferenceAttributes",
    "LocalAgentAttributes",
    "RemoteAgentAttributes",
    "RetrievalAttributes",
    "ToolAttributes",
    "WorkflowAttributes",
]
