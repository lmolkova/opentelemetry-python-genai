# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
# Code generated from OpenTelemetry GenAI semantic conventions. DO NOT EDIT.

from enum import Enum
from typing import Final

GEN_AI_PROVIDER_NAME: Final[str] = "gen_ai.provider.name"
"""The Generative AI provider as identified by the client or server instrumentation."""

GEN_AI_REQUEST_MODEL: Final[str] = "gen_ai.request.model"
"""The name of the GenAI model a request is being made to."""

GEN_AI_REQUEST_MAX_TOKENS: Final[str] = "gen_ai.request.max_tokens"
"""The maximum number of tokens the model generates for a request."""

GEN_AI_REQUEST_CHOICE_COUNT: Final[str] = "gen_ai.request.choice.count"
"""The target number of candidate completions to return."""

GEN_AI_REQUEST_TEMPERATURE: Final[str] = "gen_ai.request.temperature"
"""The temperature setting for the GenAI request."""

GEN_AI_REQUEST_TOP_P: Final[str] = "gen_ai.request.top_p"
"""The top_p sampling setting for the GenAI request."""

GEN_AI_REQUEST_TOP_K: Final[str] = "gen_ai.request.top_k"
"""The top-K sampling setting for the GenAI request: restricts token generation at each step to the K most likely next tokens."""

GEN_AI_REQUEST_STOP_SEQUENCES: Final[str] = "gen_ai.request.stop_sequences"
"""List of sequences that the model will use to stop generating further tokens."""

GEN_AI_REQUEST_FREQUENCY_PENALTY: Final[str] = (
    "gen_ai.request.frequency_penalty"
)
"""The frequency penalty setting for the GenAI request."""

GEN_AI_REQUEST_PRESENCE_PENALTY: Final[str] = "gen_ai.request.presence_penalty"
"""The presence penalty setting for the GenAI request."""

GEN_AI_REQUEST_ENCODING_FORMATS: Final[str] = "gen_ai.request.encoding_formats"
"""The encoding formats requested in an embeddings operation, if specified."""

GEN_AI_REQUEST_SEED: Final[str] = "gen_ai.request.seed"
"""Requests with same seed value more likely to return same result."""

GEN_AI_REQUEST_STREAM: Final[str] = "gen_ai.request.stream"
"""Indicates whether the GenAI request was made in streaming mode."""

GEN_AI_REQUEST_REASONING_LEVEL: Final[str] = "gen_ai.request.reasoning.level"
"""The reasoning or thinking effort level requested for a GenAI model."""

GEN_AI_REQUEST_PREVIOUS_RESPONSE_ID: Final[str] = (
    "gen_ai.request.previous_response.id"
)
"""The unique identifier of a previous response or interaction used to provide context for the current operation."""

GEN_AI_REQUEST_STREAM_CURSOR: Final[str] = "gen_ai.request.stream_cursor"
"""The cursor identifying the last streamed event already received, used to resume a streamed response from that position."""

GEN_AI_RESPONSE_ID: Final[str] = "gen_ai.response.id"
"""The unique identifier for the completion."""

GEN_AI_RESPONSE_MODEL: Final[str] = "gen_ai.response.model"
"""The name of the model that generated the response."""

GEN_AI_RESPONSE_FINISH_REASONS: Final[str] = "gen_ai.response.finish_reasons"
"""Array of reasons the model stopped generating tokens, corresponding to each generation received."""

GEN_AI_RESPONSE_STATUS: Final[str] = "gen_ai.response.status"
"""The lifecycle status of a generated response, as reported by the provider when the response is fetched or polled."""

GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK: Final[str] = (
    "gen_ai.response.time_to_first_chunk"
)
"""Time to first chunk in a streaming response, measured from request issuance, in seconds. The value is measured from when the client issues the generation request to when the first chunk is received in the response stream."""

GEN_AI_USAGE_INPUT_TOKENS: Final[str] = "gen_ai.usage.input_tokens"
"""The number of tokens used in the GenAI input (prompt)."""

GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS: Final[str] = (
    "gen_ai.usage.cache_read.input_tokens"
)
"""The number of input tokens served from a provider-managed cache."""

GEN_AI_USAGE_CACHE_WRITE_INPUT_TOKENS: Final[str] = (
    "gen_ai.usage.cache_write.input_tokens"
)
"""The number of input tokens written to a provider-managed cache."""

GEN_AI_USAGE_TEXT_INPUT_TOKENS: Final[str] = "gen_ai.usage.text.input_tokens"
"""The number of text input tokens."""

GEN_AI_USAGE_IMAGE_INPUT_TOKENS: Final[str] = "gen_ai.usage.image.input_tokens"
"""The number of image input tokens."""

GEN_AI_USAGE_AUDIO_INPUT_TOKENS: Final[str] = "gen_ai.usage.audio.input_tokens"
"""The number of audio input tokens."""

