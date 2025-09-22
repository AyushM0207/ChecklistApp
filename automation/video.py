"""Assemble frames and narration audio into a short vertical video."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    ImageClip,
    concatenate_videoclips,
)


def build_video(
    image_paths: Iterable[Path],
    audio_paths: Iterable[Path],
    output_path: Path,
    background_music: Optional[Path] = None,
    fps: int = 24,
) -> Path:
    """Create a video from ``image_paths`` and ``audio_paths``."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_paths = list(image_paths)
    audio_paths = list(audio_paths)
    if len(image_paths) != len(audio_paths):
        raise ValueError("Number of images must match number of audio files.")

    clips: List[ImageClip] = []
    narration_audio: List[AudioFileClip] = []
    background_clip: Optional[AudioFileClip] = None

    try:
        for image_path, audio_path in zip(image_paths, audio_paths):
            audio_clip = AudioFileClip(str(audio_path))
            duration = max(audio_clip.duration + 0.4, 2.5)
            image_clip = ImageClip(str(image_path)).set_duration(duration)
            image_clip = image_clip.set_audio(audio_clip)
            clips.append(image_clip)
            narration_audio.append(audio_clip)

        final_clip = concatenate_videoclips(clips, method="compose")

        if background_music is not None and background_music.exists():
            background_clip = AudioFileClip(str(background_music)).volumex(0.2)
            background_clip = background_clip.set_duration(final_clip.duration)
            final_audio = CompositeAudioClip([final_clip.audio, background_clip])
            final_clip = final_clip.set_audio(final_audio)

        final_clip.write_videofile(
            str(output_path),
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            threads=2,
            temp_audiofile=str(output_path.with_suffix(".temp-audio.m4a")),
            remove_temp=True,
        )
    finally:
        for clip in clips:
            clip.close()
        for audio in narration_audio:
            audio.close()
        if background_clip is not None:
            background_clip.close()

    return output_path
