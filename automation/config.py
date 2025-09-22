"""Configuration loading for the automation tool."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import json


@dataclass
class Settings:
    """Container holding all runtime settings for the automation workflow."""

    trending_region: str = "united_states"
    output_dir: Path = Path("output")
    assets_dir: Path = Path("assets")
    videos_per_day: int = 4
    youtube_category_id: str = "23"  # Comedy
    tags: List[str] = field(default_factory=lambda: ["shorts", "cartoon", "comedy"])
    video_title_template: str = "{topic} - Cartoon Comedy Short"
    video_description_template: str = (
        "A quick cartoon short riffing on {topic}.\n"
        "Automated script: {script}\n\n"
        "Created automatically with the ChecklistApp automation tool."
    )
    youtube_privacy_status: str = "private"
    youtube_client_secrets_file: Path = Path("credentials/client_secret.json")
    youtube_token_file: Path = Path("credentials/token.json")
    background_music_file: Optional[Path] = None

    def ensure_directories(self) -> None:
        """Ensure directories referenced by the configuration exist."""

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        if self.youtube_token_file:
            self.youtube_token_file.parent.mkdir(parents=True, exist_ok=True)


_PATH_FIELDS = {
    "output_dir",
    "assets_dir",
    "youtube_client_secrets_file",
    "youtube_token_file",
    "background_music_file",
}


def _coerce_paths(raw: dict) -> dict:
    """Convert known path fields to :class:`~pathlib.Path` instances."""

    coerced: dict = {}
    for key, value in raw.items():
        if key in _PATH_FIELDS and value is not None:
            coerced[key] = Path(value).expanduser()
        else:
            coerced[key] = value
    return coerced


def load_settings(path: Path) -> Settings:
    """Load settings from a JSON configuration file.

    Parameters
    ----------
    path:
        Path to the JSON configuration file.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file '{path}' does not exist. Create it from config.sample.json."
        )

    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    settings = Settings(**_coerce_paths(data))
    settings.ensure_directories()
    return settings
