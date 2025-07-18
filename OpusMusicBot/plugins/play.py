import os
import asyncio
import re
import aiohttp

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from OpusMusicBot.core.bot import app
from OpusMusicBot.core.call import Anony
from OpusMusicBot import yt
from OpusMusicBot.utils.db import get_mode, set_mode, get_queue
from config import WEB_URL


def extract_video_id(query: str) -> str:
    """
    Extract YouTube video ID from a URL or search query.
    """
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)",
        r"(?:https?:\/\/)?youtu\.be\/([^?]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            return match.group(1)
    
    try:
        video_id = asyncio.run(yt.search(query))  # yt.search should return video_id
        return video_id
    except Exception:
        raise ValueError("Could not extract video ID from query")


@app.on_message(filters.command("play") & filters.group)
async def play_handler(client, message: Message):
    chat_id = message.chat.id
    user = message.from_user.first_name

    if len(message.command) < 2:
        return await message.reply_text("🎵 Send the song name or YouTube link.\n\nUsage: `/play despacito`", quote=True)

    query = " ".join(message.command[1:])
    mode = await get_mode(chat_id)

    if not mode:
        buttons = [
            [
                InlineKeyboardButton("🎧 Mini App", callback_data=f"setmode_{chat_id}_miniapp"),
                InlineKeyboardButton("📺 Video Chat", callback_data=f"setmode_{chat_id}_vc")
            ]
        ]
        return await message.reply_text(
            "Choose default play mode for this group:",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )

    msg = await message.reply_text("🔎 Processing...", quote=True)

    if mode == "vc":
        try:
            if "youtube.com" in query or "youtu.be" in query:
                file_path = await yt.download_from_yt(query)
            else:
                file_path = await yt.search_and_download(query)

            title = os.path.basename(file_path)

            if not file_path.lower().endswith(('.mp3', '.wav', '.ogg')):
                raise ValueError(f"Unsupported audio format for file: {file_path}")

            await Anony.join_call(chat_id, file_path)
            await msg.edit(f"✅ Now playing via **Video Chat**:\n`{title}`")
        except Exception as e:
            await msg.edit(f"❌ VC Error: {str(e)}")

    else:
        try:
            video_id = extract_video_id(query)
            if not WEB_URL:
                raise ValueError("Mini App not configured")

            async with aiohttp.ClientSession() as session:
                async with session.post(f"{WEB_URL}/api/add/{chat_id}", json={"video_id": video_id}) as resp:
                    if resp.status != 200:
                        raise ValueError(f"Failed to add to Mini App queue: {await resp.text()}")
                    data = await resp.json()

            queue = await get_queue(chat_id)
            pos = len(queue)
            mini_app_url = f"{WEB_URL}/group/{chat_id}"

            await msg.edit(
                f"✅ Added to **Mini App** queue at position `{pos}`:\n"
                f"`{data.get('title', 'Unknown')}`\n"
                f"🎧 [Open Player]({mini_app_url})"
            )
        except Exception as e:
            await msg.edit(f"❌ Mini App Error: {str(e)}")


@app.on_callback_query(filters.regex(r"^setmode_(\-?\d+)_(miniapp|vc)$"))
async def set_mode_callback(client, cq: CallbackQuery):
    chat_id, mode = cq.data.split("_")[1:]
    await set_mode(int(chat_id), mode)
    await cq.answer(f"Mode set to: {mode.upper()}")
    await cq.edit_message_text(
        f"✅ Default mode for this group is **{mode.upper()}**.\nSend `/play` again."
    )
