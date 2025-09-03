from typing import Awaitable, Callable

from loguru import logger

from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    Frame,
    FunctionCallResultFrame,
    InterimTranscriptionFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
)
from pipecat.processors.user_idle_processor import UserIdleProcessor


class TwoStageUserIdleProcessor(UserIdleProcessor):
    def __init__(
        self,
        warning_timeout: float,
        end_timeout: float,
        warning_callback: Callable[[UserIdleProcessor], Awaitable[None]],
        end_callback: Callable[[UserIdleProcessor], Awaitable[None]],
        **kwargs,
    ):
        super().__init__(callback=self._internal_callback, timeout=warning_timeout, **kwargs)
        self.warning_timeout = warning_timeout
        self.end_timeout = end_timeout
        self.warning_callback = warning_callback
        self.end_callback = end_callback
        self.stage = 0  # 0: warning stage, 1: end stage
        self.last_speaker = None

    async def _internal_callback(self, idle_processor: UserIdleProcessor, retry_count: int):
        self.logger.debug("_internal_callback called")
        if self.stage == 0:
            # First stage timeout - trigger warning
            await self.warning_callback(self)
            self.stage = 1
            self.logger.debug("Stage set to 1")
            # Calculate remaining time and update timeout
            self._timeout = max(0, self.end_timeout - self.warning_timeout)
            self.logger.debug(f"Setting timeout of {self._timeout}")
            self._idle_event.set()  # Interrupt wait to apply new timeout
            return True
        else:
            # Final timeout - trigger end callback
            self.logger.debug("User Idle, calling end callback")
            await self.end_callback(self)
            return False

    async def process_frame(self, frame: Frame, direction):
        await super().process_frame(frame, direction)
        # Track last speaker
        if isinstance(frame, UserStartedSpeakingFrame):
            self.last_speaker = "user"
        elif isinstance(frame, BotStartedSpeakingFrame):
            self.last_speaker = "bot"
        if self._conversation_started:
            # Reset to initial stage when we receive any valid user speech
            if self.stage == 1 and (
                isinstance(frame, (InterimTranscriptionFrame, TranscriptionFrame))
                and frame.text.strip()
            ):
                self.logger.debug("Resetting stage to 0")
                self.stage = 0
                self._timeout = self.warning_timeout
                self._idle_event.set()  # Apply timeout reset immediately
            if isinstance(frame, FunctionCallResultFrame):
                self.logger.debug("Function call result received")
                self.stage = 0
                self._timeout = self.warning_timeout
                self._idle_event.set()
