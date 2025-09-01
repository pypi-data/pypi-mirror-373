import re
from typing import Any, Dict, Optional, Tuple
from functools import lru_cache
from httpx import AsyncClient, Response
import orjson

from . import youtube_parser

class YouTubeApiError(Exception):
    __slots__ = ()

_VIDEO_ID_PATTERN = re.compile(r"(?:v=|youtu\.be/|/shorts/|/embed/|/live/|/v/)([a-zA-Z0-9_-]{11})")
_VALID_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")

_API_ENDPOINT = "https://www.youtube.com/youtubei/v1/player"
_CLIENT_CONFIGS = {
    "android": {"name": "ANDROID", "version": "19.50.42", "id": "3"},
    "ios": {"name": "IOS", "version": "17.13.3", "id": "5", "device_model": "iPhone14,3"}
}

_ERROR_LOGIN_REQUIRED = "LOGIN_REQUIRED"
_ERROR_UNPLAYABLE = "UNPLAYABLE"
_ERROR_LIVE_STREAM = "Live streams are not supported"
_ERROR_NO_AUDIO = "No audio stream available"
_ERROR_INCOMPLETE_DATA = "Incomplete video data received from API"

@lru_cache(maxsize=128)
def extract_video_id(identifier: str) -> Optional[str]:
    if not identifier:
        return None
    if _VALID_ID_PATTERN.fullmatch(identifier):
        return identifier
    match = _VIDEO_ID_PATTERN.search(identifier)
    return match.group(1) if match else None

def _create_request_context(video_id: str, client_type: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    config = _CLIENT_CONFIGS[client_type]
    payload = {
        "context": {
            "client": {
                "hl": "en",
                "gl": "US",
                "clientName": config["name"],
                "clientVersion": config["version"]
            },
            "user": {"lockedSafetyMode": False}
        },
        "videoId": video_id,
        "contentCheckOk": True,
        "racyCheckOk": True
    }
    if "device_model" in config:
        payload["context"]["client"]["deviceModel"] = config["device_model"]
    headers = {
        "Content-Type": "application/json",
        "X-Youtube-Client-Name": config["id"],
        "X-Youtube-Client-Version": config["version"]
    }
    return payload, headers

async def _attempt_extraction(video_id: str, client: AsyncClient, client_type: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    payload, headers = _create_request_context(video_id, client_type)
    try:
        response = await client.post(_API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        data = orjson.loads(response.content)
    except Exception as e:
        return None, str(e)

    playability = data.get("playabilityStatus", {})
    status = playability.get("status")

    if status == _ERROR_LOGIN_REQUIRED:
        return None, _ERROR_LOGIN_REQUIRED
    if status != "OK":
        return None, playability.get("reason", _ERROR_UNPLAYABLE)

    video_details = data.get("videoDetails", {})
    streaming_data = data.get("streamingData")

    if not (streaming_data and video_details.get("title")):
        return None, _ERROR_INCOMPLETE_DATA
    if video_details.get("isLiveContent"):
        return None, _ERROR_LIVE_STREAM

    videos, audio = youtube_parser.parse_streams(streaming_data)
    if not audio:
        return None, _ERROR_NO_AUDIO

    return {"title": video_details["title"].strip(), "videos": videos, "audio": audio}, None

async def get_player_data(video_id: str, client: AsyncClient) -> Dict[str, Any]:
    data, error = await _attempt_extraction(video_id, client, "android")
    if data:
        return data

    is_login_or_age_error = error and (_ERROR_LOGIN_REQUIRED in error or "age" in error.lower())
    if is_login_or_age_error:
        data, error = await _attempt_extraction(video_id, client, "ios")
        if data:
            return data

    raise YouTubeApiError(error or "An unknown error occurred")