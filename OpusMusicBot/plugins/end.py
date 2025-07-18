from pyrogram import filters
from pyrogram.types import Message
from OpusMusicBot.core.bot import app
from OpusMusicBot.core.call import Anony
from OpusMusicBot.utils.db import get_mode, clear_queue

@app.on_message(filters.command("end") & filters.group)
async def end_handler(client, message: Message):
    chat_id = message.chat.id
    mode = await get_mode(chat_id)

    await clear_queue(chat_id)
    if mode == "vc":
        try:
            await Anony.leave_call(chat_id)
        except:
            pass
        return await message.reply_text("🛑 VC session ended and queue cleared.")
    else:
        return await message.reply_text("🗑 Mini App queue cleared.")
