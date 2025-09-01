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

# Constants
API_BASE_URL = "https://localhost:5001/tts"
NUM_CHANNELS = 1
SAMPLE_RATE = 22050
DEFAULT_LANGUAGE = "en"


@dataclass
class _TTSOptions:
    """Internal options for Piper AI TTS"""

    language: str
    base_url: str


class TTS(tts.TTS):
    """Piper AI Text-to-Speech implementation"""

    def __init__(
        self,
        *,
        language: str = DEFAULT_LANGUAGE,
        base_url: NotGivenOr[str] = NOT_GIVEN,
    ) -> None:
        """
        Create a new instance of Piper AI TTS.
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

        self._opts = _TTSOptions(
            language=language,
            base_url=base_url if is_given(base_url) else API_BASE_URL,
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
        Synthesize text to speech using Piper AI.
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
    """Piper AI TTS chunked stream implementation"""

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

        # Create the payload for Piper AI TTS API
        payload = {
            "text": self._input_text,
            "language": self._opts.language,
        }

        try:
            logger = logging.getLogger(__name__)
            logger.info(
                f"Starting TTS synthesis for request_id={request_id}, text='{self._input_text[:50]}...'")

            async with self._session.post(
                f"{self._opts.base_url}/tts",
                headers={
                    "Content-Type": "application/json",
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
