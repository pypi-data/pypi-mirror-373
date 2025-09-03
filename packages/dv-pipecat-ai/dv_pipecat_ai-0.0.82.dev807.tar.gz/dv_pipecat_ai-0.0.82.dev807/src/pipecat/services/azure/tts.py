#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Azure Cognitive Services Text-to-Speech service implementations."""

import asyncio
from typing import AsyncGenerator, Optional

from loguru import logger
from pydantic import BaseModel

from pipecat.frames.frames import (
    ErrorFrame,
    Frame,
    StartFrame,
    TTSAudioRawFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
)
from pipecat.services.azure.common import language_to_azure_language
from pipecat.services.tts_service import TTSService
from pipecat.transcriptions.language import Language
from pipecat.utils.tracing.service_decorators import traced_tts
from pipecat.utils.utils import detect_language_from_script

try:
    from azure.cognitiveservices.speech import (
        CancellationReason,
        ResultReason,
        ServicePropertyChannel,
        SpeechConfig,
        SpeechSynthesisOutputFormat,
        SpeechSynthesizer,
    )
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    logger.error("In order to use Azure, you need to `pip install pipecat-ai[azure]`.")
    raise Exception(f"Missing module: {e}")


def sample_rate_to_output_format(sample_rate: int) -> SpeechSynthesisOutputFormat:
    """Convert sample rate to Azure speech synthesis output format.

    Args:
        sample_rate: Sample rate in Hz.

    Returns:
        Corresponding Azure SpeechSynthesisOutputFormat enum value.
        Defaults to Raw24Khz16BitMonoPcm if sample rate not found.
    """
    sample_rate_map = {
        8000: SpeechSynthesisOutputFormat.Raw8Khz16BitMonoPcm,
        16000: SpeechSynthesisOutputFormat.Raw16Khz16BitMonoPcm,
        22050: SpeechSynthesisOutputFormat.Raw22050Hz16BitMonoPcm,
        24000: SpeechSynthesisOutputFormat.Raw24Khz16BitMonoPcm,
        44100: SpeechSynthesisOutputFormat.Raw44100Hz16BitMonoPcm,
        48000: SpeechSynthesisOutputFormat.Raw48Khz16BitMonoPcm,
    }
    return sample_rate_map.get(sample_rate, SpeechSynthesisOutputFormat.Raw24Khz16BitMonoPcm)


