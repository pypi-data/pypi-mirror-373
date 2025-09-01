import argparse
import platform
import subprocess
import sys
from typing import Dict, Optional, Union, Any

import anyio
from httpx import AsyncClient

from . import youtube

def _select_stream_interactive(videos: list[Dict[str, Any]]) -> Optional[Union[Dict[str, Any], str]]:
    for i, video in enumerate(videos, 1):
        bitrate_kbps = video["bitrate"] // 1000
        print(f"{i}) {video['quality']} ({bitrate_kbps} kbps)")

    audio_index = len(videos) + 1
    print(f"{audio_index}) Audio Only")

    try:
        raw_choice = input(f"Select quality [1-{audio_index}]: ")
        choice = int(raw_choice)
        if 1 <= choice <= len(videos):
            return videos[choice - 1]
        if choice == audio_index:
            return "audio"
    except (ValueError, KeyboardInterrupt):
        pass

    return None

def _find_quality_match(videos: list[Dict[str, Any]], quality_pref: str) -> Optional[Dict[str, Any]]:
    pref_lower = quality_pref.lower()
    return next((v for v in videos if pref_lower in v["quality"].lower()), videos[0] if videos else None)

def get_stream_selection(data: Dict[str, Any], quality_pref: Optional[str], audio_only: bool) -> Optional[Union[Dict[str, Any], str]]:
    if audio_only:
        return "audio"

    videos = data["videos"]
    if not videos:
        return "audio"

    if quality_pref:
        if quality_pref == "highest":
            return videos[0]
        if quality_pref == "lowest":
            return videos[-1]
        return _find_quality_match(videos, quality_pref)

    print(f"Available streams for: {data['title']}")
    return _select_stream_interactive(videos)

def get_mpv_executable_path() -> str:
    return "mpv.exe" if platform.system() == "Windows" else "mpv"

def launch_mpv(title: str, audio_url: str, video_url: Optional[str] = None) -> None:
    mpv_executable = get_mpv_executable_path()
    command = [mpv_executable, f"--title={title}", "--force-media-title= "]

    if video_url:
        command.extend([video_url, f"--audio-file={audio_url}"])
        print(f"Playing: {title} [video]")
    else:
        command.extend([audio_url, "--no-video"])
        print(f"Playing: {title} [audio only]")

    popen_kwargs = {}
    if platform.system() != "Windows":
        popen_kwargs["start_new_session"] = True

    try:
        subprocess.Popen(command, **popen_kwargs)
    except FileNotFoundError:
        print(f"Error: '{mpv_executable}' not found in PATH", file=sys.stderr)
        sys.exit(1)

def _get_identifier_from_input() -> str:
    try:
        return input("Enter YouTube URL or Video ID: ").strip()
    except KeyboardInterrupt:
        print("\nCancelled", file=sys.stderr)
        sys.exit(0)
    return ""

async def main() -> None:
    parser = argparse.ArgumentParser(description="Stream YouTube videos with mpv")
    parser.add_argument("identifier", nargs="?", help="YouTube URL or Video ID")
    parser.add_argument("-q", "--quality", help="Quality preference (e.g., 1080p, highest, lowest)")
    parser.add_argument("-a", "--audio", action="store_true", help="Audio only")

    args = parser.parse_args()

    identifier = args.identifier or _get_identifier_from_input()
    if not identifier:
        print("Error: No identifier provided", file=sys.stderr)
        sys.exit(1)

    video_id = youtube.extract_video_id(identifier)
    if not video_id:
        print("Error: Invalid YouTube URL or Video ID", file=sys.stderr)
        sys.exit(1)

    try:
        async with AsyncClient(timeout=30.0) as client:
            data = await youtube.get_player_data(video_id, client)
    except youtube.YouTubeApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    selected_stream = get_stream_selection(data, args.quality, args.audio)
    if not selected_stream:
        print("No stream selected", file=sys.stderr)
        sys.exit(1)

    audio_stream_url = data["audio"]["url"]
    if selected_stream == "audio":
        launch_mpv(data["title"], audio_stream_url)
    else:
        assert isinstance(selected_stream, dict)
        launch_mpv(data["title"], audio_stream_url, selected_stream["url"])

def run() -> None:
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        sys.exit(130)