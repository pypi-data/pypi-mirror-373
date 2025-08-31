"""Example for using HiggsAudio for generating both the transcript and audio in an interleaved manner."""

import os
import time

import torch
#import torchaudio
from loguru import logger
import click
import soundfile

from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine, HiggsAudioResponse

from input_samples import INPUT_SAMPLES

MODEL_PATH = "bosonai/higgs-audio-v2-generation-3B-base"
AUDIO_TOKENIZER_PATH = "bosonai/higgs-audio-v2-tokenizer"


@click.command()
@click.argument("example", type=click.Choice(list(INPUT_SAMPLES.keys())))
def main(example: str):
    test(example, MODEL_PATH, AUDIO_TOKENIZER_PATH)


def test(example: str, model_path: str, audio_tokenizer_path: str, save_path=""):
    input_sample = INPUT_SAMPLES[example]()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    serve_engine = HiggsAudioServeEngine(
        model_path,
        audio_tokenizer_path,
        device=device,
    )

    logger.info("Starting generation...")
    start_time = time.time()
    output: HiggsAudioResponse = serve_engine.generate(
        chat_ml_sample=input_sample,
        max_new_tokens=1024,
        temperature=1.0,
        top_p=0.95,
        top_k=50,
        stop_strings=["<|end_of_text|>", "<|eot_id|>"],
    )
    elapsed_time = time.time() - start_time

    save_path = f"./output_{example}.wav" if not save_path else save_path
    soundfile.write(save_path, output.audio, output.sampling_rate)
    info = soundfile.info(save_path, verbose=True)

    # torchaudio.save(save_path, torch.from_numpy(output.audio)[None, :], output.sampling_rate)

    print(info)
    logger.info(f"Generated text:\n{output.generated_text}")
    logger.info(
        f"Generation time: {elapsed_time:.2f} seconds, duration: {info.duration:.2f} seconds, RTF: {(elapsed_time / info.duration):.2f}"
    )
    logger.info(f"Saved audio to {save_path}")


if __name__ == "__main__":
    main()
