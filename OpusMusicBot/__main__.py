import asyncio
import importlib
import signal
import sys
import logging
import os
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

# List of plugin modules
ALL_MODULES = []
# Dynamically discover plugins if directory exists
plugins_dir = os.path.join(os.path.dirname(__file__), "OpusMusicBot/plugins")
if os.path.exists(plugins_dir):
    ALL_MODULES = [
        module[:-3] for module in os.listdir(plugins_dir)
        if module.endswith(".py") and module != "__init__.py"
    ]

async def run():
    # Load plugins if available
    if ALL_MODULES:
        for module in ALL_MODULES:
            try:
                importlib.import_module(f"OpusMusicBot.plugins.{module}")
                logger.info(f"Imported plugin: {module}")
            except Exception as e:
                logger.error(f"Failed to import plugin {module}: {str(e)}")
        logger.info(f"Successfully imported {len(ALL_MODULES)} plugin(s) from OpusMusicBot.plugins")
    else:
        logger.info("No plugins found in OpusMusicBot/plugins. Skipping plugin loading.")

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
