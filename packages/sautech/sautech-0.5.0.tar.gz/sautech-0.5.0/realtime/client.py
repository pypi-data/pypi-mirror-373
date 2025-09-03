from __future__ import annotations

import asyncio
import struct
import uuid as _uuid
from typing import Callable, Optional

import socketio
from loguru import logger

from ..constants import (
    EVENT_FT_TRANSCRIBE_RESULT,
    EVENT_RT_AUDIO_STREAM,
    EVENT_RT_END_AUDIO_STREAM,
    LanguageEnum,
)
from ..types import ErrorResponse, RtTranscribeResponse

RtTranscribeHandler = Callable[[RtTranscribeResponse], None]


class RealtimeClient:
    def __init__(
        self,
        api_url: str,
        api_path: str,
        api_key: str,
        language: LanguageEnum,
        on_connect: Optional[Callable[[]]] = lambda: None,
        on_disconnect: Optional[Callable[[]]] = lambda: None,
        on_response: Optional[RtTranscribeHandler] = lambda: None,
        on_error: Optional[Callable[[ErrorResponse], None]] = lambda: None,
    ):
        if not api_url or not api_path or not api_key:
            raise ValueError("api_url, api_path, and api_key are required")

        self._api_url = api_url
        self._api_path = api_path
        self._api_key = api_key
        self._language = language
        self.on_connect: Optional[Callable[[]]] = on_connect
        self.on_disconnect: Optional[Callable[[]]] = on_disconnect
        self.on_response: Optional[RtTranscribeHandler] = on_response
        self.on_error: Optional[Callable[[object]]] = on_error

        self._sio: socketio.AsyncClient = socketio.AsyncClient()
        self._session_id: _uuid.UUID = _uuid.uuid4()
        self._session_bytes: bytes = self._session_id.bytes
        self._first_chunk_sent: bool = False
        self._final_event: asyncio.Event = asyncio.Event()

        @self._sio.event
        async def connect():
            try:
                self.on_connect()
            except Exception:
                logger.exception("on_connect handler raised")

        @self._sio.event
        async def disconnect():
            try:
                self.on_disconnect()
            except Exception:
                logger.exception("on_disconnect handler raised")

        @self._sio.on("error")
        async def _on_error(data):
            model = ErrorResponse.model_validate(data)
            self.on_error(model)

        @self._sio.on(EVENT_FT_TRANSCRIBE_RESULT)
        async def _on_transcription_result(data):
            try:
                model = RtTranscribeResponse.model_validate(data)
                if model.transcription:
                    self.on_response(model)
                if model.is_speech_final:
                    if not self._final_event.is_set():
                        self._final_event.set()
            except Exception:
                logger.exception("Failed to process realtime transcription result")

    async def connect(self) -> None:
        if self._sio.connected:
            return
        await self._sio.connect(
            self._api_url,
            headers={"x-api-key": self._api_key},
            socketio_path=self._api_path,
            transports=["websocket"],
        )

    async def disconnect(self) -> None:
        if self._sio.connected:
            await self._sio.disconnect()

    # Public API
    async def start(self) -> None:
        """Connects and registers callbacks; sends an initialization frame.

        Users then call send(audio_bytes) repeatedly to stream audio.
        """
        self._first_chunk_sent = False

        await self.connect()

    async def stop(self) -> None:
        """Signals end of stream and disconnects."""
        try:
            # Emit end-of-stream control event (JS client parity)
            await self._sio.emit(
                EVENT_RT_END_AUDIO_STREAM,
                {"transcription_id": str(self._session_id)},
            )
        except Exception:
            logger.exception("Failed to emit end-of-stream")
        finally:
            await self.disconnect()

    async def send(self, audio_bytes: bytes, is_last: bool = False) -> None:
        """Send a chunk of streamed audio bytes using JS parity framing.

        Frame: [uuid (16 bytes)][flags (1 byte)][lang_id (1 byte)][audio bytes]
        - flags bit 0x01: first chunk
        - flags bit 0x02: last chunk
        """
        if not self._sio.connected:
            await self.connect()

        flags = 0
        if not self._first_chunk_sent:
            flags |= 0x01
            self._first_chunk_sent = True
        if is_last:
            flags |= 0x02

        payload = (
            self._session_bytes
            + struct.pack("<B", flags)
            + struct.pack("<B", int(self._language))
            + audio_bytes
        )
        await self._sio.emit(EVENT_RT_AUDIO_STREAM, payload)

    async def close(
        self,
        timeout: float = 1.0,
    ) -> None:
        """
        Send a final flag and wait for the final transcription result.
        If the final transcription result is not received within the timeout, give a warning and return.

        Args:
            timeout: The timeout in seconds to wait for the final transcription result.
        """
        self._final_event = asyncio.Event()

        try:
            await self.send(b"\x00", is_last=True)
        except Exception:
            logger.exception("Failed to send final flag")

        try:
            await asyncio.wait_for(self._final_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("Timed out waiting for final transcription result")
        finally:
            await self.disconnect()
