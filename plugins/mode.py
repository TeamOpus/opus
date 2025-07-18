from pyrogram import filters
from pyrogram.types import Message
from OpusMusicBot.core.bot import app
from OpusMusicBot.utils.db import set_mode

@app.on_message(filters.command("mode") & filters.group)
async def mode_handler(client, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("Use: `/mode miniapp` or `/mode vc`")

    mode = message.command[1].lower()
    if mode not in ["vc", "miniapp"]:
        return await message.reply_text("❌ Invalid mode. Use `vc` or `miniapp`")

    await set_mode(message.chat.id, mode)
    await message.reply_text(f"✅ Mode changed to **{mode.upper()}**")
