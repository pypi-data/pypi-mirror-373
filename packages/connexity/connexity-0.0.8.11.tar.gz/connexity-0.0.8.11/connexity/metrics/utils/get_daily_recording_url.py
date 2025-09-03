import requests
from typing import Optional, Tuple
from urllib.parse import urlparse

API_BASE = "https://api.daily.co/v1"


def _extract_room_name(room_url: str) -> str:
    """
    Extract the room name from a Daily room URL:
      https://<subdomain>.daily.co/<room_name>[...]
    """
    path = urlparse(room_url).path.rstrip("/")
    if not path or "/" not in path:
        return ""
    return path.rsplit("/", 1)[-1]


def get_daily_recording_url(
    api_key: str,
    room_url: str,
) -> Optional[str, Optional[int]]:
    """
    Return (download_url, duration_seconds) for the most recent Daily.co cloud recording
    in the given room.

    Args:
        api_key: Daily REST API key (Bearer token).
        room_url: Full room URL (e.g., "https://your-domain.daily.co/test-room").

    Returns:
        (download_url, duration) or None if nothing found.
    """
    if not api_key:
        return None, None

    headers = {"Authorization": f"Bearer {api_key}"}
    room_name = _extract_room_name(room_url)
    if not room_name:
        return None, None

    # 1) Get the most recent recording for this room
    resp = requests.get(
        f"{API_BASE}/recordings",
        headers=headers,
        params={"room_name": room_name, "limit": 1},
        timeout=15,
    )
    resp.raise_for_status()
    items = resp.json().get("data") or []
    if not items:
        return None, None

    latest = items[0]
    rec_id = latest.get("id") or latest.get("recording_id")
    duration = latest.get("duration")
    if not rec_id:
        return None, duration

    # 2) Request a signed link with a custom expiry
    link_resp = requests.get(
        f"{API_BASE}/recordings/{rec_id}/access-link",
        headers=headers,
        timeout=15,
    )
    link_resp.raise_for_status()
    link_payload = link_resp.json()

    url = link_payload.get("link") or link_payload.get("download_link")
    return url, duration
