import os
import warnings
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Environment variables with default fallback values
API_ID = int(os.getenv("API_ID", 12345))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
MONGO_URI = os.getenv("MONGO_URI", "your_mongo_uri")
STRING_SESSION = os.getenv("STRING_SESSION", "your_string_session")
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "BillaCore")
OWNER_ID = int(os.getenv("OWNER_ID", 5960968099))
API_URL = os.getenv("API_URL", None)

def check_env_vars():
    """Check if environment variables are set to non-default values and issue warnings if not."""
    default_values = {
        "API_ID": 12345,
        "API_HASH": "",
        "BOT_TOKEN": "",
        "MONGO_URI": "",
        "STRING_SESSION": "",
        "SUPPORT_CHAT": "BillaCore",
        "OWNER_ID": 5960968099,
        "API_URL": "None"
    }
    
    for var_name, default_value in default_values.items():
        current_value = globals()[var_name]
        if current_value == default_value:
            warnings.warn(
                f"Environment variable {var_name} is not set and is using default value: {default_value}. "
                "Please set the environment variable for proper configuration.",
                UserWarning
            )

# Run the check when the module is imported
check_env_vars()
