from __future__ import annotations

from typing import TYPE_CHECKING, Any

from opentelemetry import trace
from opentelemetry.context import get_value

if TYPE_CHECKING:
    from opentelemetry.util.genai.handler import TelemetryHandler

_INFERENCE_ATTRIBUTES_KEY = "opentelemetry.genai.inference_attributes"
_SPANEVENT_ATTRIBUTES_KEY = "spanevent_attributes"
_METRIC_ATTRIBUTES_KEY = "metric_attributes"


def _get_inference_attributes() -> dict[str, Any] | None:
    try:
        from opentelemetry.util.genai._context import get_inference_attributes

        return get_inference_attributes()
    except ImportError:
        attrs = get_value(_INFERENCE_ATTRIBUTES_KEY)
        return attrs if isinstance(attrs, dict) else None


def _get_telemetry_handler() -> TelemetryHandler | None:
    try:
        from opentelemetry.util.genai.handler import TelemetryHandler

        return TelemetryHandler()
    except ImportError:
        return None


class DictClient:
    """Instrumentation interacting with untyped nested dicts (Dylan's prototype)."""

    def __init__(
        self,
        client: Any,
        server_address: str = "api.openai.com",
        server_port: int = 443,
    ) -> None:
        self._client = client
        self._server_address = server_address
        self._server_port = server_port
        self._tracer = trace.get_tracer("native-instr-dict")
        self._handler = _get_telemetry_handler()

    def chat(self, model: str, prompt: str) -> Any:
        ctx_attrs = _get_inference_attributes()

        # 1. Active outer invocation (suppressed): merge raw semconv strings into nested dicts
        if ctx_attrs is not None:
            response = self._client.chat(model=model, prompt=prompt)
            spanevent_map = ctx_attrs.get(_SPANEVENT_ATTRIBUTES_KEY)
            if isinstance(spanevent_map, dict):
                spanevent_map["gen_ai.response.model"] = response.model
                spanevent_map["gen_ai.usage.input_tokens"] = (
                    response.usage.input_tokens
                )
                spanevent_map["gen_ai.usage.output_tokens"] = (
                    response.usage.output_tokens
                )
                spanevent_map["server.address"] = self._server_address
                spanevent_map["server.port"] = self._server_port

            metric_map = ctx_attrs.get(_METRIC_ATTRIBUTES_KEY)
            if isinstance(metric_map, dict):
                # Must duplicate response model, server address, and port
                # into metric_map
                # not clear if these attributes are standard or custom,
                # not clear if they should all go into all metrics
                # reported for inference invocation.
                metric_map["gen_ai.response.model"] = response.model
                metric_map["server.address"] = self._server_address
                metric_map["server.port"] = self._server_port
                metric_map["custom.low_cardinality"] = "value"
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
