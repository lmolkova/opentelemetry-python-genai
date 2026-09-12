# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

from typing import Final

CLIENT_OPERATION_DURATION: Final = [
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

CLIENT_TOKEN_USAGE: Final = [
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

INVOKE_WORKFLOW_DURATION: Final = [
    1,
    5,
    10,
    30,
    60,
    120,
    300,
    600,
    1800,
    3600,
    7200,
]

INVOKE_AGENT_DURATION: Final = [
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
]

__all__ = [
    "CLIENT_OPERATION_DURATION",
    "CLIENT_TOKEN_USAGE",
    "INVOKE_AGENT_DURATION",
    "INVOKE_WORKFLOW_DURATION",
]
