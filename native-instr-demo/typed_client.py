from __future__ import annotations

from typing import TYPE_CHECKING, Any

from opentelemetry import trace

if TYPE_CHECKING:
    from opentelemetry.util.genai._context import InferenceContextData
    from opentelemetry.util.genai.handler import TelemetryHandler


def _get_context_data() -> InferenceContextData | None:
    try:
        from opentelemetry.util.genai._context import (
            get_inference_context_data,
        )

        return get_inference_context_data()
    except ImportError:
        return None


def _get_telemetry_handler() -> TelemetryHandler | None:
    try:
        from opentelemetry.util.genai.handler import TelemetryHandler

        return TelemetryHandler()
    except ImportError:
        return None


class TypedClient:
    """Instrumentation interacting with typed InferenceContextData."""

    def __init__(
        self,
        client: Any,
        server_address: str = "api.openai.com",
        server_port: int = 443,
    ) -> None:
        self._client = client
        self._server_address = server_address
        self._server_port = server_port
        self._tracer = trace.get_tracer("native-instr-typed")
        self._handler = _get_telemetry_handler()

    def chat(self, model: str, prompt: str) -> Any:
        ctx_data = _get_context_data()

        # 1. Active outer invocation (suppressed): enrich typed fields directly
        if ctx_data is not None:
            response = self._client.chat(model=model, prompt=prompt)
            ctx_data.response_model = response.model
            ctx_data.input_tokens = response.usage.input_tokens
            ctx_data.output_tokens = response.usage.output_tokens
            ctx_data.server_address = self._server_address
            ctx_data.server_port = self._server_port
            ctx_data.metric_attributes["custom.low_cardinality"] = "value"
            return response

        # 2. Standalone with util-genai: full rich telemetry
        if self._handler is not None:
            with self._handler.inference(
                "my-provider",
                request_model=model,
                server_address=self._server_address,
                server_port=self._server_port,
            ) as inv:
                inv.metric_attributes["custom.low_cardinality"] = "value"
                response = self._client.chat(model=model, prompt=prompt)
                inv.response_model_name = response.model
                inv.input_tokens = response.usage.input_tokens
                inv.output_tokens = response.usage.output_tokens
                return response

        # 3. Standalone without util-genai: standard OTel API only
        with self._tracer.start_as_current_span(
            f"chat {model}",
            attributes={
                "gen_ai.provider.name": "my-provider",
                "gen_ai.request.model": model,
                "server.address": self._server_address,
                "server.port": self._server_port,
            },
        ) as span:
            response = self._client.chat(model=model, prompt=prompt)
            span.set_attributes(
                {
                    "gen_ai.response.model": response.model,
                    "gen_ai.usage.input_tokens": response.usage.input_tokens,
                    "gen_ai.usage.output_tokens": response.usage.output_tokens,
                }
            )
            return response
