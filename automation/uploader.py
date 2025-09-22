"""Upload finished videos to YouTube using the Data API."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_authenticated_service(client_secret_file: Path, token_file: Path):
    """Authenticate against the YouTube Data API v3 and return a client."""

    creds: Optional[Credentials] = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_file), SCOPES)
            creds = flow.run_console()
        token_file.parent.mkdir(parents=True, exist_ok=True)
        with token_file.open("w", encoding="utf-8") as fp:
            fp.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_video(
    youtube,
    video_path: Path,
    title: str,
    description: str,
    tags: Iterable[str],
    category_id: str = "23",
    privacy_status: str = "private",
) -> dict:
    """Upload ``video_path`` with the supplied metadata."""

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": list(tags),
            "categoryId": category_id,
        },
        "status": {"privacyStatus": privacy_status},
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)

    try:
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")
        print("Upload complete.")
        return response
    except HttpError as exc:  # pragma: no cover - network dependent
        error_details = exc.content.decode("utf-8") if hasattr(exc, "content") else str(exc)
        raise RuntimeError(f"YouTube upload failed: {error_details}") from exc