class AzureBaseTTSService(TTSService):
    """Base class for Azure Cognitive Services text-to-speech implementations.

    Provides common functionality for Azure TTS services including SSML
    construction, voice configuration, and parameter management.
    """

    # Define SSML escape mappings based on SSML reserved characters
    # See - https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-structure
    SSML_ESCAPE_CHARS = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&apos;",
    }

    class InputParams(BaseModel):
        """Input parameters for Azure TTS voice configuration.

        Parameters:
            emphasis: Emphasis level for speech ("strong", "moderate", "reduced").
            language: Language for synthesis. Defaults to English (US).
            pitch: Voice pitch adjustment (e.g., "+10%", "-5Hz", "high").
            rate: Speech rate multiplier. Defaults to "1.05".
            role: Voice role for expression (e.g., "YoungAdultFemale").
            style: Speaking style (e.g., "cheerful", "sad", "excited").
            style_degree: Intensity of the speaking style (0.01 to 2.0).
            volume: Volume level (e.g., "+20%", "loud", "x-soft").
        """

        emphasis: Optional[str] = None
        language: Optional[Language] = Language.EN_US
        pitch: Optional[str] = None
        rate: Optional[str] = "1.05"
        role: Optional[str] = None
        style: Optional[str] = None
        style_degree: Optional[str] = None
        volume: Optional[str] = None

    def __init__(
        self,
        *,
        api_key: str,
        region: str,
        voice: str = "en-US-SaraNeural",
        language: Optional[Language] = None,  # Primary language setting
        additional_languages: list[str] | None = None,  # e.g., ["te-IN"]
        additional_voices: dict[str, str] | None = None,  # e.g., {"te-IN": "te-IN-MohanNeural"}
        sample_rate: Optional[int] = None,
        params: Optional[InputParams] = None,
        **kwargs,
    ):
        """Initialize the Azure TTS service with configuration parameters.

        Args:
            api_key: Azure Cognitive Services subscription key.
            region: Azure region identifier (e.g., "eastus", "westus2").
            voice: Voice name to use for synthesis. Defaults to "en-US-SaraNeural".
            sample_rate: Audio sample rate in Hz. If None, uses service default.
            params: Voice and synthesis parameters configuration.
            **kwargs: Additional arguments passed to parent TTSService.
        """
        super().__init__(sample_rate=sample_rate, **kwargs)

        params = params or AzureBaseTTSService.InputParams()

        # 1. Set Primary Language/Voice (use direct params, ignore params.language here)
        primary_lang_code = self.language_to_service_language(language or params.language)
        if not primary_lang_code:
            logger.warning(f"Could not map primary language {language}, defaulting to en-US.")
            primary_lang_code = "en-US"
        self._primary_language = primary_lang_code
        self._primary_voice_id = voice
        self.logger.debug(
            f"Primary TTS language set to: {self._primary_language}, voice: {self._primary_voice_id}"
        )

        # 2. Store SSML settings from InputParams (excluding language)

        self._settings = {
            "emphasis": params.emphasis,
            "language": primary_lang_code,
            "pitch": params.pitch,
            "rate": params.rate,
            "role": params.role,
            "style": params.style,
            "style_degree": params.style_degree,
            "volume": params.volume,
        }

        self._api_key = api_key
        self._region = region
        self._speech_synthesizer = None

        # 3. Build the additional language map { "2_letter_code": (full_code, voice_name) }
        self._additional_lang_map = {}
        if additional_languages and additional_voices:
            additional_languages.append(primary_lang_code)
            additional_voices[primary_lang_code] = voice
            for full_lang_code in additional_languages:
                # Ensure it's a valid-looking code before splitting
                if isinstance(full_lang_code, str) and "-" in full_lang_code:
                    two_letter_code = full_lang_code.split("-")[0].lower()
                    if full_lang_code in additional_voices:
                        voice_name = additional_voices[full_lang_code]
                        self._additional_lang_map[two_letter_code] = (full_lang_code, voice_name)
                        logger.debug(
                            f"Mapping '{two_letter_code}' to ({full_lang_code}, {voice_name})"
                        )
                    else:
                        logger.warning(
                            f"No voice provided in additional_voices for language '{full_lang_code}', skipping."
                        )
                else:
                    logger.warning(
                        f"Invalid format in additional_languages: '{full_lang_code}', skipping."
                    )
        elif additional_languages or additional_voices:
            logger.warning(
                "Both 'additional_languages' (e.g., ['te-IN']) and 'additional_voices' (e.g., {{'te-IN': 'voice-name'}}) must be provided for multilingual TTS."
            )

        logger.debug(f"Final additional language map: {self._additional_lang_map}")

    def can_generate_metrics(self) -> bool:
        """Check if this service can generate processing metrics.

        Returns:
            True, as Azure TTS service supports metrics generation.
        """
        return True

    def language_to_service_language(self, language: Language) -> Optional[str]:
        """Convert a Language enum to Azure language format.

        Args:
            language: The language to convert.

        Returns:
            The Azure-specific language code, or None if not supported.
        """
        return language_to_azure_language(language)

    def _construct_ssml(self, text: str) -> str:
        # 1. Detect language based on script heuristic
        detected_code = detect_language_from_script(text)  # Returns "te" or "en"

        # 2. Determine target language and voice
        target_language = self._primary_language
        target_voice = self._primary_voice_id

        # Check if the detected 2-letter code has a mapping configured
        if detected_code in self._additional_lang_map:
            # Retrieve the full language code and voice name from the map
            mapped_language, mapped_voice = self._additional_lang_map[detected_code]
            target_language = mapped_language
            target_voice = mapped_voice
            logger.debug(
                f"Detected language code '{detected_code}', using mapped voice: {target_voice} ({target_language})"
            )

        # 3. Construct SSML with the selected language and voice

        # Escape special characters
        escaped_text = self._escape_text(text)

        ssml = (
            f"<speak version='1.0' xml:lang='{target_language}' "
            "xmlns='http://www.w3.org/2001/10/synthesis' "
            "xmlns:mstts='http://www.w3.org/2001/mstts'>"
            f"<voice name='{target_voice}'>"
            "<mstts:silence type='Sentenceboundary' value='20ms' />"
        )

        if self._settings["style"]:
            ssml += f"<mstts:express-as style='{self._settings['style']}'"
            if self._settings["style_degree"]:
                ssml += f" styledegree='{self._settings['style_degree']}'"
            if self._settings["role"]:
                ssml += f" role='{self._settings['role']}'"
            ssml += ">"

        prosody_attrs = []
        if self._settings["rate"]:
            prosody_attrs.append(f"rate='{self._settings['rate']}'")
        if self._settings["pitch"]:
            prosody_attrs.append(f"pitch='{self._settings['pitch']}'")
        if self._settings["volume"]:
            prosody_attrs.append(f"volume='{self._settings['volume']}'")

        ssml += f"<prosody {' '.join(prosody_attrs)}>"

        if self._settings["emphasis"]:
            ssml += f"<emphasis level='{self._settings['emphasis']}'>"

        if "Multilingual" in target_voice:
            ssml += f"<lang xml:lang='{target_language}'>"
            ssml += escaped_text
            ssml += "</lang>"
        else:
            ssml += escaped_text

        if self._settings["emphasis"]:
            ssml += "</emphasis>"

        ssml += "</prosody>"

        if self._settings["style"]:
            ssml += "</mstts:express-as>"

        ssml += "</voice></speak>"

        return ssml

    def _escape_text(self, text: str) -> str:
        """Escapes XML/SSML reserved characters according to Microsoft documentation.

        This method escapes the following characters:
        - & becomes &amp;
        - < becomes &lt;
        - > becomes &gt;
        - " becomes &quot;
        - ' becomes &apos;

        Args:
            text: The text to escape.

        Returns:
            The escaped text.
        """
        escaped_text = text
        for char, escape_code in AzureBaseTTSService.SSML_ESCAPE_CHARS.items():
            escaped_text = escaped_text.replace(char, escape_code)
        return escaped_text


