import logging
import asyncio

from achatbot.processors.audio_input_processor import AudioVADInputProcessor
from achatbot.common.types import AudioCameraParams
from achatbot.types.frames import InputImageRawFrame


class AudioVADCameraInputProcessor(AudioVADInputProcessor):
    def __init__(
        self,
        params: AudioCameraParams,
        name: str | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
        **kwargs,
    ):
        super().__init__(params=params, name=name, loop=loop, **kwargs)
        self._params = params

    async def push_video_frame(self, frame: InputImageRawFrame):
        if self._params.camera_in_enabled:
            await self.push_frame(frame)
