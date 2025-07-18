import re
import os
from OpusMusicBot import app
import httpx
from config import API_URL
import yt_dlp

API_URL = "f{API_URL}?direct&id="
COOKIES_FILE = "cookies/cookies.txt"

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

async def search_and_download(query: str) -> str:
    from youtubesearchpython import VideosSearch

    results = VideosSearch(query, limit=1).result()
    if not results["result"]:
        raise Exception("No search results.")

    video_url = results["result"][0]["link"]
    return await download_from_yt(video_url)

async def download_from_yt(url: str) -> str:
    with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")

async def fallback_api_download(video_id: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(API_URL + video_id, timeout=30)
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
