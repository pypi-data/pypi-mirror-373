from pathlib import Path

from audiotools.audiotools import AudioSignal
from audiotools.audiotools import post
from audiotools.audiotools import transforms


def test_audio_table():
    tfm = transforms.LowPass()

    audio_dict = {}

    audio_dict["inputs"] = [
        AudioSignal.excerpt("tests/audio/spk/f10_script4_produced.wav", duration=5)
        for _ in range(3)
    ]
    audio_dict["outputs"] = []
    for i in range(3):
        x = audio_dict["inputs"][i]

        kwargs = tfm.instantiate()
        output = tfm(x.clone(), **kwargs)
        audio_dict["outputs"].append(output)

    post.audio_table(audio_dict)
