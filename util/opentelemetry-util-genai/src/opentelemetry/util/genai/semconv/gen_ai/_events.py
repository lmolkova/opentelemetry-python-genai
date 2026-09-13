# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
# Code generated from OpenTelemetry GenAI semantic conventions. DO NOT EDIT.

from __future__ import annotations

from collections.abc import Mapping, Sequence

from opentelemetry._logs import Logger
from opentelemetry.context import Context
from opentelemetry.util.genai.semconv._event import _Event
from opentelemetry.util.genai.semconv.gen_ai import attributes as Attr
from opentelemetry.util.genai.semconv.gen_ai.attribute_sets import (
    InferenceAttributes,
)
from opentelemetry.util.genai.types import (
    InputMessage,
    OutputMessage,
    SystemInstructionPart,
    ToolDefinition,
)
from opentelemetry.util.types import AnyValue


class ClientInferenceOperationDetailsEvent(_Event):
    """`gen_ai.client.inference.operation.details` event."""

    def set_input_messages(self, value: Sequence[InputMessage] | None) -> None:
        self._set_structured_attribute(Attr.GEN_AI_INPUT_MESSAGES, value)

    def set_output_messages(
        self, value: Sequence[OutputMessage] | None
    ) -> None:
        self._set_structured_attribute(Attr.GEN_AI_OUTPUT_MESSAGES, value)

    def set_prompt_variable(self, name: str, value: str | None) -> None:
        self._set_attribute(Attr.GEN_AI_PROMPT_VARIABLE + f".{name}", value)

    def set_system_instructions(
        self, value: Sequence[SystemInstructionPart] | None
    ) -> None:
        self._set_structured_attribute(Attr.GEN_AI_SYSTEM_INSTRUCTIONS, value)

    def set_tool_definitions(
        self, value: Sequence[ToolDefinition] | None
    ) -> None:
        self._set_structured_attribute(Attr.GEN_AI_TOOL_DEFINITIONS, value)


class ClientOperationExceptionEvent(_Event):
    """`gen_ai.client.operation.exception` event."""


class EvaluationResultEvent(_Event):
    """`gen_ai.evaluation.result` event."""


