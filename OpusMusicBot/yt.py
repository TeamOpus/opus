import os
import re
import httpx
import yt_dlp
from typing import Union
from youtubesearchpython.__future__ import VideosSearch

# Ensure download directory exists
os.makedirs("downloads", exist_ok=True)

# Cookie path
COOKIES_FILE = "cookies/cookies.txt"

# yt-dlp options with geo-bypass
YTDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "noplaylist": True,
    "quiet": True,
    "cookies": COOKIES_FILE,
    "geo_bypass": True,
    "geo_bypass_country": "IN",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192"
    }],
}

# Regex to extract YouTube video ID
yt_regex = re.compile(r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w\-]{11})")


def extract_video_id(url: str) -> str | None:
    match = yt_regex.search(url)
    return match.group(1) if match else None


def time_to_seconds(time_str: str) -> int:
    parts = list(map(int, time_str.split(":")))
    return sum(x * 60**i for i, x in enumerate(reversed(parts)))


async def search(query: str) -> str:
    """Search YouTube using yt-dlp and return video ID."""
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "geo_bypass": True, "cookies": COOKIES_FILE}) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            return info["entries"][0]["id"]
    except Exception as e:
        raise Exception(f"Search failed via yt-dlp: {e}")


async def search_and_download(query: str) -> str:
    """Search YouTube and download audio."""
    video_id = await search(query)
    url = f"https://www.youtube.com/watch?v={video_id}"
    return await download_from_yt(url)


async def download_from_yt(url: str) -> str:
    """Download audio from YouTube URL using yt-dlp."""
    with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")


async def fallback_api_download(video_id: str) -> str:
    """Fallback to custom API to download MP3 if yt-dlp fails."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}?direct&id={video_id}", timeout=30)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == 200:
                url = data["data"]["url"]
                filename = f"downloads/{video_id}.mp3"
                async with client.stream("GET", url) as resp:
                    with open(filename, "wb") as f:
                        async for chunk in resp.aiter_bytes():
                            f.write(chunk)
                return filename
    raise Exception("Fallback failed")


async def details(query: str, videoid: Union[bool, str] = None):
    """
    Get video details: title, duration (min/sec), thumbnail, video_id
    """
    if videoid:
        query = f"https://www.youtube.com/watch?v={query}"
    if "&" in query:
        query = query.split("&")[0]

    try:
        results = VideosSearch(query, limit=1)
        res = await results.next()

        for result in res.get("result", []):
            title = result.get("title")
            duration_min = result.get("duration") or "0:00"
            thumbnail = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
            vidid = result.get("id")

            duration_sec = time_to_seconds(duration_min) if duration_min else 0

            return title, duration_min, duration_sec, thumbnail, vidid

    except Exception as e:
        raise Exception(f"Details fetch failed: {e}")
