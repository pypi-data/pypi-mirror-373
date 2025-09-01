# Copyright 2023 Irontec, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import asyncio
import json
import os
import time
import logging
import weakref
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import aiohttp
from aiohttp import ClientWSTimeout

from livekit import rtc
from livekit.agents import (
    DEFAULT_API_CONNECT_OPTIONS,
    APIConnectOptions,
    APIStatusError,
    stt,
    utils,
)
from livekit.agents.types import (
    NOT_GIVEN,
    NotGivenOr,
)
from livekit.agents.utils import AudioBuffer, is_given

SAMPLE_RATE = 8000
NUM_CHANNELS = 1

from .models import STTModels

logger = logging.getLogger(__name__)

@dataclass
class _STTOptions:
    api_key: str
    base_url: str
    model: STTModels | str
    language: str


class STT(stt.STT):
    def __init__(
        self,
        *,
        base_url: str = "wss://realtime-irontec.trebesrv.com",
        api_key: NotGivenOr[str] = NOT_GIVEN,
        language: str = "es",
        model: STTModels | str = "es_eu-Telephonic",
    ):
        """
        Create a new instance of Trebe STT.

        Args:
            base_url: Custom base URL for the API. Optional.
            api_key: API key for authentication. Required.
            language: The language to transcribe in. Defaults to "es".
            model: The Trebe model to use for transcription.
        """

        super().__init__(
            capabilities=stt.STTCapabilities(streaming=True, interim_results=False)
        )

        trebe_api_key = api_key if is_given(api_key) else os.environ.get("TREBE_API_KEY")
        if not trebe_api_key:
            raise ValueError(
                "Trebe API key is required, either as argument or set TREBE_API_KEY environmental variable"
            )

        self._opts = _STTOptions(
            api_key=trebe_api_key,
            base_url=base_url,
            language=language,
            model=model,
        )

        self._streams = weakref.WeakSet[SpeechStream]()
        self._session: aiohttp.ClientSession | None = None
        self._pool = utils.ConnectionPool[aiohttp.ClientWebSocketResponse](
            connect_cb=self._connect_ws,
            close_cb=self._close_ws,
        )

    def stream(
        self,
        *,
        language: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> SpeechStream:
        if is_given(language):
            self._opts.language = language
        stream = SpeechStream(
            stt=self,
            pool=self._pool,
            conn_options=conn_options,
        )
        self._streams.add(stream)
        return stream

    def update_options(
        self,
        *,
        model: NotGivenOr[STTModels | str] = NOT_GIVEN,
        language: NotGivenOr[str] = NOT_GIVEN,
    ) -> None:
        """
        Update the options for the speech stream. Most options are updated at the
        connection level. SpeechStreams will be recreated when options are updated.

        Args:
            language: The language to transcribe in.
            model: The model to use for transcription.
        """  # noqa: E501
        if is_given(model):
            self._opts.model = model
        if is_given(language):
            self._opts.language = language

        for stream in self._streams:
            if is_given(language):
                stream.update_options(language=language)

    async def _connect_ws(self, timeout: float) -> aiohttp.ClientWebSocketResponse:
        auth_message: dict[str, Any] = {
            "message_type": "authorization",
            "payload": {
                "key": self._opts.api_key,
            },
        }

        query_params: dict[str, str] = {
            "model": self._opts.model,
        }
        url = f"{str(self._opts.base_url).rstrip('/')}/?{urlencode(query_params)}"
        if url.startswith("http"):
            url = url.replace("http", "ws", 1)

        session = self._ensure_session()
        ws = await asyncio.wait_for(
            session.ws_connect(url),
            timeout,
        )
        await ws.send_json(auth_message)
        logger.info("Trebe Realtime STT authentication sent.")
        # Wait for the welcome message
        response = await ws.receive()
        if response.type != aiohttp.WSMsgType.TEXT:
            raise APIStatusError(
                message="Trebe Realtime STT connection failed"
            )
        welcome_message = json.loads(response.data)
        if welcome_message.get("message_type") != "session_welcome":
            raise APIStatusError(
                message="Trebe Realtime STT connection failed"
            )
        logger.info("Trebe Realtime STT welcome received: %s", welcome_message)

        config_message: dict[str, Any] = {
            "message_type": "configuration",
            "payload": {
                "audio_format": "audio/l16;rate=8000",
                "recv_transcription": True,
                "recv_translation": False,
                "transcription_interim_results": True,
            },
        }
        await ws.send_json(config_message)
        logger.info("Trebe Realtime STT configuration done.")

        return ws

    async def _close_ws(self, ws: aiohttp.ClientWebSocketResponse):
        await ws.close()

    def _ensure_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = utils.http_context.http_session()

        return self._session

    async def _recognize_impl(self, buffer, *, language=NOT_GIVEN, conn_options=None):
        raise NotImplementedError("Este STT solo soporta modo streaming.")


class SpeechStream(stt.SpeechStream):
    def __init__(
        self,
        *,
        stt: STT,
        conn_options: APIConnectOptions,
        pool: utils.ConnectionPool[aiohttp.ClientWebSocketResponse],
    ) -> None:
        super().__init__(stt=stt, conn_options=conn_options, sample_rate=SAMPLE_RATE)

        self._pool = pool
        self._language = stt._opts.language
        self._request_id = ""
        self._reconnect_event = asyncio.Event()

    def update_options(
        self,
        *,
        language: str,
    ):
        self._language = language
        self._pool.invalidate()
        self._reconnect_event.set()

    @utils.log_exceptions(logger=logger)
    async def _run(self) -> None:
        closing_ws = False

        @utils.log_exceptions(logger=logger)
        async def send_task(ws: aiohttp.ClientWebSocketResponse):
            nonlocal closing_ws

            # forward audio to OAI in chunks of 50ms
            audio_bstream = utils.audio.AudioByteStream(
                sample_rate=SAMPLE_RATE,
                num_channels=NUM_CHANNELS,
                samples_per_channel=SAMPLE_RATE // 20,
            )

            async for data in self._input_ch:
                frames: list[rtc.AudioFrame] = []
                if isinstance(data, rtc.AudioFrame):
                    audio_bytes = data.data.tobytes()
                    frames.extend(audio_bstream.write(audio_bytes))
                elif isinstance(data, self._FlushSentinel):
                    frames.extend(audio_bstream.flush())

                for frame in frames:
                    await ws.send_bytes(frame.data.tobytes())

            closing_ws = True

        @utils.log_exceptions(logger=logger)
        async def recv_task(ws: aiohttp.ClientWebSocketResponse):
            nonlocal closing_ws
            current_text = ""
            last_interim_at: float = 0
            connected_at = time.time()
            while True:
                logger.info("Trebe waiting for message")
                msg = await ws.receive()
                logger.info("Trebe message received: %s", msg.data)
                if msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSING,
                ):
                    if closing_ws:  # close is expected, see SpeechStream.aclose
                        return

                    # this will trigger a reconnection, see the _run loop
                    raise APIStatusError(
                        message="Trebe Realtime STT connection closed unexpectedly"
                    )

                if msg.type != aiohttp.WSMsgType.TEXT:
                    logger.warning("unexpected Trebe message type %s", msg.type)
                    continue

                try:
                    data = json.loads(msg.data)
                    msg_type = data.get("message_type")
                    if msg_type == "result":
                        payload = data.get("payload")
                        if payload.get("type") == "transcription":
                            is_final = payload.get("is_final", False)
                            if is_final:
                                transcript = payload.get("stable_text")
                                if transcript:
                                    logger.info("Trebe message received: %s", msg.data)
                                    self._event_ch.send_nowait(
                                        stt.SpeechEvent(
                                            type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                                            alternatives=[
                                                stt.SpeechData(
                                                    text=transcript,
                                                    language=self._language,
                                                )
                                            ],
                                        )
                                    )
                except Exception:
                    logger.exception("failed to process Trebe message")

        while True:
            async with self._pool.connection(timeout=10) as ws:
                tasks = [
                    asyncio.create_task(send_task(ws)),
                    asyncio.create_task(recv_task(ws)),
                ]
                tasks_group = asyncio.gather(*tasks)
                wait_reconnect_task = asyncio.create_task(self._reconnect_event.wait())
                try:
                    done, _ = await asyncio.wait(
                        [tasks_group, wait_reconnect_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )  # type: ignore

                    # propagate exceptions from completed tasks
                    for task in done:
                        if task != wait_reconnect_task:
                            task.result()

                    if wait_reconnect_task not in done:
                        break

                    self._reconnect_event.clear()
                finally:
                    await utils.aio.gracefully_cancel(*tasks, wait_reconnect_task)
                    await tasks_group
