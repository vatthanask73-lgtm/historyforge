#!/usr/bin/env python3
"""HistoryForge — utils/audio_mixer.py — Mix narration + music + SFX."""

import os
import logging
from pathlib import Path

log = logging.getLogger("audio_mixer")

try:
    from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips
except ImportError:
    pass


def mix_audio(narration_path, music_path=None, output_path=None,
              narration_volume=1.0, music_volume=0.20,
              music_fade_in=2.0, music_fade_out=3.0, **kwargs):
    narration = AudioFileClip(narration_path)
    dur = narration.duration
    layers = [narration.volumex(narration_volume)]

    if music_path and os.path.isfile(music_path):
        music = AudioFileClip(music_path)
        if music.duration < dur:
            reps = int(dur / music.duration) + 1
            music = concatenate_audioclips([music] * reps)
        music = music.subclip(0, dur)
        if music_fade_in > 0:
            music = music.audio_fadein(music_fade_in)
        if music_fade_out > 0:
            music = music.audio_fadeout(music_fade_out)
        music = music.volumex(music_volume)
        layers.append(music)

    comp = CompositeAudioClip(layers).set_duration(dur)
    if output_path is None:
        output_path = str(Path(narration_path).with_suffix(".mixed.mp3"))
    comp.write_audiofile(output_path, fps=44100, logger=None)
    log.info("Mixed audio: %s", output_path)
    return output_path