GEN_AI_USAGE_OUTPUT_TOKENS: Final[str] = "gen_ai.usage.output_tokens"
"""The number of tokens used in the GenAI response (completion)."""

GEN_AI_USAGE_REASONING_OUTPUT_TOKENS: Final[str] = (
    "gen_ai.usage.reasoning.output_tokens"
)
"""The number of output tokens used for reasoning (e.g. chain-of-thought, extended thinking)."""

GEN_AI_USAGE_TEXT_OUTPUT_TOKENS: Final[str] = "gen_ai.usage.text.output_tokens"
"""The number of text output tokens."""

GEN_AI_USAGE_IMAGE_OUTPUT_TOKENS: Final[str] = (
    "gen_ai.usage.image.output_tokens"
)
"""The number of image output tokens."""

GEN_AI_USAGE_AUDIO_OUTPUT_TOKENS: Final[str] = (
    "gen_ai.usage.audio.output_tokens"
)
"""The number of audio output tokens."""

GEN_AI_USAGE_TEXT_CACHE_READ_INPUT_TOKENS: Final[str] = (
    "gen_ai.usage.text.cache_read.input_tokens"
)
"""The number of text input tokens served from a provider-managed cache."""

GEN_AI_USAGE_IMAGE_CACHE_READ_INPUT_TOKENS: Final[str] = (
    "gen_ai.usage.image.cache_read.input_tokens"
)
"""The number of image input tokens served from a provider-managed cache."""

GEN_AI_USAGE_AUDIO_CACHE_READ_INPUT_TOKENS: Final[str] = (
    "gen_ai.usage.audio.cache_read.input_tokens"
)
"""The number of audio input tokens served from a provider-managed cache."""

GEN_AI_TOKEN_TYPE: Final[str] = "gen_ai.token.type"
"""The type of token being counted."""

GEN_AI_CONVERSATION_ID: Final[str] = "gen_ai.conversation.id"
"""The unique identifier for a conversation (session, thread), used to store and correlate messages within this conversation."""

GEN_AI_CONVERSATION_COMPACTED: Final[str] = "gen_ai.conversation.compacted"
"""Indicates whether the effective conversation context used for this operation is a compacted view of a prior conversation."""

GEN_AI_AGENT_ID: Final[str] = "gen_ai.agent.id"
"""The unique and stable identifier of the GenAI hosted agent resource."""

GEN_AI_AGENT_NAME: Final[str] = "gen_ai.agent.name"
"""Human-readable name of the GenAI agent provided by the application."""

GEN_AI_AGENT_DESCRIPTION: Final[str] = "gen_ai.agent.description"
"""Free-form description of the GenAI agent provided by the application."""

GEN_AI_AGENT_VERSION: Final[str] = "gen_ai.agent.version"
"""The version of the GenAI agent."""

GEN_AI_TOOL_NAME: Final[str] = "gen_ai.tool.name"
"""Name of the tool utilized by the agent."""

GEN_AI_TOOL_CALL_ID: Final[str] = "gen_ai.tool.call.id"
"""The tool call identifier."""

GEN_AI_TOOL_DESCRIPTION: Final[str] = "gen_ai.tool.description"
"""The tool description."""

GEN_AI_TOOL_TYPE: Final[str] = "gen_ai.tool.type"
"""Type of the tool utilized by the agent"""

GEN_AI_TOOL_CALL_ARGUMENTS: Final[str] = "gen_ai.tool.call.arguments"
"""Parameters passed to the tool call."""

GEN_AI_TOOL_CALL_RESULT: Final[str] = "gen_ai.tool.call.result"
"""The result returned by the tool call (if any and if execution was successful)."""

GEN_AI_TOOL_DEFINITIONS: Final[str] = "gen_ai.tool.definitions"
"""The list of tool definitions available to the GenAI agent or model."""

GEN_AI_DATA_SOURCE_ID: Final[str] = "gen_ai.data_source.id"
"""The data source identifier."""

GEN_AI_OPERATION_NAME: Final[str] = "gen_ai.operation.name"
"""The name of the operation being performed."""

GEN_AI_OUTPUT_TYPE: Final[str] = "gen_ai.output.type"
"""Represents the content type requested by the client."""

GEN_AI_EMBEDDINGS_DIMENSION_COUNT: Final[str] = (
    "gen_ai.embeddings.dimension.count"
)
"""The number of dimensions the resulting output embeddings should have."""

GEN_AI_RETRIEVAL_DOCUMENTS: Final[str] = "gen_ai.retrieval.documents"
"""The documents retrieved."""

GEN_AI_RETRIEVAL_QUERY_TEXT: Final[str] = "gen_ai.retrieval.query.text"
"""The query text used for retrieval."""

