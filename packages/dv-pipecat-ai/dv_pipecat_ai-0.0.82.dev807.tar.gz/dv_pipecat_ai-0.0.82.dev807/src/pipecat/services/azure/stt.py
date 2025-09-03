#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Azure Speech-to-Text service implementation for Pipecat.

This module provides speech-to-text functionality using Azure Cognitive Services
Speech SDK for real-time audio transcription.
"""

import asyncio
from typing import AsyncGenerator, List, Optional  # Add List

from loguru import logger

from pipecat.frames.frames import (
    CancelFrame,
    EndFrame,
    Frame,
    StartFrame,
    TranscriptionFrame,
)
from pipecat.services.azure.common import language_to_azure_language
from pipecat.services.stt_service import STTService
from pipecat.transcriptions.language import Language
from pipecat.utils.time import time_now_iso8601
from pipecat.utils.tracing.service_decorators import traced_stt

try:
    from azure.cognitiveservices.speech import (
        PhraseListGrammar,  # Import PhraseListGrammar here
        PropertyId,
        ResultReason,
        SpeechConfig,
        SpeechRecognizer,
    )
    from azure.cognitiveservices.speech.audio import (
        AudioStreamFormat,
        PushAudioInputStream,
    )
    from azure.cognitiveservices.speech.dialog import AudioConfig
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    logger.error("In order to use Azure, you need to `pip install pipecat-ai[azure]`.")
    raise Exception(f"Missing module: {e}")


class AzureSTTService(STTService):
    """Azure Speech-to-Text service for real-time audio transcription.

    This service uses Azure Cognitive Services Speech SDK to convert speech
    audio into text transcriptions. It supports continuous recognition and
    provides real-time transcription results with timing information.
    """

    def __init__(
        self,
        *,
        api_key: str,
        region: str,
        language: Language = Language.EN_US,
        additional_languages: list[Language] = None,
        sample_rate: Optional[int] = None,
        endpoint_id: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the Azure STT service.

        Args:
            api_key: Azure Cognitive Services subscription key.
            region: Azure region for the Speech service (e.g., 'eastus').
            language: Language for speech recognition. Defaults to English (US).
            sample_rate: Audio sample rate in Hz. If None, uses service default.
            endpoint_id: Custom model endpoint id.
            **kwargs: Additional arguments passed to parent STTService.
        """
        super().__init__(sample_rate=sample_rate, **kwargs)
        self._vocab: Optional[List[str]] = kwargs.pop("vocab", None)  # Get vocab from kwargs

        self._speech_config = SpeechConfig(
            subscription=api_key,
            region=region,
            speech_recognition_language=language_to_azure_language(language),
        )

        # Optimize Azure STT for faster transcripts
        self._speech_config.set_property(PropertyId.Speech_SegmentationSilenceTimeoutMs, "400")
        self._primary_language = language
        self._additional_languages = additional_languages
        if endpoint_id:
            self._speech_config.endpoint_id = endpoint_id

        self._audio_stream = None
        self._speech_recognizer = None
        self._settings = {
            "region": region,
            "language": language_to_azure_language(language),
            "sample_rate": sample_rate,
        }

    def can_generate_metrics(self) -> bool:
        """Check if this service can generate performance metrics.

        Returns:
            True as this service supports metrics generation.
        """
        return True

    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        """Process audio data for speech-to-text conversion.

        Feeds audio data to the Azure speech recognizer for processing.
        Recognition results are handled asynchronously through callbacks.

        Args:
            audio: Raw audio bytes to process.

        Yields:
            None - actual transcription frames are pushed via callbacks.
        """
        await self.start_processing_metrics()
        await self.start_ttfb_metrics()
        if self._audio_stream:
            # Write audio to the Azure PushAudioInputStream for recognition
            self._audio_stream.write(audio)
        yield None

    async def start(self, frame: StartFrame):
        """Start the speech recognition service.

        Initializes the Azure speech recognizer with audio stream configuration
        and begins continuous speech recognition.

        Args:
            frame: Frame indicating the start of processing.
        """
        await super().start(frame)

        if self._audio_stream:
            # Already started, skip re-initialization
            return

        stream_format = AudioStreamFormat(samples_per_second=self.sample_rate, channels=1)
        self._audio_stream = PushAudioInputStream(stream_format)

        audio_config = AudioConfig(stream=self._audio_stream)

        # Set up auto language detection if additional languages specified
        if self._additional_languages:
            from azure.cognitiveservices.speech import AutoDetectSourceLanguageConfig

            azure_primary_lang = language_to_azure_language(self._primary_language)
            all_languages = [azure_primary_lang] if azure_primary_lang else []
            for lang in self._additional_languages:
                azure_lang = language_to_azure_language(lang)
                if azure_lang and azure_lang not in all_languages:
                    all_languages.append(azure_lang)
            self.logger.debug(f"Setting up Azure STT with language detection for: {all_languages}")
            self._auto_detect_source_language_config = AutoDetectSourceLanguageConfig(
                languages=all_languages
            )
            self._speech_config.set_property(
                property_id=PropertyId.SpeechServiceConnection_LanguageIdMode,
                value="Continuous",
            )
            # Create recognizer with auto language detection enabled
            self._speech_recognizer = SpeechRecognizer(
                speech_config=self._speech_config,
                auto_detect_source_language_config=self._auto_detect_source_language_config,
                audio_config=audio_config,
            )
        else:
            # Single language mode
            self.logger.debug(
                f"Setting up Azure STT for primary language: {self._speech_config.speech_recognition_language}"
            )
            self._speech_recognizer = SpeechRecognizer(
                speech_config=self._speech_config, audio_config=audio_config
            )

        # Apply phrase list if vocab is provided
        self._apply_phrase_list(self._speech_recognizer)

        # Attach event handler for recognized speech
        self._speech_recognizer.recognized.connect(self._on_handle_recognized)
        self._speech_recognizer.start_continuous_recognition_async()

    async def stop(self, frame: EndFrame):
        """Stop the speech recognition service.

        Cleanly shuts down the Azure speech recognizer and closes audio streams.

        Args:
            frame: Frame indicating the end of processing.
        """
        await super().stop(frame)

        if self._speech_recognizer:
            # Stop Azure continuous recognition
            self._speech_recognizer.stop_continuous_recognition_async()

        if self._audio_stream:
            # Close the audio stream to free resources
            self._audio_stream.close()

    async def cancel(self, frame: CancelFrame):
        """Cancel the speech recognition service.

        Immediately stops recognition and closes resources.

        Args:
            frame: Frame indicating cancellation.
        """
        await super().cancel(frame)

        if self._speech_recognizer:
            # Cancel ongoing recognition session
            self._speech_recognizer.stop_continuous_recognition_async()

        if self._audio_stream:
            # Close the audio stream on cancel
            self._audio_stream.close()

    @traced_stt
    async def _handle_transcription(
        self, transcript: str, is_final: bool, language: Optional[Language] = None
    ):
        """Handle a transcription result with tracing."""
        await self.stop_ttfb_metrics()
        await self.stop_processing_metrics()

    def _on_handle_recognized(self, event):
        # Azure event handler for recognized speech
        if event.result.reason == ResultReason.RecognizedSpeech and len(event.result.text) > 0:
            self.logger.debug(f"Transcript: {event.result.text}")
            language = getattr(event.result, "language", None) or self._settings.get("language")
            frame = TranscriptionFrame(
                event.result.text,
                self._user_id,
                time_now_iso8601(),
                language,
                result=event,
            )
            asyncio.run_coroutine_threadsafe(
                self._handle_transcription(event.result.text, True, language), self.get_event_loop()
            )
            asyncio.run_coroutine_threadsafe(self.push_frame(frame), self.get_event_loop())

    def _apply_phrase_list(self, recognizer: SpeechRecognizer):
        """Applies the configured vocabulary as a phrase list to the recognizer."""
        if self._vocab and recognizer:
            try:
                phrase_list_grammar = PhraseListGrammar.from_recognizer(recognizer)
                for phrase in self._vocab:
                    if isinstance(phrase, str) and phrase.strip():
                        phrase_list_grammar.addPhrase(phrase.strip())
                self.logger.info(f"Applied phrase list to Azure STT: {self._vocab}")
            except Exception as e:
                self.logger.error(f"Failed to apply phrase list grammar: {e}")

    async def set_language(self, language: Language):
        """Updates the primary recognition language for Azure STT service."""
        if self._additional_languages and language in self._additional_languages:
            self.logger.info(f"Language {language} is already in additional languages, skipping.")
            return
        self.logger.info(f"Switching STT language to: [{language}]")

        # Convert to Azure's language code format
        azure_language = language_to_azure_language(language)
        if not azure_language:
            self.logger.warning(f"Could not map language {language}, keeping current setting.")
            return

        # Update primary language
        self._primary_language = language

        # Update the speech config
        self._speech_config.speech_recognition_language = azure_language

        # Re-apply optimizations for faster transcripts
        self._speech_config.set_property(PropertyId.Speech_SegmentationSilenceTimeoutMs, "400")

        # If we have an active recognizer, we need to recreate it with the new language settings
        if self._speech_recognizer:
            # Stop current recognition - making sure to properly handle the ResultFuture
            stop_future = self._speech_recognizer.stop_continuous_recognition_async()
            await asyncio.to_thread(stop_future.get)  # Wait for stop to complete

            # Close the existing audio stream
            if self._audio_stream:
                self._audio_stream.close()

        # Create a new audio stream with same settings
        stream_format = AudioStreamFormat(samples_per_second=self.sample_rate, channels=1)
        self._audio_stream = PushAudioInputStream(stream_format)
        audio_config = AudioConfig(stream=self._audio_stream)

        # Create new speech recognizer with updated primary language
        self.logger.debug(
            f"Reconfiguring Azure STT for language: {self._speech_config.speech_recognition_language}"
        )
        self._speech_recognizer = SpeechRecognizer(
            speech_config=self._speech_config, audio_config=audio_config
        )

        # Add session events for logging
        self._speech_recognizer.session_started.connect(
            lambda evt: self.logger.info(
                f"Azure STT session started with language: {azure_language}"
            )
        )
        self._speech_recognizer.session_stopped.connect(
            lambda evt: self.logger.info("Azure STT session stopped")
        )

        # Re-apply phrase list to the new recognizer
        self._apply_phrase_list(self._speech_recognizer)

        # Reconnect events and restart recognition
        self._speech_recognizer.recognized.connect(self._on_handle_recognized)
        self._speech_recognizer.start_continuous_recognition_async()