class AzureTTSService(AzureBaseTTSService):
    """Azure Cognitive Services streaming TTS service.

    Provides real-time text-to-speech synthesis using Azure's WebSocket-based
    streaming API. Audio chunks are streamed as they become available for
    lower latency playback.
    """

    def __init__(self, **kwargs):
        """Initialize the Azure streaming TTS service.

        Args:
            **kwargs: All arguments passed to AzureBaseTTSService parent class.
        """
        super().__init__(**kwargs)
        self._speech_config = None
        self._speech_synthesizer = None
        self._audio_queue = asyncio.Queue()
        self._clear_audio = False

    async def start(self, frame: StartFrame):
        """Start the Azure TTS service and initialize speech synthesizer.

        Args:
            frame: Start frame containing initialization parameters.
        """
        await super().start(frame)

        if self._speech_config:
            return

        # Now self.sample_rate is properly initialized
        self._speech_config = SpeechConfig(
            subscription=self._api_key,
            region=self._region,
            speech_recognition_language=self._primary_language,
        )
        self._speech_config.set_speech_synthesis_output_format(
            sample_rate_to_output_format(self.sample_rate)
        )
        self._speech_config.set_service_property(
            "synthesizer.synthesis.connection.synthesisConnectionImpl",
            "websocket",
            ServicePropertyChannel.UriQueryParameter,
        )

        self._speech_synthesizer = SpeechSynthesizer(
            speech_config=self._speech_config, audio_config=None
        )

        # Set up event handlers
        self._speech_synthesizer.synthesizing.connect(self._handle_synthesizing)
        self._speech_synthesizer.synthesis_completed.connect(self._handle_completed)
        self._speech_synthesizer.synthesis_canceled.connect(self._handle_canceled)

    def _handle_synthesizing(self, evt):
        """Handle audio chunks as they arriv."""
        if evt.result and evt.result.audio_data:
            self._audio_queue.put_nowait(evt.result.audio_data)

    def _handle_completed(self, evt):
        """Handle synthesis completion."""
        self._audio_queue.put_nowait(None)  # Signal completion

    def _handle_canceled(self, evt):
        """Handle synthesis cancellation"""
        self.logger.error(f"Speech synthesis canceled: {evt.result.cancellation_details.reason}")
        self._audio_queue.put_nowait(None)

    async def flush_audio(self):
        """Flush any pending audio data."""
        logger.trace(f"{self}: flushing audio")

    @traced_tts
    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        """Generate speech from text using Azure's streaming synthesis.

        Args:
            text: The text to synthesize into speech.

        Yields:
            Frame: Audio frames containing synthesized speech data.
        """
        text = text.lstrip()
        self.logger.debug(f"{self}: Generating TTS [{text}]")

        # Clear the audio queue in case there's still audio in it, causing the next audio response
        # to be cut off by the 'None' element returned at the end of the previous audio synthesis.
        # Empty the audio queue before processing the new text
        while not self._audio_queue.empty():
            self._audio_queue.get_nowait()
            self._audio_queue.task_done()

        try:
            if self._speech_synthesizer is None:
                error_msg = "Speech synthesizer not initialized."
                logger.error(error_msg)
                yield ErrorFrame(error_msg)
                return
            try:
                await self.start_ttfb_metrics()
                yield TTSStartedFrame()
                ssml = self._construct_ssml(text)
                self._speech_synthesizer.speak_ssml_async(ssml)
                await self.start_tts_usage_metrics(text)

                # Stream audio chunks as they arrive
                while True:
                    if self._clear_audio:
                        break
                    chunk = await self._audio_queue.get()
                    if chunk is None:  # End of stream
                        break
                    await self.stop_ttfb_metrics()
                    yield TTSAudioRawFrame(
                        audio=chunk,
                        sample_rate=self.sample_rate,
                        num_channels=1,
                    )
                self.logger.debug(f"{self}: Ending TTS: [{text}]")
                yield TTSStoppedFrame()
            except Exception as e:
                self.logger.error(f"{self} error during synthesis: {e}")
                yield TTSStoppedFrame()
                # Could add reconnection logic here if needed
                return
        except Exception as e:
            logger.error(f"{self} exception: {e}")


