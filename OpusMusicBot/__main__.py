import asyncio
import importlib
import signal
import sys
import logging
from pyrogram import idle
from OpusMusicBot.core.bot import app
from OpusMusicBot.core.userbot import userbot
from OpusMusicBot.core.call import Anony

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# List of plugin modules (adjust based on your plugins directory)
ALL_MODULES = [
    # Add your plugin module names here, e.g., "music", "admin", "help"
    # Or dynamically discover them:
]
# Optional: Dynamically discover plugins
import os
plugins_dir = os.path.join(os.path.dirname(__file__), "OpusMusicBot/plugins")
ALL_MODULES = [
    module[:-3] for module in os.listdir(plugins_dir)
    if module.endswith(".py") and module != "__init__.py"
]

async def run():
    # Load plugins
    for module in ALL_MODULES:
        importlib.import_module(f"OpusMusicBot.plugins.{module}")
    logger.info(f"Successfully imported {len(ALL_MODULES)} plugin(s) from OpusMusicBot.plugins")

    await app.start()
    await userbot.start()
    await Anony.start()
    logger.info("OpusMusicBot is up and running.")
    await idle()
    await app.stop()
    await userbot.stop()

def handle_shutdown(loop):
    logger.info("Stop signal received (SIGINT or SIGTERM). Exiting...")
    tasks = [task for task in asyncio.all_tasks(loop) if task is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.run_until_complete(app.stop())
    loop.run_until_complete(userbot.stop())
    loop.close()
    sys.exit(0)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # Set up signal handlers for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_shutdown, loop)
    try:
        loop.run_until_complete(run())
    except asyncio.CancelledError:
        pass  # Handle cancellation from SIGINT
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        if not loop.is_closed():
            loop.run_until_complete(app.stop())
            loop.run_until_complete(userbot.stop())
            loop.close()
