from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient
from pyrogram import Client

import config

TEMP_MONGODB = "mongodb+srv://strvortexcore:vortexcore0019@cluster0.fkb3o.mongodb.net/?retryWrites=true&w=majority"


if config.MONGO_DB_URI is None:
    LOGGER(__name__).warning(
        "ɴᴏ ᴍᴏɴɢᴏ ᴅʙ ᴜʀʟ ғᴏᴜɴᴅ.. ʏᴏᴜʀ ʙᴏᴛ ᴡɪʟʟ ᴡᴏʀᴋ ᴏɴ sʜᴜᴋʟᴀ  ᴍᴜsɪᴄ ᴅᴀᴛᴀʙᴀsᴇ"
    )
    temp_client = Client(
        "OpusMusicBot",
        bot_token=config.BOT_TOKEN,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
    )
    temp_client.start()
    info = temp_client.get_me()
    username = info.username
    temp_client.stop()
    _mongo_async_ = _mongo_client_(TEMP_MONGODB)
    _mongo_sync_ = MongoClient(TEMP_MONGODB)
    mongodb = _mongo_async_[username]
    pymongodb = _mongo_sync_[username]
else:
    _mongo_async_ = _mongo_client_(config.MONGO_URI)
    _mongo_sync_ = MongoClient(config.MONGO_URI)
    mongodb = _mongo_async_.OpusMusicBot
    pymongodb = _mongo_sync_.OpusMusicBot
