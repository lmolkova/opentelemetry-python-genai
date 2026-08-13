# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Transparent proxy for streaming ``with_raw_response`` results.

Mirrors the OpenAI sibling package's ``_raw_response`` module. The anthropic
SDK returns a raw-response object (a ``LegacyAPIResponse``) from
``with_raw_response.create(stream=True)`` and from ``with_streaming_response``,
not a ``Stream``. That object falls past the ``isinstance(result,
AnthropicStream)`` check in ``patch.py``, so without this proxy the span is
ended immediately with no response attributes, before the caller ever calls
``parse()``.
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from anthropic._streaming import Stream as AnthropicStream
from wrapt import ObjectProxy

from .wrappers import AsyncMessagesStreamWrapper, MessagesStreamWrapper

try:
    from anthropic._streaming import AsyncStream as _AnthropicAsyncStream
except ImportError:
    _AnthropicAsyncStream = None

if TYPE_CHECKING:
    from opentelemetry.util.genai.invocation import InferenceInvocation

_logger = logging.getLogger(__name__)

_INSTRUMENTABLE_STREAM_TYPES: tuple[type, ...] = (AnthropicStream,)
if _AnthropicAsyncStream is not None:
    _INSTRUMENTABLE_STREAM_TYPES += (_AnthropicAsyncStream,)


class RawResponseStreamProxy(ObjectProxy):
    """Proxy for a streaming ``with_raw_response`` result.

    Callers read response metadata (``headers``, ``request_id``,
    ``http_response`` ...) off the raw response and call ``parse()`` to obtain
    the stream. Wrapping the raw response (instead of the parsed stream) keeps
    every metadata attribute resolving natively, and keeps ``isinstance`` /
    ``__class__`` seeing the original type, while ``parse()`` returns an
    instrumented stream wrapper. Parsing is deferred until the caller asks for
    it and memoized so repeated calls share one span.

    ``parse()`` wraps the result only when it is an SDK ``Stream`` /
    ``AsyncStream`` we know how to drive. Anything else is handed back
    untouched (for example the coroutine ``parse()`` becomes on the non-legacy
    async streaming response, or a custom non-stream target): we cannot
    instrument it, so we log and step aside.

    The span is finalized independently of ``parse()``. Whether the caller
    parses and drains the wrapper, drains the body directly, or never parses at
    all, every path ends by closing the underlying httpx response, so a
    fallback on its ``close`` / ``aclose`` finalizes the span when ``parse()``
    never built a wrapper that would finalize it instead.
    """

    def __init__(
        self,
        raw_response: Any,
        wrap_stream: Callable[[Any], object | None],
        finalize: Callable[[], None],
    ) -> None:
        super().__init__(raw_response)
        self._self_wrap_stream = wrap_stream
        self._self_finalize: Callable[[], None] | None = finalize
        self._self_parsed: object | None = None
        self._install_close_fallback(raw_response)

    def _install_close_fallback(self, raw_response: Any) -> None:
        # httpx exposes a sync ``close`` and an async ``aclose``; wrap whichever
        # the underlying response has so the appropriate one finalizes the span.
        http_response = getattr(raw_response, "http_response", None)
        if http_response is None:
            return
        close = getattr(http_response, "close", None)
        if close is not None:
            http_response.close = self._wrap_sync_close(close)
        aclose = getattr(http_response, "aclose", None)
        if aclose is not None:
            http_response.aclose = self._wrap_async_close(aclose)

    def _wrap_sync_close(
        self, original: Callable[..., object]
    ) -> Callable[..., object]:
        @functools.wraps(original)
        def _close(*args: object, **kwargs: object) -> object:
            try:
                return original(*args, **kwargs)
            finally:
                self._finalize_close_fallback()

        return _close

    def _wrap_async_close(
        self, original: Callable[..., Awaitable[object]]
    ) -> Callable[..., Awaitable[object]]:
        @functools.wraps(original)
        async def _aclose(*args: object, **kwargs: object) -> object:
            try:
                return await original(*args, **kwargs)
            finally:
                self._finalize_close_fallback()

        return _aclose

    def _finalize_close_fallback(self) -> None:
        # When ``parse()`` built a stream wrapper, that wrapper owns
        # finalization; only finalize here for callers that never parsed.
        if self._self_parsed is None:
            self._finalize_once()

    def _finalize_once(self) -> None:
        # ``stop()`` is not idempotent, so finalize at most once.
        if self._self_finalize is not None:
            finalize, self._self_finalize = self._self_finalize, None
            finalize()

    def parse(self, *args: Any, **kwargs: Any) -> object:
        # Memoize the first parse regardless of the arguments it was called
        # with, so calling parse() again returns the same wrapper rather than
        # re-parsing. This is deliberate: one raw response backs one span, and
        # re-parsing a stream would consume it twice anyway.
        if self._self_parsed is not None:
            return self._self_parsed
        stream = self.__wrapped__.parse(*args, **kwargs)
        if isinstance(stream, _INSTRUMENTABLE_STREAM_TYPES):
            wrapped = self._self_wrap_stream(stream)
            if wrapped is not None:
                self._self_parsed = wrapped
                return wrapped
        # Not a stream we can drive; hand it back untouched. The close fallback
        # finalizes the span once the caller drains/closes the response body.
        _logger.debug(
            "with_raw_response.parse() returned %s, not an SDK stream; "
            "skipping stream instrumentation for this call",
            type(stream).__name__,
        )
        return stream


def _wrap_parsed_stream(
    stream: Any,
    invocation: InferenceInvocation,
    capture_content: bool,
) -> object | None:
    """Wrap a parsed stream in the matching instrumented wrapper.

    Handles both the sync (``Stream`` -> ``MessagesStreamWrapper``) and async
    (``AsyncStream`` -> ``AsyncMessagesStreamWrapper``) cases: the async
    client's legacy raw response returns an ``AsyncStream`` from its sync
    ``parse()``. Returns ``None`` for anything we cannot drive.
    """
    if isinstance(stream, AnthropicStream):
        return MessagesStreamWrapper(stream, invocation, capture_content)
    if _AnthropicAsyncStream is not None and isinstance(
        stream, _AnthropicAsyncStream
    ):
        return AsyncMessagesStreamWrapper(stream, invocation, capture_content)
    return None


def wrap_raw_stream_result(
    result: Any,
    invocation: InferenceInvocation,
    capture_content: bool,
) -> RawResponseStreamProxy:
    """Wrap a streaming ``with_raw_response`` result, deferring ``parse()``.

    The raw response is wrapped so its metadata resolves natively and
    ``parse()`` returns an instrumented ``MessagesStreamWrapper`` /
    ``AsyncMessagesStreamWrapper`` only once the caller asks for it. The span
    is finalized by the parsed wrapper when drained, or by the close fallback
    when the caller drains/closes the body without parsing.
    """
    return RawResponseStreamProxy(
        result,
        lambda stream: _wrap_parsed_stream(
            stream, invocation, capture_content
        ),
        finalize=invocation.stop,
    )
