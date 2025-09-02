from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Union

import aiohttp
import numpy as np
from loguru import logger

from bithuman.audio import resample

try:
    from bithuman_local_voice import BithumanLocalSTT as BithumanSTTImpl
except ImportError:
    BithumanSTTImpl = None

try:
    from livekit.agents import utils
    from livekit.agents.stt import (
        STT,
        SpeechData,
        SpeechEvent,
        SpeechEventType,
        STTCapabilities,
    )
    from livekit.agents.types import NOT_GIVEN, APIConnectOptions, NotGivenOr
except ImportError:
    raise ImportError(
        "livekit is required, please install it with `pip install livekit-agents`"
    )


@dataclass
class _STTOptions:
    locale: str = "en-US"
    on_device: bool = True
    punctuation: bool = True
    debug: bool = False


class BithumanSTTError(Exception):
    pass


class BithumanLocalSTT(STT):
    _SAMPLE_RATE = 16000

    def __init__(
        self,
        *,
        locale="en-US",
        server_url=None,
        on_device=True,
        punctuation=True,
        debug=False,
    ):
        capabilities = STTCapabilities(streaming=False, interim_results=False)
        super().__init__(capabilities=capabilities)
        self._opts = _STTOptions(
            locale=locale, on_device=on_device, punctuation=punctuation, debug=debug
        )
        self._server_url: str | None = None
        self._session: aiohttp.ClientSession | None = None
        self._stt_impl = None

        if server_url:
            self._server_url = server_url
            self._session = aiohttp.ClientSession()
        else:
            if BithumanSTTImpl is None:
                raise ImportError(
                    "bithuman_local_voice is required if server_url is not provided, "
                    "please install it with `pip install bithuman_local_voice`"
                )
            self._stt_impl = BithumanSTTImpl(
                locale=locale,
                on_device=on_device,
                punctuation=punctuation,
                debug=debug,
            )

    async def _recognize_impl(
        self,
        buffer: utils.audio.AudioBuffer,
        *,
        language: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions,
    ):
        if utils.is_given(language) and language != self._opts.locale:
            try:
                await self._set_locale(language)
            except Exception as e:
                logger.error(f"Failed to set locale: {e}")

        frame = utils.audio.combine_frames(buffer)
        audio_data = np.frombuffer(frame.data, dtype=np.int16)
        if frame.sample_rate != self._SAMPLE_RATE:
            audio_data = resample(audio_data, frame.sample_rate, self._SAMPLE_RATE)

        try:
            result = await self._recognize_audio(
                audio_data, sample_rate=self._SAMPLE_RATE
            )
        except Exception as e:
            logger.warning(f"Failed to recognize audio with error: {e}")
            result = {"text": "", "confidence": 0.0}

        return SpeechEvent(
            type=SpeechEventType.FINAL_TRANSCRIPT,
            request_id="",
            alternatives=[
                SpeechData(
                    language=self._opts.locale,
                    text=result["text"],
                    confidence=result["confidence"],
                )
            ],
        )

    async def _recognize_audio(
        self, audio_data: Union[bytes, np.ndarray], sample_rate: int = 16000
    ) -> Dict:
        """Recognize speech in the provided audio data.

        Args:
            audio_data: Audio data as bytes or numpy array
            sample_rate: Sample rate of the audio data

        Returns:
            Dict containing transcription and confidence score
        """
        if self._stt_impl is not None:
            return await self._stt_impl.recognize(audio_data, sample_rate)

        # Convert numpy array to bytes if needed
        if isinstance(audio_data, np.ndarray):
            # Convert to float in [-1, 1] range if not already
            if audio_data.dtype != np.int16:
                audio_data = (audio_data * 32767).astype(np.int16)
            audio_bytes = audio_data.tobytes()
        else:
            audio_bytes = audio_data

        async with self._session.post(
            f"{self._server_url}/transcribe",
            data=audio_bytes,
            headers={"Content-Type": "application/octet-stream"},
            timeout=5,
        ) as response:
            response.raise_for_status()
            result: dict = await response.json()
            return {
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
            }

    async def _set_locale(self, locale: str):
        """Set the recognition locale.

        Args:
            locale: Locale identifier (e.g. en-US, fr-FR)
        """
        if self._stt_impl is not None:
            await self._stt_impl.set_locale(locale)
            self._opts.locale = locale
            return

        assert self._server_url is not None
        async with self._session.post(
            f"{self._server_url}/setLocale",
            json={"locale": locale},
            headers={"Content-Type": "application/json"},
            timeout=5,
        ) as response:
            response.raise_for_status()
            result: dict = await response.json()
            if result.get("success"):
                self._opts.locale = locale
            raise BithumanSTTError(result.get("message", "Unknown error"))

    async def aclose(self):
        if self._stt_impl is not None:
            await self._stt_impl.stop()
        if self._session is not None:
            await self._session.close()
