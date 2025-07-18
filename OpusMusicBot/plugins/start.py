from pyrogram import Client, filters
from OpusMusicBot import app

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("OpusMusicBot is alive!")
