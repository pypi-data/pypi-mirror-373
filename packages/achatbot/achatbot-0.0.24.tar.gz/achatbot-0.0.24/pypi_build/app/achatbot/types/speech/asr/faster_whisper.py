from dataclasses import dataclass
from typing import Optional, Union

from achatbot.types.speech.asr.base import ASRArgs
from faster_whisper.vad import VadOptions


@dataclass
class WhisperFasterASRArgs(ASRArgs):
    vad_filter: bool = False
    vad_parameters: Optional[Union[dict, VadOptions]] = None
