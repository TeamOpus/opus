from pyrogram import filters
from pyrogram.types import Message
from OpusMusicBot.core.bot import app
from OpusMusicBot.call import Anony
from OpusMusicBot.utils.db import get_mode, pop_queue, get_queue

@app.on_message(filters.command("skip") & filters.group)
async def skip_handler(client, message: Message):
    chat_id = message.chat.id
    mode = await get_mode(chat_id)

    if mode == "vc":
        next_song = await pop_queue(chat_id)
        if next_song:
            try:
                await Anony.change_stream(chat_id, next_song["file_path"])
                return await message.reply_text(f"⏭ Skipped to: `{next_song['title']}`")
            except Exception as e:
                return await message.reply_text(f"❌ Failed to skip: {e}")
        else:
            await Anony.leave_call(chat_id)
            return await message.reply_text("✅ Queue ended. Left VC.")
    else:
        next_song = await pop_queue(chat_id)
        if next_song:
            return await message.reply_text(f"⏭ Removed: `{next_song['title']}` from queue.")
        else:
            return await message.reply_text("❌ Queue is already empty.")
