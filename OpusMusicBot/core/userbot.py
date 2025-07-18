from pyrogram import Client
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, STRING_SESSION

userbot = Client(
    name="userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
    parse_mode=ParseMode.HTML,
    no_updates=True,
)
