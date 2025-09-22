"""Utility helpers for remembering which topics were already used."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Set
import json


def load_used_topics(path: Path) -> Set[str]:
    """Load previously used topics from ``path``."""

    if not path.exists():
        return set()

    with path.open("r", encoding="utf-8") as fp:
        try:
            data = json.load(fp)
        except json.JSONDecodeError:
            return set()

    if isinstance(data, list):
        return {str(item) for item in data}

    return set()


def save_used_topics(path: Path, topics: Iterable[str]) -> None:
    """Persist ``topics`` to ``path`` in JSON format."""

    sorted_topics = sorted({topic.strip() for topic in topics if topic})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(sorted_topics, fp, indent=2, ensure_ascii=False)
