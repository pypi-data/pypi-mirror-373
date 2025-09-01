import os

from achatbot.common.types import MODELS_DIR
from achatbot.common.session import Session
from achatbot.common.factory import EngineClass
from achatbot.common.interface import IAsrLive
from achatbot.thirdparty.streaming_sensevoice import StreamingSenseVoice


class ASRStreamingSenseVoice(EngineClass, IAsrLive):
    TAG = "asr_streaming_sensevoice"

    def __init__(self, **kwargs):
        super().__init__()
        self.args = kwargs
        model_path = kwargs.pop("model", os.path.join(MODELS_DIR, "FunAudioLLM/SenseVoiceSmall"))
        self.model = StreamingSenseVoice(model=model_path, **kwargs)

    def reset(self):
        self.model.reset()

    async def streaming_transcribe(self, session: Session, **kwargs):
        audio_chunk = session.ctx.state["audio_chunk"]
        is_last = session.ctx.state["is_last"]
        for res in self.model.streaming_inference(audio_chunk, is_last):
            # {"timestamps":[],"text":""}
            yield res
