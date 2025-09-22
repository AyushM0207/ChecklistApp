"""Entry point orchestrating the daily automation run."""
from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from . import audio, config, history, script_generator, trends, uploader, video, visuals

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def _select_topics(
    settings: config.Settings,
    explicit_topic: str | None,
    used_topics: set[str],
    desired_count: int,
) -> List[str]:
    """Return a list of topics to cover in the current automation run."""

    desired_count = max(1, desired_count)

    if explicit_topic:
        logging.info(
            "Using manually supplied topic '%s'; overriding configured count to one video.",
            explicit_topic,
        )
        return [explicit_topic]

    logging.info("Selecting %d topic(s) for this batch.", desired_count)

    try:
        candidate_limit = max(desired_count * 3, 20)
        candidates = trends.fetch_trending_topics(settings.trending_region, limit=candidate_limit)
    except trends.TrendFetchError as exc:
        logging.warning(
            "Falling back to default topic list because trending fetch failed: %s",
            exc,
        )
        return ["Cartoon Mishaps"] * desired_count

    topics: List[str] = []
    for topic in candidates:
        if topic not in used_topics and topic not in topics:
            topics.append(topic)
        if len(topics) == desired_count:
            break

    if len(topics) < desired_count:
        logging.info(
            "Only %d fresh trending topic(s) found; reusing suggestions to reach %d videos.",
            len(topics),
            desired_count,
        )
        pool = candidates or ["Cartoon Mishaps"]
        while len(topics) < desired_count:
            topics.append(pool[len(topics) % len(pool)])

    logging.info("Selected topics for run: %s", ", ".join(topics))
    return topics


def _render_video(
    topic: str,
    session_dir: Path,
    settings: config.Settings,
) -> Tuple[Path, List[str]]:
    """Generate assets and render a single video for ``topic``."""

    frame_dir = session_dir / "frames"
    audio_dir = session_dir / "audio"
    for directory in (session_dir, frame_dir, audio_dir):
        directory.mkdir(parents=True, exist_ok=True)

    script_lines = script_generator.generate_script(topic)
    logging.info("Generated script with %d lines for topic '%s'", len(script_lines), topic)

    frame_paths = visuals.create_frames(topic, script_lines, frame_dir, settings.assets_dir)
    audio_paths = audio.synthesize_lines(script_lines, audio_dir)
    logging.info(
        "Created %d frames and audio snippets for topic '%s'",
        len(frame_paths),
        topic,
    )

    video_path = video.build_video(
        frame_paths,
        audio_paths,
        output_path=session_dir / "cartoon_short.mp4",
        background_music=settings.background_music_file,
    )
    logging.info("Video exported to %s", video_path)

    return video_path, script_lines


def run(
    settings: config.Settings,
    explicit_topic: str | None = None,
    dry_run: bool = False,
    count: int | None = None,
) -> List[Path]:
    """Run the automation pipeline and optionally upload multiple videos to YouTube."""

    desired_count = count if count is not None else settings.videos_per_day
    if desired_count < 1:
        logging.warning("Invalid video count %s provided; defaulting to 1.", desired_count)
        desired_count = 1

    history_path = settings.output_dir / "history.json"
    used_topics = history.load_used_topics(history_path)
    logging.info("Loaded %d previously used topics", len(used_topics))

    topics = _select_topics(settings, explicit_topic, used_topics, desired_count)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = settings.output_dir / timestamp
    batch_dir.mkdir(parents=True, exist_ok=True)

    youtube_client = None
    if not dry_run:
        youtube_client = uploader.get_authenticated_service(
            settings.youtube_client_secrets_file, settings.youtube_token_file
        )

    video_paths: List[Path] = []
    for index, topic in enumerate(topics, start=1):
        video_dir = batch_dir / f"video_{index:02d}"
        logging.info("Producing video %d/%d for topic '%s'", index, len(topics), topic)
        video_path, script_lines = _render_video(topic, video_dir, settings)
        used_topics.add(topic)

        if dry_run:
            logging.info("Dry run enabled; skipping upload for topic '%s'.", topic)
        else:
            title = settings.video_title_template.format(topic=topic)
            description = settings.video_description_template.format(
                topic=topic, script=" ".join(script_lines)
            )
            tags = sorted(set(settings.tags + [topic]))

            logging.info("Uploading video %d/%d titled '%s'", index, len(topics), title)
            response = uploader.upload_video(
                youtube_client,
                video_path,
                title=title,
                description=description,
                tags=tags,
                category_id=settings.youtube_category_id,
                privacy_status=settings.youtube_privacy_status,
            )
            logging.info("YouTube response for '%s': %s", title, response)

        video_paths.append(video_path)

    history.save_used_topics(history_path, used_topics)
    logging.info("Recorded %d total topics to %s", len(used_topics), history_path)

    return video_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and upload a cartoon YouTube Short.")
    parser.add_argument("--config", type=Path, default=Path("config.json"), help="Path to the configuration JSON file.")
    parser.add_argument("--topic", type=str, help="Override the automatically selected trending topic.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate the video but skip uploading it to YouTube.",
    )
    parser.add_argument(
        "--count",
        type=int,
        help="Number of videos to generate and upload during this run.",
    )
    args = parser.parse_args()

    settings = config.load_settings(args.config)
    run(
        settings,
        explicit_topic=args.topic,
        dry_run=args.dry_run,
        count=args.count,
    )


if __name__ == "__main__":
    main()
