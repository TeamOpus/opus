import re
import os
import logging
import yt_dlp
import aiohttp
from OpusMusicBot import app
from config import API_URL
from youtubesearchpython import VideosSearch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure downloads directory exists
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Cookie file
COOKIES_FILE = "cookies/cookies.txt"

# yt-dlp options
YTDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": f"{DOWNLOADS_DIR}/%(id)s.%(ext)s",
    "noplaylist": True,
    "quiet": True,
    "cookies": COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192"
    }],
}

# YouTube URL regex
yt_regex = re.compile(
    r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w\-]{11})"
)

def extract_video_id(url: str) -> str | None:
    """
    Extract YouTube video ID from a URL.
    """
    match = yt_regex.search(url)
    return match.group(1) if match else None

async def search(query: str) -> str:
    """
    Search YouTube for a video and return its video_id.
    """
    try:
        results = VideosSearch(query, limit=1).result()
        if not results["result"]:
            raise ValueError("No search results found")
        return results["result"][0]["id"]
    except Exception as e:
        logger.error(f"Search failed for query '{query}': {str(e)}")
        raise Exception(f"Failed to search YouTube: {str(e)}")

async def download_from_yt(url: str) -> str:
    """
    Download audio from a YouTube URL using yt-dlp.
    Returns the absolute path to the MP3 file.
    """
    try:
        # Validate cookies
        if not os.path.exists(COOKIES_FILE):
            logger.warning("Cookies file not found, proceeding without cookies")
            YTDL_OPTS["cookies"] = None

        with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            file_path = filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Downloaded file not found: {file_path}")
            return os.path.abspath(file_path)
    except Exception as e:
        logger.error(f"Download failed for URL '{url}': {str(e)}")
        raise Exception(f"Failed to download from YouTube: {str(e)}")

async def search_and_download(query: str) -> str:
    """
    Search YouTube for a video and download its audio.
    Returns the absolute path to the MP3 file.
    """
    try:
        video_id = await search(query)
        url = f"https://youtube.com/watch?v={video_id}"
        return await download_from_yt(url)
    except Exception as e:
        logger.error(f"Search and download failed for query '{query}': {str(e)}")
        raise Exception(f"Failed to search and download: {str(e)}")

async def fallback_api_download(video_id: str) -> str:
    """
    Download MP3 from Space.dev API as a fallback.
    Returns the absolute path to the MP3 file.
    """
    try:
        api_url = f"{API_URL}?direct&id={video_id}"
        file_name = f"{video_id}.mp3"
        file_path = os.path.abspath(os.path.join(DOWNLOADS_DIR, file_name))

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=30) as resp:
                if resp.status != 200:
                    raise Exception(f"Space.dev API error: {await resp.text()}")
                with open(file_path, "wb") as f:
                    async for chunk in resp.aiter_content():
                        f.write(chunk)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Downloaded file not found: {file_path}")
                return file_path
    except Exception as e:
        logger.error(f"Fallback download failed for video_id '{video_id}': {str(e)}")
        raise Exception(f"Failed to download from Space.dev: {str(e)}")
