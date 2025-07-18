import re
import os
import logging
import yt_dlp
import httpx

from config import API_URL
from youtubesearchpython import VideosSearch

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory setup
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Cookie path
COOKIES_FILE = "cookies/cookies.txt"
USE_COOKIES = os.path.exists(COOKIES_FILE)

# YouTube video ID regex
yt_regex = re.compile(r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w\-]{11})")

# yt-dlp options
YTDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": f"{DOWNLOADS_DIR}/%(id)s.%(ext)s",
    "noplaylist": True,
    "quiet": True,
    "cookies": COOKIES_FILE if USE_COOKIES else None,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}


def extract_video_id(url: str) -> str | None:
    """Extract video ID from a YouTube URL."""
    match = yt_regex.search(url)
    return match.group(1) if match else None


async def search(query: str) -> str:
    """Search YouTube and return the first result's video ID."""
    try:
        results = VideosSearch(query, limit=1).result()
        if not results["result"]:
            raise ValueError("No results found")
        return results["result"][0]["id"]
    except Exception as e:
        logger.error(f"[search] Error: {e}")
        raise Exception(f"Search failed: {e}")


async def download_from_yt(url: str) -> str:
    """Download audio from a YouTube URL using yt-dlp."""
    try:
        with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_path = ydl.prepare_filename(info)
            mp3_path = raw_path.rsplit(".", 1)[0] + ".mp3"

            if not os.path.exists(mp3_path):
                raise FileNotFoundError(f"MP3 not found after download: {mp3_path}")
            return os.path.abspath(mp3_path)

    except Exception as e:
        logger.error(f"[yt-dlp] Failed to download: {e}")
        raise Exception(f"Download failed: {e}")


async def search_and_download(query: str) -> str:
    """Search YouTube and download the audio."""
    try:
        video_id = await search(query)
        return await download_from_yt(f"https://youtube.com/watch?v={video_id}")
    except Exception as e:
        logger.error(f"[search_and_download] Failed: {e}")
        raise


async def fallback_api_download(video_id: str) -> str:
    """Download using fallback API (Space.dev)."""
    try:
        api_url = f"{API_URL}?direct&id={video_id}"
        file_path = os.path.join(DOWNLOADS_DIR, f"{video_id}.mp3")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(api_url)
            if response.status_code != 200:
                raise Exception(f"Fallback API Error: {response.text}")

            with open(file_path, "wb") as f:
                f.write(response.content)

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Fallback file not saved: {file_path}")

            return os.path.abspath(file_path)

    except Exception as e:
        logger.error(f"[fallback_api_download] Failed for {video_id}: {e}")
        raise Exception(f"Fallback download failed: {e}")
