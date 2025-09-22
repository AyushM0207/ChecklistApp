"""Create colourful cartoon slides for each script line."""
from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Iterable, List

from PIL import Image, ImageDraw, ImageFont


_IMAGE_SIZE = (1080, 1920)  # 9:16 portrait suitable for YouTube Shorts
_TEXT_COLOR = (20, 20, 20)
_CAPTION_COLOR = (255, 255, 255)
_CAPTION_BG = (30, 30, 30, 180)


def _random_pastel(seed: int) -> tuple[int, int, int]:
    random.seed(seed)
    base = [random.randint(120, 220) for _ in range(3)]
    return tuple(base)


def _load_font(assets_dir: Path, size: int) -> ImageFont.ImageFont:
    """Load a playful font, preferring a user-provided asset."""

    custom_font = assets_dir / "cartoon.ttf"
    if custom_font.exists():
        return ImageFont.truetype(str(custom_font), size=size)
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)  # Common on Linux
    except OSError:
        return ImageFont.load_default()


def _draw_doodles(draw: ImageDraw.ImageDraw, seed: int) -> None:
    random.seed(seed)
    width, height = _IMAGE_SIZE
    for _ in range(6):
        shape_type = random.choice(["cloud", "star", "swirl"])
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(120, 260)
        colour = tuple(random.randint(80, 200) for _ in range(3)) + (160,)
        if shape_type == "cloud":
            for offset in range(3):
                bbox = [
                    x + offset * 30 - size // 2,
                    y - size // 2,
                    x + offset * 30 + size // 2,
                    y + size // 2,
                ]
                draw.ellipse(bbox, fill=colour)
        elif shape_type == "star":
            points = []
            for i in range(5):
                angle = i * (2 * math.pi / 5)
                outer = (x + math.cos(angle) * size, y + math.sin(angle) * size)
                inner_angle = angle + math.pi / 5
                inner = (x + math.cos(inner_angle) * size / 2, y + math.sin(inner_angle) * size / 2)
                points.extend([outer, inner])
            draw.polygon(points, fill=colour)
        else:  # swirl
            for radius in range(20, size, 15):
                bbox = [x - radius, y - radius, x + radius, y + radius]
                start = random.randint(0, 360)
                end = start + random.randint(90, 270)
                draw.arc(bbox, start, end, fill=colour, width=8)


def _draw_caption(draw: ImageDraw.ImageDraw, topic: str, font: ImageFont.ImageFont) -> None:
    text = f"Trending: {topic}"[:60]
    text_width, text_height = draw.textsize(text, font=font)
    padding = 20
    rect = [
        (_IMAGE_SIZE[0] - text_width) // 2 - padding,
        40,
        (_IMAGE_SIZE[0] + text_width) // 2 + padding,
        40 + text_height + padding,
    ]
    draw.rounded_rectangle(rect, radius=30, fill=_CAPTION_BG)
    draw.text((rect[0] + padding // 2, rect[1] + padding // 2), text, font=font, fill=_CAPTION_COLOR)


def create_frames(topic: str, script_lines: Iterable[str], output_dir: Path, assets_dir: Path) -> List[Path]:
    """Create one frame per script line and return their paths."""

    output_dir.mkdir(parents=True, exist_ok=True)
    frames: List[Path] = []

    header_font = _load_font(assets_dir, 70)
    body_font = _load_font(assets_dir, 64)

    for index, line in enumerate(script_lines):
        background = Image.new("RGBA", _IMAGE_SIZE, color=_random_pastel(hash((topic, index))))
        draw = ImageDraw.Draw(background, "RGBA")
        _draw_doodles(draw, seed=hash((topic, "doodle", index)))
        _draw_caption(draw, topic, header_font)

        bbox = (120, 520, _IMAGE_SIZE[0] - 120, _IMAGE_SIZE[1] - 320)
        draw.rounded_rectangle(bbox, radius=60, fill=(255, 255, 255, 235), outline=(10, 10, 10, 255), width=6)

        text_width, text_height = draw.multiline_textsize(line, font=body_font, spacing=12)
        text_x = bbox[0] + (bbox[2] - bbox[0] - text_width) / 2
        text_y = bbox[1] + (bbox[3] - bbox[1] - text_height) / 2

        draw.multiline_text((text_x, text_y), line, font=body_font, fill=_TEXT_COLOR, align="center", spacing=12)

        path = output_dir / f"frame_{index:02d}.png"
        background.convert("RGB").save(path, format="PNG")
        frames.append(path)

    return frames
