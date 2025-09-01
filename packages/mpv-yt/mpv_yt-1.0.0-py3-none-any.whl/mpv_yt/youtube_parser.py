from typing import Dict, List, Optional, Tuple, Any

ITAG_QUALITY_MAP = {
    160: "144p", 278: "144p", 330: "144p", 394: "144p", 694: "144p",
    133: "240p", 242: "240p", 331: "240p", 395: "240p", 695: "240p",
    134: "360p", 243: "360p", 332: "360p", 396: "360p", 696: "360p",
    135: "480p", 244: "480p", 333: "480p", 397: "480p", 697: "480p",
    136: "720p", 247: "720p", 298: "720p", 302: "720p", 334: "720p", 398: "720p", 698: "720p",
    137: "1080p", 299: "1080p", 248: "1080p", 303: "1080p", 335: "1080p", 399: "1080p", 699: "1080p",
    264: "1440p", 271: "1440p", 304: "1440p", 308: "1440p", 336: "1440p", 400: "1440p", 700: "1440p",
    266: "2160p", 305: "2160p", 313: "2160p", 315: "2160p", 337: "2160p", 401: "2160p", 701: "2160p",
    138: "4320p", 272: "4320p", 402: "4320p", 571: "4320p",
}

def parse_streams(streaming_data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    adaptive_formats = streaming_data.get("adaptiveFormats", [])
    if not isinstance(adaptive_formats, list):
        return [], None

    video_streams: Dict[str, Dict[str, Any]] = {}
    best_audio: Optional[Dict[str, Any]] = None
    best_audio_bitrate = -1

    for fmt in adaptive_formats:
        url = fmt.get("url")
        bitrate = fmt.get("bitrate")
        if not (url and bitrate and isinstance(fmt, dict)):
            continue

        mime_type = fmt.get("mimeType", "")
        is_video = "video/" in mime_type
        is_audio = "audio/" in mime_type

        if is_video:
            itag = fmt.get("itag")
            if not isinstance(itag, int):
                continue
            quality_label = ITAG_QUALITY_MAP.get(itag)
            if not quality_label:
                continue

            existing_stream = video_streams.get(quality_label)
            if not existing_stream or bitrate > existing_stream["bitrate"]:
                video_streams[quality_label] = {"quality": quality_label, "url": url, "bitrate": bitrate}

        elif is_audio and bitrate > best_audio_bitrate:
            best_audio = {"url": url, "bitrate": bitrate}
            best_audio_bitrate = bitrate

    sorted_videos = sorted(video_streams.values(), key=lambda x: x["bitrate"], reverse=True)
    return sorted_videos, best_audio