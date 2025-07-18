import os
import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from OpusMusicBot.core.bot import app
from OpusMusicBot.core.call import Anony
from OpusMusicBot import yt
from OpusMusicBot.utils.db import get_mode, set_mode, add_to_queue, get_queue, pop_queue


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
            "**Choose default play mode for this group:**",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )

    msg = await message.reply_text("🔎 Searching...", quote=True)

    try:
        file_path = await yt.download_from_yt(query) if "youtube.com" in query or "youtu.be" in query else await yt.search_and_download(query)
        title = os.path.basename(file_path)
        # Validate file format to align with call.py
        if not file_path.lower().endswith(('.mp3', '.wav', '.ogg')):
            raise ValueError(f"Unsupported audio format for file: {file_path}")
    except Exception as e:
        return await msg.edit(f"❌ Failed to download: `{str(e)}`")

    if mode == "vc":
        try:
            await Anony.join_call(chat_id, file_path)
            await msg.edit(f"✅ Now playing via **Video Chat**:\n`{title}`")
        except Exception as e:
            await msg.edit(f"❌ VC Error: {str(e)}")
    else:
        await add_to_queue(chat_id, file_path, title)
        queue = await get_queue(chat_id)
        pos = len(queue)
        await msg.edit(f"✅ Added to Mini App queue at position `{pos}`:\n`{title}`")


@app.on_message(filters.command("skip") & filters.group)
async def skip_handler(client, message: Message):
    chat_id = message.chat.id
    mode = await get_mode(chat_id)

    if not mode:
        return await message.reply_text("🎵 No playback mode set. Use /play first.", quote=True)

    queue = await get_queue(chat_id)
    if not queue:
        return await message.reply_text("🎵 Queue is empty. Nothing to skip.", quote=True)

    msg = await message.reply_text("⏭ Skipping...", quote=True)

    try:
        # Pop the current song
        await pop_queue(chat_id)
        queue = await get_queue(chat_id)

        if not queue:
            # No more songs in queue, leave the call
            await Anony.leave_call(chat_id)
            await msg.edit("✅ Queue is empty. Left the call.")
            return

        # Play the next song
        file_path, title = queue[0]
        # Validate file format to align with call.py
        if not file_path.lower().endswith(('.mp3', '.wav', '.ogg')):
            raise ValueError(f"Unsupported audio format for file: {file_path}")
        await Anony.skip_stream(chat_id, file_path)
        await msg.edit(f"✅ Skipped to:\n`{title}`")
    except Exception as e:
        await msg.edit(f"❌ Skip error: {str(e)}")


@app.on_callback_query(filters.regex(r"^setmode_(\-?\d+)_(miniapp|vc)$"))
async def set_mode_callback(client, cq: CallbackQuery):
    chat_id, mode = cq.data.split("_")[1:]
    await set_mode(int(chat_id), mode)
    await cq.answer(f"Mode set to: {mode.upper()}")
    await cq.edit_message_text(f"✅ Default mode for this group is **{mode.upper()}**.\nSend /play again.")
