# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

import os

from portkey_ai import Portkey

client = Portkey(
    api_key="test_portkey_api_key",
    base_url=f"{os.environ['MOCK_SERVER_URL']}/v1",
    provider="openai",
)

client.chat.completions.create(
    messages=[{"role": "user", "content": "Say this is a test"}],
    model="gpt-4o-mini",
    stream=False,
)
