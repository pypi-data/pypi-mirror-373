# Copyright 2025 Irontec S.L.
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
import weakref
import os
from dataclasses import dataclass

import aiohttp

from livekit.agents import (
    APIConnectionError,
    APIConnectOptions,
    APIStatusError,
    APITimeoutError,
    tts,
    utils,
)
from livekit.agents.types import (
    DEFAULT_API_CONNECT_OPTIONS,
    NOT_GIVEN,
    NotGivenOr,
)
from livekit.agents.utils import is_given
import logging
from .models import TTSModels

# Constants
API_BASE_URL = "https://tts.trebesrv.com"
NUM_CHANNELS = 1
SAMPLE_RATE = 22050


@dataclass
class _TTSOptions:
    """Internal options for Trebe AI TTS"""
    api_key: str
    base_url: str
    language: NotGivenOr[str]
    model: TTSModels | str
    speed: float

class TTS(tts.TTS):
    """Trebe AI Text-to-Speech implementation"""

    def __init__(
        self,
        *,
        language: str = "es",
        base_url: NotGivenOr[str] = NOT_GIVEN,
        api_key: NotGivenOr[str] = NOT_GIVEN,
        model: TTSModels | str = "David",
        speed: float = 1.0,
    ) -> None:
        """
        Create a new instance of Trebe AI TTS.
        Args:
            language (str): Language ID. Defaults to en.
            base_url (NotGivenOr[str]): Custom base URL for the API. Optional.
        """
        super().__init__(
            capabilities=tts.TTSCapabilities(
                streaming=False,
            ),
            sample_rate=SAMPLE_RATE,
            num_channels=NUM_CHANNELS,
        )

        trebe_api_key = api_key if is_given(api_key) else os.environ.get("TREBE_API_KEY")
        if not trebe_api_key:
            raise ValueError(
                "Trebe API key is required, either as argument or set TREBE_API_KEY environmental variable"
            )

        self._opts = _TTSOptions(
            api_key=trebe_api_key,
            language=language,
            base_url=base_url if is_given(base_url) else API_BASE_URL,
            model=model,
            speed=speed,
        )
        self._streams = weakref.WeakSet[ChunkedStream]()
        self._session = None

    def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure we have a valid HTTP session"""
        if self._session is not None:
            return self._session

        # Only try to get a session from the context if we don't have one
        try:
            self._session = utils.http_context.http_session()
        except RuntimeError:
            # If we're outside a job context, create a new session
            self._session = aiohttp.ClientSession()

        return self._session

    def update_options(
        self, *, language: NotGivenOr[str] = NOT_GIVEN
    ) -> None:
        """
        Update the TTS options.

        Args:
            language (str, optional): Language to use for synthesis.
        """
        if is_given(language):
            self._opts.language = language

    def synthesize(
        self,
        text: str,
        *,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> ChunkedStream:
        """
        Synthesize text to speech using Trebe AI.
        Args:
            text (str): Text to synthesize
            conn_options (APIConnectOptions): Connection options
        Returns:
            ChunkedStream: Stream of synthesized audio
        """
        stream = ChunkedStream(
            tts=self,
            input_text=text,
            conn_options=conn_options,
            opts=self._opts,
            session=self._ensure_session(),
        )
        self._streams.add(stream)
        return stream

    async def aclose(self) -> None:
        """Close all streams and resources"""
        for stream in list(self._streams):
            await stream.aclose()
        self._streams.clear()
        await super().aclose()


class ChunkedStream(tts.ChunkedStream):
    """Trebe AI TTS chunked stream implementation"""

    def __init__(
        self,
        *,
        tts: TTS,
        input_text: str,
        opts: _TTSOptions,
        conn_options: APIConnectOptions,
        session: aiohttp.ClientSession,
    ) -> None:
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._opts = opts
        self._session = session

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        """Run the TTS synthesis process"""
        request_id = utils.shortuuid()
        output_emitter.initialize(
            request_id=request_id,
            sample_rate=SAMPLE_RATE,
            num_channels=1,
            mime_type="audio/wav",
        )

        # Create the payload for Trebe AI TTS API
        payload = {
            "text": self._input_text,
            "languageCode": self._opts.language,
            "modelName": self._opts.model,
            "speed": self._opts.speed,
        }

        try:
            logger = logging.getLogger(__name__)
            logger.info(f"Starting TTS synthesis text='{self._input_text[:50]}...'")

            async with self._session.post(
                f"{self._opts.base_url}/tts",
                headers={
                    "Content-Type": "application/json",
                    "apikey": self._opts.api_key,
                },
                json=payload,
                timeout=aiohttp.ClientTimeout(
                    total=30,
                    sock_connect=self._conn_options.timeout,
                ),
            ) as audio_resp:
                audio_resp.raise_for_status()

                # Read the audio data
                audio_data = await audio_resp.read()

                if audio_data:
                    output_emitter.push(audio_data)

        except asyncio.TimeoutError as e:
            raise APITimeoutError() from e
        except aiohttp.ClientResponseError as e:
            raise APIStatusError(
                message=e.message,
                status_code=e.status,
                request_id=request_id,
                body=None,
            ) from e
        except Exception as e:
            raise APIConnectionError() from e