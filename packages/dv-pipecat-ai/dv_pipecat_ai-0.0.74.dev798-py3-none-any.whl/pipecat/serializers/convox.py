#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import base64
import datetime
import json
from typing import Optional

from loguru import logger
from pydantic import BaseModel

from pipecat.audio.utils import create_default_resampler
from pipecat.frames.frames import (
    AudioRawFrame,
    CancelFrame,
    EndFrame,
    Frame,
    InputAudioRawFrame,
    InputDTMFFrame,
    KeypadEntry,
    StartFrame,
    StartInterruptionFrame,
    TransportMessageFrame,
    TransportMessageUrgentFrame,
)
from pipecat.serializers.base_serializer import FrameSerializer, FrameSerializerType


class ConVoxFrameSerializer(FrameSerializer):
    """Serializer for ConVox WebSocket protocol.

    This serializer handles converting between Pipecat frames and ConVox's WebSocket
    protocol. It supports audio conversion, DTMF events, and real-time communication
    with ConVox telephony systems.

    ConVox WebSocket protocol typically uses:
    - PCM audio format at 16kHz sample rate
    - Base64 encoded audio payloads
    - JSON message format for control and media events
    """

    class InputParams(BaseModel):
        """Configuration parameters for ConVoxFrameSerializer.

        Attributes:
            convox_sample_rate: Sample rate used by ConVox, defaults to 16000 Hz.
            sample_rate: Optional override for pipeline input sample rate.
            auto_hang_up: Whether to automatically terminate call on EndFrame.
        """

        convox_sample_rate: int = 16000
        sample_rate: Optional[int] = None
        auto_hang_up: bool = False

    def __init__(
        self,
        stream_id: str,
        call_id: Optional[str] = None,
        params: Optional[InputParams] = None,
    ):
        """Initialize the ConVoxFrameSerializer.

        Args:
            stream_id: The ConVox stream identifier.
            call_id: The associated ConVox call identifier.
            params: Configuration parameters.
        """
        self._stream_id = stream_id
        self._call_id = call_id
        self._params = params or ConVoxFrameSerializer.InputParams()

        self._convox_sample_rate = self._params.convox_sample_rate
        self._sample_rate = 0  # Pipeline input rate
        self._call_ended = False

        self._resampler = create_default_resampler()

    @property
    def type(self) -> FrameSerializerType:
        """Gets the serializer type.

        Returns:
            The serializer type as TEXT for JSON WebSocket messages.
        """
        return FrameSerializerType.TEXT

    async def setup(self, frame: StartFrame):
        """Sets up the serializer with pipeline configuration.

        Args:
            frame: The StartFrame containing pipeline configuration.
        """
        self._sample_rate = self._params.sample_rate or frame.audio_in_sample_rate

    async def serialize(self, frame: Frame) -> str | bytes | None:
        """Serializes a Pipecat frame to ConVox WebSocket format.

        Handles conversion of various frame types to ConVox WebSocket messages.

        Args:
            frame: The Pipecat frame to serialize.

        Returns:
            Serialized data as JSON string, or None if the frame isn't handled.
        """
        if isinstance(frame, StartInterruptionFrame):
            # Clear/interrupt command for ConVox
            message = {
                "event": "clear",
                "stream_id": self._stream_id,
                "call_id": self._call_id,
            }
            return json.dumps(message)

        elif isinstance(frame, AudioRawFrame):
            if self._call_ended:
                logger.debug("🎵 CONVOX SERIALIZE: Skipping audio - call has ended")
                return None

            # Convert PCM audio to ConVox format
            data = frame.audio
            # logger.info(
            #     f"🎵 CONVOX SERIALIZE: Processing AudioRawFrame - Original: {len(data)} bytes at {frame.sample_rate}Hz"
            # )

            # Resample to ConVox sample rate
            serialized_data = await self._resampler.resample(
                data, frame.sample_rate, self._convox_sample_rate
            )
            # logger.info(
            #     f"🎵 CONVOX SERIALIZE: Resampled to {self._convox_sample_rate}Hz - {len(serialized_data)} bytes"
            # )

            # Encode as base64 for transmission
            payload = base64.b64encode(serialized_data).decode("ascii")

            # ConVox expects play_audio event format according to the documentation
            timestamp = datetime.datetime.now().isoformat()

            message = {
                "event": "play_audio",
                "stream_id": self._stream_id,
                "call_id": self._call_id,
                "details": {
                    "timestamp": timestamp,
                    "direction": "WSS",
                    "message": payload,
                },
            }

            # logger.info(
            #     f"🎵 CONVOX SERIALIZE: Sending play_audio event to ConVox - stream_id: {self._stream_id}, call_id: {self._call_id}"
            # )
            # logger.debug(f"🎵 CONVOX SERIALIZE: Complete message: {json.dumps(message, indent=2)}")

            return json.dumps(message)

        elif isinstance(frame, (TransportMessageFrame, TransportMessageUrgentFrame)):
            # Pass through transport messages
            return json.dumps(frame.message)

        return None

    async def deserialize(self, data: str | bytes) -> Frame | None:
        """Deserializes ConVox WebSocket data to Pipecat frames.

        Handles conversion of ConVox media events to appropriate Pipecat frames.

        Args:
            data: The raw WebSocket data from ConVox.

        Returns:
            A Pipecat frame corresponding to the ConVox event, or None if unhandled.
        """
        try:
            message = json.loads(data)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from ConVox: {data}")
            return None

        # Log all incoming events for debugging and monitoring
        event = message.get("event")
        # logger.info(
        #     f"📥 CONVOX INCOMING EVENT: {event} - stream_id: {self._stream_id}, call_id: {self._call_id}"
        # )
        # logger.info(f"📥 CONVOX FULL MESSAGE: {json.dumps(message, indent=2)}")

        if event == "media":
            # Handle incoming audio data
            media = message.get("media", {})
            payload_base64 = media.get("payload")

            if not payload_base64:
                logger.warning("🎵 CONVOX DESERIALIZE: No payload in ConVox media message")
                return None

            try:
                payload = base64.b64decode(payload_base64)
                # logger.info(
                #     f"🎵 CONVOX DESERIALIZE: Received audio from ConVox - {len(payload)} bytes at {self._convox_sample_rate}Hz"
                # )
            except Exception as e:
                logger.error(f"🎵 CONVOX DESERIALIZE: Error decoding ConVox audio payload: {e}")
                return None

            # Convert from ConVox sample rate to pipeline sample rate
            deserialized_data = await self._resampler.resample(
                payload,
                self._convox_sample_rate,
                self._sample_rate,
            )
            # logger.info(
            #     f"🎵 CONVOX DESERIALIZE: Resampled to pipeline rate {self._sample_rate}Hz - {len(deserialized_data)} bytes"
            # )

            audio_frame = InputAudioRawFrame(
                audio=deserialized_data,
                num_channels=1,  # ConVox typically uses mono audio
                sample_rate=self._sample_rate,
            )
            # logger.info(
            #     f"🎵 CONVOX DESERIALIZE: Created InputAudioRawFrame for pipeline processing"
            # )
            return audio_frame

        elif event == "dtmf":
            # Handle DTMF events
            dtmf_data = message.get("dtmf", {})
            digit = dtmf_data.get("digit")

            if digit:
                try:
                    return InputDTMFFrame(KeypadEntry(digit))
                except ValueError:
                    logger.warning(f"Invalid DTMF digit from ConVox: {digit}")
                    return None

        elif event == "start":
            # Handle stream start event
            logger.info(f"ConVox stream started: {message}")
            return None

        elif event == "bridge_connected":
            logger.info(f"ConVox bridge connected: {message}")
            return None

        elif event == "stop":
            # Handle stream stop event
            logger.info(f"ConVox stream stopped: {message}")
            return None

        elif event == "error":
            # Handle error events
            error_msg = message.get("error", "Unknown error")
            logger.error(f"ConVox error: {error_msg}")
            return None

        elif event == "callEnd" or event == "call_end":
            logger.info("ConVox call end event received")
            self._call_ended = True
            return CancelFrame()

        elif event == "failed":
            logger.info(f"ConVox failed event received: {message}")
            self._call_ended = True
            return CancelFrame()
        # else:
        #     logger.warning(
        #         f"📥 CONVOX UNHANDLED EVENT: {event} - Full message: {json.dumps(message, indent=2)}"
        #     )

        return None
