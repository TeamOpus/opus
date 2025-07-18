import re
import os
import httpx
import yt_dlp
from config import API_URL

COOKIES_FILE = "cookies/cookies.txt"

# Ensure downloads directory exists
os.makedirs("downloads", exist_ok=True)

YTDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "noplaylist": True,
    "quiet": True,
    "cookies": COOKIES_FILE,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192"
    }],
}

yt_regex = re.compile(
    r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w\-]{11})"
)


def extract_video_id(url: str) -> str | None:
    match = yt_regex.search(url)
    return match.group(1) if match else None


async def search(query: str) -> str:
    """Use yt-dlp to search YouTube and return the first video ID."""
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            return info["entries"][0]["id"]
    except Exception as e:
        raise Exception(f"Search failed via yt-dlp: {e}")


async def search_and_download(query: str) -> str:
    """Search YouTube and download the audio."""
    video_id = await search(query)
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return await download_from_yt(video_url)


async def download_from_yt(url: str) -> str:
    """Download the audio from a YouTube URL."""
    with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")


async def fallback_api_download(video_id: str) -> str:
    """Use your fallback API to download the file by video ID."""
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
    raise Exception("Fallback failed.")