GEN_AI_RETRIEVAL_TOP_K: Final[str] = "gen_ai.retrieval.top_k"
"""The maximum number of documents the retriever was asked to return for the query (also known as `k`, `limit`, or `max_num_results`)."""

GEN_AI_MEMORY_STORE_ID: Final[str] = "gen_ai.memory.store.id"
"""The unique identifier of the memory store."""

GEN_AI_MEMORY_RECORD_ID: Final[str] = "gen_ai.memory.record.id"
"""The unique identifier of the memory record."""

GEN_AI_MEMORY_RECORD_COUNT: Final[str] = "gen_ai.memory.record.count"
"""The number of memory records relevant to the operation."""

GEN_AI_MEMORY_QUERY_TEXT: Final[str] = "gen_ai.memory.query.text"
"""The search query used to retrieve memories."""

GEN_AI_MEMORY_RECORDS: Final[str] = "gen_ai.memory.records"
"""The memory records stored or retrieved in a memory operation."""

GEN_AI_SYSTEM_INSTRUCTIONS: Final[str] = "gen_ai.system_instructions"
"""The system message or instructions provided to the GenAI model separately from the chat history."""

GEN_AI_INPUT_MESSAGES: Final[str] = "gen_ai.input.messages"
"""The chat history provided to the model as an input."""

GEN_AI_OUTPUT_MESSAGES: Final[str] = "gen_ai.output.messages"
"""Messages returned by the model where each message represents a specific model response (choice, candidate)."""

GEN_AI_EVALUATION_NAME: Final[str] = "gen_ai.evaluation.name"
"""The name of the evaluation metric used for the GenAI response."""

GEN_AI_EVALUATION_SCORE_VALUE: Final[str] = "gen_ai.evaluation.score.value"
"""The evaluation score returned by the evaluator."""

GEN_AI_EVALUATION_SCORE_LABEL: Final[str] = "gen_ai.evaluation.score.label"
"""Human readable label for evaluation."""

GEN_AI_EVALUATION_EXPLANATION: Final[str] = "gen_ai.evaluation.explanation"
"""A free-form explanation for the assigned score provided by the evaluator."""

GEN_AI_PROMPT_NAME: Final[str] = "gen_ai.prompt.name"
"""The name of the prompt that uniquely identifies it."""

GEN_AI_PROMPT_VERSION: Final[str] = "gen_ai.prompt.version"
"""The version of the prompt template used."""

GEN_AI_PROMPT_VARIABLE: Final[str] = "gen_ai.prompt.variable"
"""The variables supplied to the prompt template, the `<key>` being the variable name, the value being the variable value."""

GEN_AI_WORKFLOW_NAME: Final[str] = "gen_ai.workflow.name"
"""Human-readable name of the GenAI workflow provided by the application."""


class GenAiProviderName(str, Enum):
    """Known values for `gen_ai.provider.name`."""

    OPENAI = "openai"
    GCP_GEN_AI = "gcp.gen_ai"
    GCP_VERTEX_AI = "gcp.vertex_ai"
    GCP_GEMINI = "gcp.gemini"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    AZURE_AI_INFERENCE = "azure.ai.inference"
    AZURE_AI_OPENAI = "azure.ai.openai"
    IBM_WATSONX_AI = "ibm.watsonx.ai"
    AWS_BEDROCK = "aws.bedrock"
    PERPLEXITY = "perplexity"
    X_AI = "x_ai"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    MISTRAL_AI = "mistral_ai"
    MOONSHOT_AI = "moonshot_ai"


