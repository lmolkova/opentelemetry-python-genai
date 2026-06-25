# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from opentelemetry.metrics import Histogram, Meter
from opentelemetry.semconv._incubating.metrics import gen_ai_metrics

# PROTOTYPE: these metric names are not yet in opentelemetry.semconv. They track
# semantic-conventions-genai PR #336 (gen_ai.invoke_agent.{inference,tool}_calls).
# Replace these literals with gen_ai_metrics constants once that PR ships.
_GEN_AI_INVOKE_AGENT_INFERENCE_CALLS = "gen_ai.invoke_agent.inference_calls"
_GEN_AI_INVOKE_AGENT_TOOL_CALLS = "gen_ai.invoke_agent.tool_calls"

_GEN_AI_INVOKE_AGENT_CALLS_BUCKETS = [
    0,
    1,
    2,
    4,
    8,
    16,
    32,
    64,
]

_GEN_AI_CLIENT_OPERATION_DURATION_BUCKETS = [
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
]

_GEN_AI_CLIENT_TOKEN_USAGE_BUCKETS = [
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
]


def create_duration_histogram(meter: Meter) -> Histogram:
    return meter.create_histogram(
        name=gen_ai_metrics.GEN_AI_CLIENT_OPERATION_DURATION,
        description="Duration of GenAI client operation",
        unit="s",
        explicit_bucket_boundaries_advisory=_GEN_AI_CLIENT_OPERATION_DURATION_BUCKETS,
    )


def create_token_histogram(meter: Meter) -> Histogram:
    return meter.create_histogram(
        name=gen_ai_metrics.GEN_AI_CLIENT_TOKEN_USAGE,
        description="Number of input and output tokens used by GenAI clients",
        unit="{token}",
        explicit_bucket_boundaries_advisory=_GEN_AI_CLIENT_TOKEN_USAGE_BUCKETS,
    )


def create_agent_inference_calls_histogram(meter: Meter) -> Histogram:
    return meter.create_histogram(
        name=_GEN_AI_INVOKE_AGENT_INFERENCE_CALLS,
        description="Number of inference (model) calls a GenAI agent makes during a single invocation",
        unit="{inference_call}",
        explicit_bucket_boundaries_advisory=_GEN_AI_INVOKE_AGENT_CALLS_BUCKETS,
    )


def create_agent_tool_calls_histogram(meter: Meter) -> Histogram:
    return meter.create_histogram(
        name=_GEN_AI_INVOKE_AGENT_TOOL_CALLS,
        description="Number of tool calls a GenAI agent makes during a single invocation",
        unit="{tool_call}",
        explicit_bucket_boundaries_advisory=_GEN_AI_INVOKE_AGENT_CALLS_BUCKETS,
    )
