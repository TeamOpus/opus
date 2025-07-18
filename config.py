import os

API_ID = int(os.getenv("API_ID", 12345))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

MONGO_URI = os.getenv("MONGO_URI", "your_mongo_uri")
STRING_SESSION = os.getenv("STRING_SESSION", "your_string_session")

SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "OpusSupport")
OWNER_ID = int(os.getenv("OWNER_ID", 123456789))

API_URL = "