class GenAiResponseStatus(str, Enum):
    """Known values for `gen_ai.response.status`."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenAiTokenType(str, Enum):
    """Known values for `gen_ai.token.type`."""

    INPUT = "input"
    OUTPUT = "output"


class GenAiOperationName(str, Enum):
    """Known values for `gen_ai.operation.name`."""

    CHAT = "chat"
    GENERATE_CONTENT = "generate_content"
    TEXT_COMPLETION = "text_completion"
    EMBEDDINGS = "embeddings"
    RETRIEVAL = "retrieval"
    FETCH_RESPONSE = "fetch_response"
    CREATE_AGENT = "create_agent"
    INVOKE_AGENT = "invoke_agent"
    EXECUTE_TOOL = "execute_tool"
    INVOKE_WORKFLOW = "invoke_workflow"
    PLAN = "plan"
    SEARCH_MEMORY = "search_memory"
    CREATE_MEMORY = "create_memory"
    UPDATE_MEMORY = "update_memory"
    UPSERT_MEMORY = "upsert_memory"
    DELETE_MEMORY = "delete_memory"
    CREATE_MEMORY_STORE = "create_memory_store"
    DELETE_MEMORY_STORE = "delete_memory_store"


class GenAiOutputType(str, Enum):
    """Known values for `gen_ai.output.type`."""

    TEXT = "text"
    JSON = "json"
    IMAGE = "image"
    SPEECH = "speech"


__all__ = [
    "GEN_AI_AGENT_DESCRIPTION",
    "GEN_AI_AGENT_ID",
    "GEN_AI_AGENT_NAME",
    "GEN_AI_AGENT_VERSION",
    "GEN_AI_CONVERSATION_COMPACTED",
    "GEN_AI_CONVERSATION_ID",
    "GEN_AI_DATA_SOURCE_ID",
    "GEN_AI_EMBEDDINGS_DIMENSION_COUNT",
    "GEN_AI_EVALUATION_EXPLANATION",
    "GEN_AI_EVALUATION_NAME",
    "GEN_AI_EVALUATION_SCORE_LABEL",
    "GEN_AI_EVALUATION_SCORE_VALUE",
    "GEN_AI_INPUT_MESSAGES",
    "GEN_AI_MEMORY_QUERY_TEXT",
    "GEN_AI_MEMORY_RECORDS",
    "GEN_AI_MEMORY_RECORD_COUNT",
    "GEN_AI_MEMORY_RECORD_ID",
    "GEN_AI_MEMORY_STORE_ID",
    "GEN_AI_OPERATION_NAME",
    "GEN_AI_OUTPUT_MESSAGES",
    "GEN_AI_OUTPUT_TYPE",
    "GEN_AI_PROMPT_NAME",
    "GEN_AI_PROMPT_VARIABLE",
    "GEN_AI_PROMPT_VERSION",
    "GEN_AI_PROVIDER_NAME",
    "GEN_AI_REQUEST_CHOICE_COUNT",
    "GEN_AI_REQUEST_ENCODING_FORMATS",
    "GEN_AI_REQUEST_FREQUENCY_PENALTY",
    "GEN_AI_REQUEST_MAX_TOKENS",
    "GEN_AI_REQUEST_MODEL",
    "GEN_AI_REQUEST_PRESENCE_PENALTY",
    "GEN_AI_REQUEST_PREVIOUS_RESPONSE_ID",
    "GEN_AI_REQUEST_REASONING_LEVEL",
    "GEN_AI_REQUEST_SEED",
    "GEN_AI_REQUEST_STOP_SEQUENCES",
    "GEN_AI_REQUEST_STREAM",
    "GEN_AI_REQUEST_STREAM_CURSOR",
    "GEN_AI_REQUEST_TEMPERATURE",
    "GEN_AI_REQUEST_TOP_K",
    "GEN_AI_REQUEST_TOP_P",
    "GEN_AI_RESPONSE_FINISH_REASONS",
    "GEN_AI_RESPONSE_ID",
    "GEN_AI_RESPONSE_MODEL",
    "GEN_AI_RESPONSE_STATUS",
    "GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK",
    "GEN_AI_RETRIEVAL_DOCUMENTS",
    "GEN_AI_RETRIEVAL_QUERY_TEXT",
    "GEN_AI_RETRIEVAL_TOP_K",
    "GEN_AI_SYSTEM_INSTRUCTIONS",
    "GEN_AI_TOKEN_TYPE",
    "GEN_AI_TOOL_CALL_ARGUMENTS",
    "GEN_AI_TOOL_CALL_ID",
    "GEN_AI_TOOL_CALL_RESULT",
    "GEN_AI_TOOL_DEFINITIONS",
    "GEN_AI_TOOL_DESCRIPTION",
    "GEN_AI_TOOL_NAME",
    "GEN_AI_TOOL_TYPE",
    "GEN_AI_USAGE_AUDIO_CACHE_READ_INPUT_TOKENS",
    "GEN_AI_USAGE_AUDIO_INPUT_TOKENS",
    "GEN_AI_USAGE_AUDIO_OUTPUT_TOKENS",
    "GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS",
    "GEN_AI_USAGE_CACHE_WRITE_INPUT_TOKENS",
    "GEN_AI_USAGE_IMAGE_CACHE_READ_INPUT_TOKENS",
    "GEN_AI_USAGE_IMAGE_INPUT_TOKENS",
    "GEN_AI_USAGE_IMAGE_OUTPUT_TOKENS",
    "GEN_AI_USAGE_INPUT_TOKENS",
    "GEN_AI_USAGE_OUTPUT_TOKENS",
    "GEN_AI_USAGE_REASONING_OUTPUT_TOKENS",
    "GEN_AI_USAGE_TEXT_CACHE_READ_INPUT_TOKENS",
    "GEN_AI_USAGE_TEXT_INPUT_TOKENS",
    "GEN_AI_USAGE_TEXT_OUTPUT_TOKENS",
    "GEN_AI_WORKFLOW_NAME",
    "GenAiOperationName",
    "GenAiOutputType",
    "GenAiProviderName",
    "GenAiResponseStatus",
    "GenAiTokenType",
]
