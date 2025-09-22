# Cartoon Shorts Automation

This project automates the creation and upload of daily, trending, cartoon-style
YouTube Shorts. It stitches together three core steps:

1. Grab a trending topic from Google Trends.
2. Generate a light-hearted script, narration, and colourful cartoon slides.
3. Render the final 9:16 video and optionally upload it to your YouTube channel
   using the YouTube Data API v3.

Everything is built with free Python tooling so you can run the pipeline locally
or on a small server without paying for external services.

## Features

- Fetch trending topics for a configurable region via `pytrends`.
- Automatic script generation with playful punchlines.
- Cartoon-ish slides built with Pillow, including optional custom fonts.
- Text-to-speech narration through the offline-friendly `pyttsx3` engine.
- Video assembly with `moviepy` producing Shorts-ready MP4 files.
- One-click upload to YouTube once you supply OAuth credentials.
- Topic history tracking so you always post something fresh.
- Batch-friendly runs that can render and upload four or more Shorts in one go.

## Getting Started

### 1. Install system dependencies

`pyttsx3` needs a speech engine. On Linux install `espeak` (or
`espeak-ng`). On macOS it uses the system voices, and on Windows SAPI5
is available by default.

```bash
# Ubuntu / Debian
sudo apt-get update && sudo apt-get install -y espeak
```

Make sure `ffmpeg` is also installed because `moviepy` relies on it for
video encoding.

```bash
sudo apt-get install -y ffmpeg
```

### 2. Create a virtual environment & install Python packages

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure the automation

Copy `config.sample.json` to `config.json` and adjust it to suit your
channel. The most important values are the Google OAuth files and your
preferred output directories.

```bash
cp config.sample.json config.json
```

Each configuration field is documented inline, but here is a quick
reference:

- `trending_region` – region code accepted by `pytrends` (e.g. `united_states`, `india`).
- `videos_per_day` – how many Shorts to render/upload each time you trigger the automation.
- `output_dir` – location where rendered videos and logs will be written.
- `assets_dir` – folder that may contain custom fonts (`cartoon.ttf`) or background music.
- `youtube_client_secrets_file` – OAuth client secrets downloaded from Google Cloud.
- `youtube_token_file` – token cache generated after the first authentication.
- `video_title_template` / `video_description_template` – format strings that receive the `{topic}` and `{script}`.
- `background_music_file` – optional MP3/M4A that plays quietly under the narration.

### 4. Enable the YouTube Data API

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the YouTube Data API v3.
3. Configure an OAuth 2.0 Client ID (Desktop type works best).
4. Download the JSON secrets file and place it where `youtube_client_secrets_file`
   points (e.g. `credentials/client_secret.json`).

When you run the automation for the first time it will open a browser or
prompt you with a URL to authorise access. The resulting token is stored
in `youtube_token_file` so subsequent runs are unattended.

## Running the automation

By default the script honours the `videos_per_day` value in your
configuration (set to 4 in `config.sample.json`). Trigger the full
pipeline with:

```bash
python -m automation.main --config config.json
```

You can temporarily override the batch size by supplying `--count`.
For example, to publish five Shorts in one run:

```bash
python -m automation.main --config config.json --count 5
```

Use `--dry-run` to generate the videos without uploading them (helpful
while testing):

```bash
python -m automation.main --config config.json --dry-run
```

You can also override the topic manually:

```bash
python -m automation.main --config config.json --topic "Space Tourism"
```

The script writes each run to a timestamped folder inside
`output_dir`, storing the frames, audio snippets, and the final
`cartoon_short.mp4`. The file is ready to be posted as a YouTube Short.

## Scheduling daily uploads

- **Linux/macOS** – use `cron` to run the command once per day.
- **Windows** – add a task to the Task Scheduler that executes the
  virtual environment's Python with `-m automation.main`.

Remember that the machine must stay online during the scheduled time and
that Google OAuth tokens occasionally expire, so check the logs
periodically.

## Assets

Place optional supporting files in the folder referenced by
`assets_dir`:

- `cartoon.ttf` – a fun display font used for the slides (falls back to
  DejaVu Sans if missing).
- `background_music.mp3` – soft music loop used as background audio (set
  the path in `config.json`).

## Limitations & tips

- Trending data depends on Google's availability; the script falls back
  to a stock topic if the API fails.
- Text-to-speech quality varies by platform. Feel free to plug in a
  different engine if you have access to one.
- Review the generated videos before posting to ensure they align with
  your channel's style and community guidelines.
- Keep an eye on YouTube's policies; automated uploads must still follow
  their rules.

Enjoy automating your cartoon Shorts pipeline!
