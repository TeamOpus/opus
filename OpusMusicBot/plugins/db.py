from pyrogram import Client, filters
from OpusMusicBot import app
from pymongo import MongoClient
from config import MONGO_URI

mongo = MongoClient(MONGO_URI)
db = mongo.OpusMusicBot

queue_col = db.queue
mode_col = db.mode
active_col = db.active

# 🔁 QUEUE SYSTEM

async def add_to_queue(chat_id: int, file_path: str, title: str):
    queue_col.insert_one({
        "chat_id": chat_id,
        "file_path": file_path,
        "title": title
    })

async def get_queue(chat_id: int):
    return list(queue_col.find({"chat_id": chat_id}).limit(100))

async def pop_queue(chat_id: int):
    item = queue_col.find_one({"chat_id": chat_id})
    if item:
        queue_col.delete_one({"_id": item["_id"]})
    return item

async def clear_queue(chat_id: int):
    queue_col.delete_many({"chat_id": chat_id})

# 📀 PLAY MODE SYSTEM

async def set_mode(chat_id: int, mode: str):
    mode_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"mode": mode}},
        upsert=True
    )

async def get_mode(chat_id: int) -> str:
    doc = mode_col.find_one({"chat_id": chat_id})
    return doc["mode"] if doc else "miniapp"  # default is mini app

# 🔊 ACTIVE CHATS (for VC cleanup etc.)

async def add_active_chat(chat_id: int):
    active_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"active": True}},
        upsert=True
    )

async def remove_active_chat(chat_id: int):
    active_col.delete_one({"chat_id": chat_id})

async def is_active_chat(chat_id: int) -> bool:
    return bool(active_col.find_one({"chat_id": chat_id}))