class AzureHttpTTSService(AzureBaseTTSService):
    """Azure Cognitive Services HTTP-based TTS service.

    Provides text-to-speech synthesis using Azure's HTTP API for simpler,
    non-streaming synthesis. Suitable for use cases where streaming is not
    required and simpler integration is preferred.
    """

    def __init__(self, **kwargs):
        """Initialize the Azure HTTP TTS service.

        Args:
            **kwargs: All arguments passed to AzureBaseTTSService parent class.
        """
        super().__init__(**kwargs)
        self._speech_config = None
        self._speech_synthesizer = None

    async def start(self, frame: StartFrame):
        """Start the Azure HTTP TTS service and initialize speech synthesizer.

        Args:
            frame: Start frame containing initialization parameters.
        """
        await super().start(frame)

        if self._speech_config:
            return

        self._speech_config = SpeechConfig(
            subscription=self._api_key,
            region=self._region,
        )
        self._speech_config.speech_synthesis_language = self._settings["language"]
        self._speech_config.set_speech_synthesis_output_format(
            sample_rate_to_output_format(self.sample_rate)
        )
        self._speech_synthesizer = SpeechSynthesizer(
            speech_config=self._speech_config, audio_config=None
        )

    @traced_tts
    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        """Generate speech from text using Azure's HTTP synthesis API.

        Args:
            text: The text to synthesize into speech.

        Yields:
            Frame: Audio frames containing the complete synthesized speech.
        """
        logger.debug(f"{self}: Generating TTS [{text}]")

        await self.start_ttfb_metrics()

        ssml = self._construct_ssml(text)

        result = await asyncio.to_thread(self._speech_synthesizer.speak_ssml, ssml)

        if result.reason == ResultReason.SynthesizingAudioCompleted:
            await self.start_tts_usage_metrics(text)
            await self.stop_ttfb_metrics()
            yield TTSStartedFrame()
            # Azure always sends a 44-byte header. Strip it off.
            yield TTSAudioRawFrame(
                audio=result.audio_data[44:],
                sample_rate=self.sample_rate,
                num_channels=1,
            )
            yield TTSStoppedFrame()
        elif result.reason == ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.warning(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == CancellationReason.Error:
                logger.error(f"{self} error: {cancellation_details.error_details}")
