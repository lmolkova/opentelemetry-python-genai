# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Transparent proxy for ``with_raw_response`` / ``with_streaming_response`` results.

Mirrors the OpenAI sibling package's ``_raw_response`` module. Both anthropic
raw-response entry points hand the caller a response object whose payload is
behind ``parse()``:

* ``with_raw_response.create(...)`` returns a ``LegacyAPIResponse`` directly.
* ``with_streaming_response.create(...)`` returns an (async) context manager
  that yields an ``APIResponse`` / ``AsyncAPIResponse``.

The SDK sets the ``x-stainless-raw-response: stream`` header on *every*
``with_streaming_response`` call, streaming or not, so the request header cannot
tell us whether the parsed payload is a ``Message`` or a ``Stream``. Instead of
guessing from the header, this proxy defers to ``parse()`` and routes on what it
actually returns:

* a ``Message`` -> extract response telemetry and finalize the span now;
* a ``Stream`` / ``AsyncStream`` -> hand back an instrumented stream wrapper that
  finalizes the span when it is drained;
* a coroutine (``AsyncAPIResponse.parse`` is ``async``) -> hand back a coroutine
  that awaits the real parse and then routes by the same rules;
* anything else -> hand back untouched and log at debug.

The span is finalized independently of ``parse()``: a caller that only reads
metadata and closes the body finalizes it once via the ``close`` / ``aclose``
fallback on the underlying httpx response.
"""

from __future__ import annotations

import functools
import inspect
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, cast

from anthropic._streaming import Stream as AnthropicStream
from anthropic.types import Message as AnthropicMessage

from .wrappers import (
    AsyncMessagesStreamWrapper,
    MessagesStreamWrapper,
    MessageWrapper,
)

try:
    from anthropic._streaming import AsyncStream as _AnthropicAsyncStream
except ImportError:
    _AnthropicAsyncStream = None

if TYPE_CHECKING:
    from anthropic._streaming import AsyncStream as AnthropicAsyncStream
    from anthropic.types import RawMessageStreamEvent

    from opentelemetry.util.genai.invocation import InferenceInvocation

    # wrapt's ``ObjectProxy`` is untyped; model just the constructor we use so
    # the proxy subclass and its ``__init__`` are fully typed under pyright.
    class _ObjectProxy:
        def __init__(self, wrapped: object) -> None: ...

else:
    from wrapt import ObjectProxy as _ObjectProxy

_logger = logging.getLogger(__name__)

_INSTRUMENTABLE_STREAM_TYPES: tuple[type, ...] = tuple(
    stream_type
    for stream_type in (AnthropicStream, _AnthropicAsyncStream)
    if stream_type is not None
)


class RawResponseProxy(_ObjectProxy):
    """Proxy for a ``with_raw_response`` / ``with_streaming_response`` result.

    Callers read response metadata (``headers``, ``request_id``,
    ``http_response`` ...) off the raw response and call ``parse()`` to obtain
    the payload. Wrapping the raw response (instead of the parsed value) keeps
    every metadata attribute resolving natively, and keeps ``isinstance`` /
    ``__class__`` seeing the original type, while ``parse()`` routes on the
    value it returns. Parsing is deferred until the caller asks for it and
    memoized so repeated calls share one span.

    ``parse()`` dispatches on the parsed value rather than on any request
    header, because the SDK sets ``x-stainless-raw-response: stream`` on every
    ``with_streaming_response`` call regardless of whether the payload is a
    ``Message`` or a ``Stream``:

    * ``Message`` -> extract response telemetry and finalize the span now;
    * ``Stream`` / ``AsyncStream`` -> return an instrumented stream wrapper that
      finalizes the span when drained;
    * a coroutine (async client's ``parse()``) -> return a coroutine that awaits
      it and then dispatches by the same rules;
    * anything else -> return it untouched and log at debug.

    A memoized parse is replayed in kind: the sync client gets the value back
    directly, and the async client (whose ``parse()`` is a coroutine) gets a
    fresh awaitable that resolves to the same already-parsed value, so
    ``await raw_response.parse()`` works on the second call too.

    The span is finalized independently of ``parse()``. Whether the caller
    parses, drains the body directly, or never parses at all, every path ends by
    closing the underlying httpx response, so a fallback on its ``close`` /
    ``aclose`` finalizes the span when ``parse()`` never built (or never ran) a
    dispatch that finalized it instead.
    """

    def __init__(
        self,
        raw_response: Any,
        dispatch_message: Callable[[AnthropicMessage], None],
        wrap_stream: Callable[[Any], object | None],
        finalize: Callable[[], None],
    ) -> None:
        super().__init__(raw_response)
        self._self_response: Any = raw_response
        self._self_dispatch_message = dispatch_message
        self._self_wrap_stream = wrap_stream
        self._self_finalize: Callable[[], None] | None = finalize
        self._self_parsed: object | None = None
        self._self_async_parse = False
        self._self_parsing = False
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
        # A ``with_streaming_response`` non-streaming ``parse()`` reads and
        # closes the body while it deserializes, so the close fires *during* the
        # parse call -- before dispatch can extract the message. While a parse is
        # in flight, let that parse own finalization instead of finalizing here
        # with no response attributes.
        if self._self_parsing:
            return
        # When ``parse()`` already dispatched (extracted a message, or built a
        # stream wrapper that owns finalization), do not finalize here; only
        # finalize for callers that never parsed.
        if self._self_parsed is None:
            self._finalize_once()

    def _finalize_once(self) -> None:
        # ``stop()`` is not idempotent, so finalize at most once.
        if self._self_finalize is not None:
            finalize, self._self_finalize = self._self_finalize, None
            finalize()

    def parse(self, *args: Any, **kwargs: Any) -> object:
        # Memoize the first parse regardless of the arguments it was called
        # with, so calling parse() again returns the same value rather than
        # re-parsing. This is deliberate: one raw response backs one span, and
        # re-parsing a stream would consume it twice anyway. The async client
        # awaits ``parse()``, so replay the memoized value through a fresh
        # awaitable; the sync client hands it back directly.
        if self._self_parsed is not None:
            if self._self_async_parse:
                return self._replay_parsed()
            return self._self_parsed
        # Suppress the close fallback while the SDK reads the body: a
        # non-streaming ``parse()`` closes the response synchronously, and the
        # fallback would otherwise finalize the span before we can dispatch.
        self._self_parsing = True
        try:
            parsed: Any = self._self_response.parse(*args, **kwargs)
        except BaseException:
            # The caller's own ``parse()`` failed; let the close fallback
            # finalize the span and propagate the caller's exception unchanged.
            self._self_parsing = False
            raise
        if inspect.iscoroutine(parsed):
            # Async client: ``parse()`` is a coroutine and the body is only read
            # when it is awaited, so keep suppressing until the awaitable runs.
            self._self_async_parse = True
            return self._dispatch_awaitable(parsed)
        self._self_parsing = False
        return self._dispatch(parsed)

    async def _replay_parsed(self) -> object:
        return self._self_parsed

    async def _dispatch_awaitable(self, awaitable: Awaitable[Any]) -> object:
        try:
            parsed = await awaitable
        finally:
            self._self_parsing = False
        return self._dispatch(parsed)

    def _dispatch(self, parsed: Any) -> object:
        if isinstance(parsed, AnthropicMessage):
            try:
                self._self_dispatch_message(parsed)
            except Exception:  # pylint: disable=broad-exception-caught
                # Telemetry must never break the caller: if extraction fails,
                # log and hand the parsed message back untouched.
                _logger.debug(
                    "failed to extract raw-response message telemetry; "
                    "returning the parsed message untouched",
                    exc_info=True,
                )
            self._self_parsed = parsed
            self._finalize_once()
            return parsed
        if isinstance(parsed, _INSTRUMENTABLE_STREAM_TYPES):
            wrapped = self._self_wrap_stream(parsed)
            if wrapped is not None:
                self._self_parsed = wrapped
                return wrapped
        # Neither an SDK message nor a stream we can drive; hand it back
        # untouched. The body was likely already read/closed during parse, so
        # finalize now with the request attributes.
        _logger.debug(
            "with_raw_response.parse() returned %s, neither an SDK Message nor "
            "a stream we can drive; skipping instrumentation for this call",
            type(parsed).__name__,
        )
        self._finalize_once()
        return parsed


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
        return MessagesStreamWrapper[None](
            cast("AnthropicStream[RawMessageStreamEvent]", stream),
            invocation,
            capture_content,
        )
    if _AnthropicAsyncStream is not None and isinstance(
        stream, _AnthropicAsyncStream
    ):
        return AsyncMessagesStreamWrapper[None](
            cast("AnthropicAsyncStream[RawMessageStreamEvent]", stream),
            invocation,
            capture_content,
        )
    return None


def wrap_raw_response(
    result: Any,
    invocation: InferenceInvocation,
    capture_content: bool,
) -> Any:
    """Wrap a ``with_raw_response`` / ``with_streaming_response`` result.

    When the SDK has already read the body to completion (the non-streaming
    ``with_raw_response`` path), the operation is over: ``parse()`` is a memoized
    deserialization with nothing left to wait for, so the span is finalized here
    and the caller gets its raw response untouched.

    While the body is still open, the caller owns when it is read, so the result
    is wrapped so its metadata resolves natively and ``parse()`` routes on the
    value it returns: a ``Message`` finalizes the span immediately with response
    telemetry, a ``Stream`` / ``AsyncStream`` becomes an instrumented wrapper
    that finalizes on drain, and a coroutine is awaited before dispatching. When
    the caller never parses, the close fallback finalizes the span once.
    """
    http_response = getattr(result, "http_response", None)
    if getattr(http_response, "is_closed", False):
        try:
            parsed = result.parse()
        except Exception:  # pylint: disable=broad-exception-caught
            _logger.debug(
                "raw-response parse() failed; skipping response telemetry",
                exc_info=True,
            )
        else:
            if isinstance(parsed, AnthropicMessage):
                MessageWrapper(parsed, capture_content).extract_into(
                    invocation
                )
        invocation.stop()
        return result

    return RawResponseProxy(
        result,
        dispatch_message=lambda message: MessageWrapper(
            message, capture_content
        ).extract_into(invocation),
        wrap_stream=lambda stream: _wrap_parsed_stream(
            stream, invocation, capture_content
        ),
        finalize=invocation.stop,
    )
