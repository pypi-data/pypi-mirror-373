import datetime
import os
import time
import wave
from typing import Optional
import asyncio

import numpy as np
from loguru import logger

from pipecat.audio.filters.base_audio_filter import BaseAudioFilter
from pipecat.audio.utils import create_default_resampler
from pipecat.frames.frames import FilterControlFrame, FilterEnableFrame


try:
    from pyrnnoise import RNNoise
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    logger.error(
        "In order to use the PyRnnNoise filter, add `pyrnnoise` to remote-requirements.txt/requirements.txt."
    )
    raise Exception(f"Missing module: {e}")


# Sadly BaseAudioFilter has no concept of tracking metrics.
class PyRnnNoiseLocalFilter(BaseAudioFilter):
    """Audio filter that uses PyRNNoise."""

    def __init__(
        self, call_id: str, max_buffer_duration: float = 60.0, save_audio: bool = False
    ) -> None:
        self._filtering = True
        self._sample_rate = 0
        self._filter_ready = True
        self.denoiser: Optional[RNNoise] = None
        self.resampler = create_default_resampler()
        self.model_sample_rate = 48000

        self._frame_size = 480  # py rnn needs the frame size to be 480
        self._resampled_buffer = np.empty(0, dtype=np.int16)
        self.metric_tracker = list()  # will see how i can export this
        self.bot_logger = logger.bind(call_id=call_id)

        # Audio saving configuration
        self._save_audio = save_audio
        self._max_buffer_duration = max_buffer_duration  # seconds
        self._max_buffer_bytes = 0  # will be calculated in start()
        self._base_audio_buffer = bytearray()
        self._processed_audio_buffer = bytearray()
        self.call_id = call_id
        self._file_counter = 0

    async def start(self, sample_rate: int):
        self._sample_rate = sample_rate
        self.denoiser = RNNoise(self.model_sample_rate)
        self.denoiser.channels = 1
        self._resampled_buffer = np.empty(0, dtype=np.int16)

        # Calculate max buffer size in bytes (16-bit samples, mono)
        self._max_buffer_bytes = int(self._max_buffer_duration * sample_rate * 2)
        self.bot_logger.info(
            f"RNN Noise filter initialized. Sample rate: {sample_rate}Hz, max buffer: {self._max_buffer_duration}s ({self._max_buffer_bytes} bytes)"
        )

    async def stop(self):
        # Save audio buffers as WAV files before cleanup
        if self._save_audio:
            await self._save_audio_buffers()
        return

    async def _check_and_save_buffers(self):
        if not self._save_audio or len(self._base_audio_buffer) < self._max_buffer_bytes:
            return

        await self._save_audio_buffers()

    async def _save_audio_buffers(self):
        """Save the collected audio buffers as WAV files."""
        if not self._base_audio_buffer and not self._processed_audio_buffer:
            self.bot_logger.debug("No audio data to save")
            return

        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: os.makedirs(logs_dir, exist_ok=True)
        )

        try:
            # Save base (original) audio buffer
            if self._base_audio_buffer:
                base_filename = os.path.join(
                    logs_dir, f"base_audio_{self.call_id}_{self._file_counter:03d}.wav"
                )
                await self._save_wav_file(self._base_audio_buffer, base_filename, self._sample_rate)
                self.bot_logger.info(
                    f"Saved base audio buffer to {base_filename} ({len(self._base_audio_buffer)} bytes)"
                )

            # Save processed (filtered) audio buffer
            if self._processed_audio_buffer:
                processed_filename = os.path.join(
                    logs_dir, f"processed_audio_{self.call_id}_{self._file_counter:03d}.wav"
                )
                await self._save_wav_file(
                    self._processed_audio_buffer, processed_filename, self._sample_rate
                )
                self.bot_logger.info(
                    f"Saved processed audio buffer to {processed_filename} ({len(self._processed_audio_buffer)} bytes)"
                )

            # Clear buffers and increment counter
            self._base_audio_buffer.clear()
            self._processed_audio_buffer.clear()
            self._file_counter += 1

        except Exception as e:
            self.bot_logger.error(f"Error saving audio buffers: {e}")

    async def _save_wav_file(self, audio_buffer: bytearray, filename: str, sample_rate: int):
        """Save audio buffer to WAV file without blocking the event loop."""

        def _write_wav_sync():
            with wave.open(filename, "wb") as wf:
                wf.setsampwidth(2)  # 16-bit samples (2 bytes)
                wf.setnchannels(1)  # Mono
                wf.setframerate(sample_rate)
                wf.writeframes(audio_buffer)

        # Run the synchronous file operation in a thread pool to avoid blocking
        await asyncio.get_event_loop().run_in_executor(None, _write_wav_sync)

    async def process_frame(self, frame: FilterControlFrame):
        if isinstance(frame, FilterEnableFrame):
            self._filtering = frame.enable

    async def filter(self, audio: bytes) -> bytes:
        if not self._filtering or not audio:
            return audio

        # Check if denoiser is initialized
        if self.denoiser is None:
            return audio

        # Store original audio if saving is enabled
        if self._save_audio:
            self._base_audio_buffer.extend(audio)

        resampled_audio_bytes = await self.resampler.resample(
            audio, self._sample_rate, self.model_sample_rate
        )

        incoming = np.frombuffer(resampled_audio_bytes, dtype=np.int16)
        if self._resampled_buffer.size:
            data = np.concatenate([self._resampled_buffer, incoming])
        else:
            data = incoming

        out_frames = []
        pos = 0

        # pipecat sends 160 samples in a frame at a sampling rate of 8000 which is 20 ms of audio data. Pyrnn needs 10 ms of data in a frame at 48000 sampling rate
        while pos + self._frame_size <= data.shape[0]:
            frame = data[pos : pos + self._frame_size]

            frame_2d = np.atleast_2d(frame)
            _, denoised = self.denoiser.denoise_frame(frame_2d, partial=False)
            out_frames.append(denoised[0])
            pos += self._frame_size

        # TODO: in some cases small amount of audio gets left inside this (2-3 ms), need to send that back as it is.
        self._resampled_buffer = data[pos:]

        if not out_frames:
            return b""

        cleaned_audio = np.concatenate(out_frames)
        filtered_audio_bytes = (
            np.clip(cleaned_audio, -32768, 32767).astype(np.int16, copy=False).tobytes()
        )
        resampled_filtered_audio_bytes = await self.resampler.resample(
            filtered_audio_bytes, self.model_sample_rate, self._sample_rate
        )

        # Store processed audio and check if we need to save
        if self._save_audio:
            self._processed_audio_buffer.extend(resampled_filtered_audio_bytes)
            await self._check_and_save_buffers()

        # self.metric_tracker.append(time.perf_counter() - s_time)
        return resampled_filtered_audio_bytes
