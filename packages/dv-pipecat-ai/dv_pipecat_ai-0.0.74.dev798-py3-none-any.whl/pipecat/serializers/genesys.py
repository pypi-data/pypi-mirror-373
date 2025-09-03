import base64
import json
from typing import Optional

from pydantic import BaseModel

from pipecat.audio.utils import create_default_resampler, pcm_to_ulaw, ulaw_to_pcm
from pipecat.frames.frames import (
    AudioRawFrame,
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


class GenesysFrameSerializer(FrameSerializer):
    class InputParams(BaseModel):
        genesys_sample_rate: int = 8000  # Default Genesys rate (8kHz)
        sample_rate: Optional[int] = None  # Pipeline input rate

    def __init__(self, session_id: str, params: InputParams = InputParams()):
        self._session_id = session_id
        self._params = params
        self._genesys_sample_rate = self._params.genesys_sample_rate
        self._sample_rate = 0  # Pipeline input rate
        self._resampler = create_default_resampler()
        self._seq = 1  # Sequence number for outgoing messages

    @property
    def type(self) -> FrameSerializerType:
        return FrameSerializerType.TEXT

    async def setup(self, frame: StartFrame):
        self._sample_rate = self._params.sample_rate or frame.audio_in_sample_rate

    async def serialize(self, frame: Frame) -> str | bytes | None:
        if isinstance(frame, StartInterruptionFrame):
            answer = {
                "version": "2",
                "type": "clearAudio",  # Or appropriate event for interruption
                "seq": self._seq,
                "id": self._session_id,
            }
            self._seq += 1
            return json.dumps(answer)
        elif isinstance(frame, AudioRawFrame):
            data = frame.audio
            # Convert PCM to 8kHz μ-law for Genesys
            serialized_data = await pcm_to_ulaw(
                data, frame.sample_rate, self._genesys_sample_rate, self._resampler
            )
            payload = base64.b64encode(serialized_data).decode("utf-8")
            answer = {
                "version": "2",
                "type": "audio",
                "seq": self._seq,
                "id": self._session_id,
                "media": {
                    "payload": payload,
                    "format": "PCMU",
                    "rate": self._genesys_sample_rate,
                },
            }
            self._seq += 1
            return json.dumps(answer)
        elif isinstance(frame, (TransportMessageFrame, TransportMessageUrgentFrame)):
            return json.dumps(frame.message)

    async def deserialize(self, data: str | bytes) -> Frame | None:
        message = json.loads(data)
        if message.get("type") == "audio":
            payload_base64 = message["media"]["payload"]
            payload = base64.b64decode(payload_base64)
            # Convert Genesys 8kHz μ-law to PCM at pipeline input rate
            deserialized_data = await ulaw_to_pcm(
                payload, self._genesys_sample_rate, self._sample_rate, self._resampler
            )
            audio_frame = InputAudioRawFrame(
                audio=deserialized_data, num_channels=1, sample_rate=self._sample_rate
            )
            return audio_frame
        elif message.get("type") == "dtmf":
            digit = message.get("dtmf", {}).get("digit")
            try:
                return InputDTMFFrame(KeypadEntry(digit))
            except ValueError:
                return None
        else:
            return None