class _Events:
    """Creates events following the gen_ai semantic conventions."""

    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    def client_inference_operation_details_from_attributes(
        self,
        attributes: InferenceAttributes,
        *,
        additional_attributes: Mapping[str, AnyValue] | None = None,
        context: Context | None = None,
    ) -> ClientInferenceOperationDetailsEvent:
        """Create a `gen_ai.client.inference.operation.details` event from aggregate attributes."""
        return self.client_inference_operation_details(
            error_type=attributes.error_type,
            conversation_compacted=attributes.conversation_compacted,
            conversation_id=attributes.conversation_id,
            operation_name=attributes.operation_name,
            output_type=attributes.output_type,
            prompt_name=attributes.prompt_name,
            prompt_version=attributes.prompt_version,
            provider_name=attributes.provider_name,
            request_choice_count=attributes.request_choice_count,
            request_frequency_penalty=attributes.request_frequency_penalty,
            request_max_tokens=attributes.request_max_tokens,
            request_model=attributes.request_model,
            request_presence_penalty=attributes.request_presence_penalty,
            request_previous_response_id=attributes.request_previous_response_id,
            request_reasoning_level=attributes.request_reasoning_level,
            request_seed=attributes.request_seed,
            request_stop_sequences=attributes.request_stop_sequences,
            request_stream=attributes.request_stream,
            request_temperature=attributes.request_temperature,
            request_top_k=attributes.request_top_k,
            request_top_p=attributes.request_top_p,
            response_finish_reasons=attributes.response_finish_reasons,
            response_id=attributes.response_id,
            response_model=attributes.response_model,
            response_time_to_first_chunk=attributes.response_time_to_first_chunk,
            usage_audio_cache_read_input_tokens=attributes.usage_audio_cache_read_input_tokens,
            usage_audio_input_tokens=attributes.usage_audio_input_tokens,
            usage_audio_output_tokens=attributes.usage_audio_output_tokens,
            usage_cache_read_input_tokens=attributes.usage_cache_read_input_tokens,
            usage_cache_write_input_tokens=attributes.usage_cache_write_input_tokens,
            usage_image_cache_read_input_tokens=attributes.usage_image_cache_read_input_tokens,
            usage_image_input_tokens=attributes.usage_image_input_tokens,
            usage_image_output_tokens=attributes.usage_image_output_tokens,
            usage_input_tokens=attributes.usage_input_tokens,
            usage_output_tokens=attributes.usage_output_tokens,
            usage_reasoning_output_tokens=attributes.usage_reasoning_output_tokens,
            usage_text_cache_read_input_tokens=attributes.usage_text_cache_read_input_tokens,
            usage_text_input_tokens=attributes.usage_text_input_tokens,
            usage_text_output_tokens=attributes.usage_text_output_tokens,
            server_address=attributes.server_address,
            server_port=attributes.server_port,
            additional_attributes=additional_attributes,
            context=context,
        )

    def client_inference_operation_details(
        self,
        *,
        operation_name: Attr.GenAIOperationName | str,
        provider_name: Attr.GenAIProviderName | str,
        error_type: str | None = None,
        conversation_compacted: bool | None = None,
        conversation_id: str | None = None,
        input_messages: Sequence[InputMessage] | None = None,
        output_messages: Sequence[OutputMessage] | None = None,
        output_type: Attr.GenAIOutputType | str | None = None,
        prompt_name: str | None = None,
        prompt_variable: Mapping[str, object] | None = None,
        prompt_version: str | None = None,
        request_choice_count: int | None = None,
        request_frequency_penalty: float | None = None,
        request_max_tokens: int | None = None,
        request_model: str | None = None,
        request_presence_penalty: float | None = None,
        request_previous_response_id: str | None = None,
        request_reasoning_level: str | None = None,
        request_seed: int | None = None,
        request_stop_sequences: Sequence[str] | None = None,
        request_stream: bool | None = None,
        request_temperature: float | None = None,
        request_top_k: int | None = None,
        request_top_p: float | None = None,
        response_finish_reasons: Sequence[str] | None = None,
        response_id: str | None = None,
        response_model: str | None = None,
        response_time_to_first_chunk: float | None = None,
        system_instructions: Sequence[SystemInstructionPart] | None = None,
        tool_definitions: Sequence[ToolDefinition] | None = None,
        usage_audio_cache_read_input_tokens: int | None = None,
        usage_audio_input_tokens: int | None = None,
        usage_audio_output_tokens: int | None = None,
        usage_cache_read_input_tokens: int | None = None,
        usage_cache_write_input_tokens: int | None = None,
        usage_image_cache_read_input_tokens: int | None = None,
        usage_image_input_tokens: int | None = None,
        usage_image_output_tokens: int | None = None,
        usage_input_tokens: int | None = None,
        usage_output_tokens: int | None = None,
        usage_reasoning_output_tokens: int | None = None,
        usage_text_cache_read_input_tokens: int | None = None,
        usage_text_input_tokens: int | None = None,
        usage_text_output_tokens: int | None = None,
        server_address: str | None = None,
        server_port: int | None = None,
        additional_attributes: Mapping[str, AnyValue] | None = None,
        context: Context | None = None,
    ) -> ClientInferenceOperationDetailsEvent:
        """Create a `gen_ai.client.inference.operation.details` event."""
        event = ClientInferenceOperationDetailsEvent(
            self._logger,
            "gen_ai.client.inference.operation.details",
            context=context,
        )
        event._set_attribute("error.type", error_type)
        event._set_attribute(
            Attr.GEN_AI_CONVERSATION_COMPACTED, conversation_compacted
        )
        event._set_attribute(Attr.GEN_AI_CONVERSATION_ID, conversation_id)
        event.set_input_messages(input_messages)
        event._set_attribute(Attr.GEN_AI_OPERATION_NAME, operation_name)
        event.set_output_messages(output_messages)
        event._set_attribute(Attr.GEN_AI_OUTPUT_TYPE, output_type)
        event._set_attribute(Attr.GEN_AI_PROMPT_NAME, prompt_name)
        if prompt_variable is not None:
            for name, value in prompt_variable.items():
                event.set_prompt_variable(name, value)
        event._set_attribute(Attr.GEN_AI_PROMPT_VERSION, prompt_version)
        event._set_attribute(Attr.GEN_AI_PROVIDER_NAME, provider_name)
        event._set_attribute(
            Attr.GEN_AI_REQUEST_CHOICE_COUNT, request_choice_count
        )
        event._set_attribute(
            Attr.GEN_AI_REQUEST_FREQUENCY_PENALTY, request_frequency_penalty
        )
        event._set_attribute(
            Attr.GEN_AI_REQUEST_MAX_TOKENS, request_max_tokens
        )
        event._set_attribute(Attr.GEN_AI_REQUEST_MODEL, request_model)
        event._set_attribute(
            Attr.GEN_AI_REQUEST_PRESENCE_PENALTY, request_presence_penalty
        )
        event._set_attribute(
            Attr.GEN_AI_REQUEST_PREVIOUS_RESPONSE_ID,
            request_previous_response_id,
        )
        event._set_attribute(
            Attr.GEN_AI_REQUEST_REASONING_LEVEL, request_reasoning_level
        )
        event._set_attribute(Attr.GEN_AI_REQUEST_SEED, request_seed)
        event._set_attribute(
            Attr.GEN_AI_REQUEST_STOP_SEQUENCES, request_stop_sequences
        )
        event._set_attribute(Attr.GEN_AI_REQUEST_STREAM, request_stream)
        event._set_attribute(
            Attr.GEN_AI_REQUEST_TEMPERATURE, request_temperature
        )
        event._set_attribute(Attr.GEN_AI_REQUEST_TOP_K, request_top_k)
        event._set_attribute(Attr.GEN_AI_REQUEST_TOP_P, request_top_p)
        event._set_attribute(
            Attr.GEN_AI_RESPONSE_FINISH_REASONS, response_finish_reasons
        )
        event._set_attribute(Attr.GEN_AI_RESPONSE_ID, response_id)
        event._set_attribute(Attr.GEN_AI_RESPONSE_MODEL, response_model)
        event._set_attribute(
            Attr.GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK,
            response_time_to_first_chunk,
        )
        event.set_system_instructions(system_instructions)
        event.set_tool_definitions(tool_definitions)
        event._set_attribute(
            Attr.GEN_AI_USAGE_AUDIO_CACHE_READ_INPUT_TOKENS,
            usage_audio_cache_read_input_tokens,
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_AUDIO_INPUT_TOKENS, usage_audio_input_tokens
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_AUDIO_OUTPUT_TOKENS, usage_audio_output_tokens
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS,
            usage_cache_read_input_tokens,
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_CACHE_WRITE_INPUT_TOKENS,
            usage_cache_write_input_tokens,
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_IMAGE_CACHE_READ_INPUT_TOKENS,
            usage_image_cache_read_input_tokens,
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_IMAGE_INPUT_TOKENS, usage_image_input_tokens
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_IMAGE_OUTPUT_TOKENS, usage_image_output_tokens
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_INPUT_TOKENS, usage_input_tokens
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_OUTPUT_TOKENS, usage_output_tokens
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_REASONING_OUTPUT_TOKENS,
            usage_reasoning_output_tokens,
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_TEXT_CACHE_READ_INPUT_TOKENS,
            usage_text_cache_read_input_tokens,
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_TEXT_INPUT_TOKENS, usage_text_input_tokens
        )
        event._set_attribute(
            Attr.GEN_AI_USAGE_TEXT_OUTPUT_TOKENS, usage_text_output_tokens
        )
        event._set_attribute("server.address", server_address)
        event._set_attribute("server.port", server_port)
        if additional_attributes is not None:
            event.set_attributes(additional_attributes)
        return event

    def client_operation_exception(
        self,
        *,
        exception_message: str | None = None,
        exception_stacktrace: str | None = None,
        exception_type: str | None = None,
        additional_attributes: Mapping[str, AnyValue] | None = None,
        context: Context | None = None,
    ) -> ClientOperationExceptionEvent:
        """Create a `gen_ai.client.operation.exception` event."""
        event = ClientOperationExceptionEvent(
            self._logger,
            "gen_ai.client.operation.exception",
            context=context,
        )
        event._set_attribute("exception.message", exception_message)
        event._set_attribute("exception.stacktrace", exception_stacktrace)
        event._set_attribute("exception.type", exception_type)
        if additional_attributes is not None:
            event.set_attributes(additional_attributes)
        return event

    def evaluation_result(
        self,
        *,
        evaluation_name: str,
        error_type: str | None = None,
        evaluation_explanation: str | None = None,
        evaluation_score_label: str | None = None,
        evaluation_score_value: float | None = None,
        response_id: str | None = None,
        additional_attributes: Mapping[str, AnyValue] | None = None,
        context: Context | None = None,
    ) -> EvaluationResultEvent:
        """Create a `gen_ai.evaluation.result` event."""
        event = EvaluationResultEvent(
            self._logger,
            "gen_ai.evaluation.result",
            context=context,
        )
        event._set_attribute("error.type", error_type)
        event._set_attribute(
            Attr.GEN_AI_EVALUATION_EXPLANATION, evaluation_explanation
        )
        event._set_attribute(Attr.GEN_AI_EVALUATION_NAME, evaluation_name)
        event._set_attribute(
            Attr.GEN_AI_EVALUATION_SCORE_LABEL, evaluation_score_label
        )
        event._set_attribute(
            Attr.GEN_AI_EVALUATION_SCORE_VALUE, evaluation_score_value
        )
        event._set_attribute(Attr.GEN_AI_RESPONSE_ID, response_id)
        if additional_attributes is not None:
            event.set_attributes(additional_attributes)
        return event


__all__ = [
    "ClientInferenceOperationDetailsEvent",
    "ClientOperationExceptionEvent",
    "EvaluationResultEvent",
    "_Events",
]
