#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Hamsa Speech-to-Text service implementation.

This module implements speech-to-text transcription using the Hamsa API.
Hamsa supports Arabic and English languages via HTTP POST requests.
"""

import asyncio
import base64
import json
from typing import AsyncGenerator, Optional

import aiohttp
from loguru import logger
from pydantic import BaseModel, Field
from typing_extensions import override

from pipecat.frames.frames import (
    ErrorFrame,
    Frame,
    TranscriptionFrame,
)
from pipecat.services.stt_service import SegmentedSTTService
from pipecat.transcriptions.language import Language
from pipecat.utils.time import time_now_iso8601
from pipecat.utils.tracing.service_decorators import traced_stt


def language_to_hamsa_language(language: Language) -> Optional[str]:
    """Convert a Language enum to Hamsa's language code format.

    Args:
        language: The Language enum value to convert

    Returns:
        The Hamsa language code string or None if not supported
    """
    # Hamsa supports Arabic and English
    language_map = {
        # Arabic
        Language.AR: "ar",
        Language.AR_AE: "ar",
        Language.AR_BH: "ar",
        Language.AR_DZ: "ar",
        Language.AR_EG: "ar",
        Language.AR_IQ: "ar",
        Language.AR_JO: "ar",
        Language.AR_KW: "ar",
        Language.AR_LB: "ar",
        Language.AR_LY: "ar",
        Language.AR_MA: "ar",
        Language.AR_OM: "ar",
        Language.AR_QA: "ar",
        Language.AR_SA: "ar",
        Language.AR_SY: "ar",
        Language.AR_TN: "ar",
        Language.AR_YE: "ar",
        # English
        Language.EN: "en",
        Language.EN_AU: "en",
        Language.EN_CA: "en",
        Language.EN_GB: "en",
        Language.EN_HK: "en",
        Language.EN_IE: "en",
        Language.EN_IN: "en",
        Language.EN_KE: "en",
        Language.EN_NG: "en",
        Language.EN_NZ: "en",
        Language.EN_PH: "en",
        Language.EN_SG: "en",
        Language.EN_TZ: "en",
        Language.EN_US: "en",
        Language.EN_ZA: "en",
    }
    return language_map.get(language)


class HamsaSTTService(SegmentedSTTService):
    """Hamsa Speech-to-Text service implementation.

    This service uses the Hamsa API for speech-to-text transcription.
    It inherits from SegmentedSTTService to handle audio buffering and
    processes complete audio segments when the user stops speaking.

    Features:
    - Supports Arabic and English languages
    - Uses HTTP POST requests (not streaming)
    - Configurable End of Speech (EOS) detection
    - Base64 audio encoding

    Args:
        api_key: Hamsa API key for authentication
        language: Language for transcription (defaults to Arabic "ar")
        eos_threshold: End of speech threshold (0.0-1.0, default 0.3)
        base_url: Hamsa API base URL
        aiohttp_session: Optional aiohttp session for connection pooling
        **kwargs: Additional arguments passed to SegmentedSTTService
    """

    class InputParams(BaseModel):
        language: str = Field(default="ar", description="Language code ('ar' or 'en')")
        eos_threshold: float = Field(default=0.3, description="End of speech threshold")

    def __init__(
        self,
        *,
        api_key: str,
        language: Language = Language.AR,
        eos_threshold: float = 0.3,
        base_url: str = "https://api.tryhamsa.com",
        aiohttp_session: Optional[aiohttp.ClientSession] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._language = language_to_hamsa_language(language) or "ar"
        self._eos_threshold = eos_threshold
        self._aiohttp_session = aiohttp_session
        self._endpoint = f"{self._base_url}/v1/realtime/stt"

        # Store current settings
        self._settings = {
            "language": self._language,
            "eos_threshold": self._eos_threshold,
        }

    async def set_language(self, language: Language):
        """Set the language for speech recognition.

        Args:
            language: The language to use for speech recognition
        """
        hamsa_language = language_to_hamsa_language(language)
        if hamsa_language:
            self._language = hamsa_language
            self._settings["language"] = hamsa_language
            logger.info(f"Updated Hamsa STT language to: {hamsa_language}")
        else:
            logger.warning(f"Language {language} not supported by Hamsa STT")

    @traced_stt
    @override
    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        """Run speech-to-text transcription on the provided audio.

        Args:
            audio: Raw audio bytes (WAV format) to transcribe

        Yields:
            Frame: TranscriptionFrame with transcription results or ErrorFrame on failure
        """
        try:
            # Convert audio bytes to base64
            audio_b64 = base64.b64encode(audio).decode("utf-8")

            # Prepare request payload
            payload = {
                "audioBase64": audio_b64,
                "language": self._language,
                "eos_threshold": self._eos_threshold,
            }

            headers = {
                "Authorization": f"Token {self._api_key}",
                "Content-Type": "application/json",
            }

            # Use provided session or create a new one
            session = self._aiohttp_session
            should_close_session = False

            if not session:
                session = aiohttp.ClientSession()
                should_close_session = True

            try:
                # Make the HTTP POST request
                async with session.post(
                    self._endpoint,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        result = await response.json()

                        # Extract transcribed text from response
                        transcription = result.get("text", "").strip()

                        if transcription:
                            logger.debug(f"Hamsa STT transcription: {transcription}")
                            yield TranscriptionFrame(
                                text=transcription,
                                user_id="user",
                                timestamp=time_now_iso8601(),
                            )
                        else:
                            logger.debug("Hamsa STT returned empty transcription")

                    elif response.status == 401:
                        error_msg = "Hamsa STT authentication failed - check API key"
                        logger.error(error_msg)
                        yield ErrorFrame(error=error_msg)

                    elif response.status == 400:
                        error_text = await response.text()
                        error_msg = f"Hamsa STT bad request: {error_text}"
                        logger.error(error_msg)
                        yield ErrorFrame(error=error_msg)

                    else:
                        error_text = await response.text()
                        error_msg = f"Hamsa STT request failed: {response.status} - {error_text}"
                        logger.error(error_msg)
                        yield ErrorFrame(error=error_msg)

            finally:
                if should_close_session and session:
                    await session.close()

        except asyncio.TimeoutError:
            error_msg = "Hamsa STT request timed out"
            logger.error(error_msg)
            yield ErrorFrame(error=error_msg)

        except aiohttp.ClientError as e:
            error_msg = f"Hamsa STT client error: {str(e)}"
            logger.error(error_msg)
            yield ErrorFrame(error=error_msg)

        except Exception as e:
            error_msg = f"Hamsa STT unexpected error: {str(e)}"
            logger.error(error_msg)
            yield ErrorFrame(error=error_msg)
