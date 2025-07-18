from OpusMusicBot.core.bot import app
from OpusMusicBot.core.userbot import userbot
from OpusMusicBot.core.call import Anony

from pyrogram import idle
import asyncio

async def run():
    await app.start()
    await userbot.start()
    await Anony.start()
    print("OpusMusicBot is up and running.")
    await idle()
    await app.stop()
    await userbot.stop()

if __name__ == "__main__":
    asyncio.run(run())
