from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# Initialize the Pyrogram Client
app = Client(
    "OpusMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=20,
    plugins=dict(root="OpusMusicBot.plugins")  # Plugins loaded as before
)

# Dynamically import utils (optional, if you want to load them dynamically)
import importlib
utils_module = importlib.import_module("OpusMusicBot.utils")
