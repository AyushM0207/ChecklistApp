"""Generate narration audio files from the script."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pyttsx3


def synthesize_lines(lines: Iterable[str], output_dir: Path) -> List[Path]:
    """Synthesize one audio file per line and return their paths."""

    output_dir.mkdir(parents=True, exist_ok=True)
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)

    paths: List[Path] = []
    for index, line in enumerate(lines):
        path = output_dir / f"line_{index:02d}.wav"
        engine.save_to_file(line, str(path))
        paths.append(path)

    engine.runAndWait()
    engine.stop()
    return paths
