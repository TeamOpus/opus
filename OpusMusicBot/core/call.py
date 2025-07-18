import asyncio
import os
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, AudioQuality
from pytgcalls.exceptions import NoActiveGroupCall, AlreadyJoinedError
from pyrogram import Client
from OpusMusicBot.core.userbot import userbot
from OpusMusicBot.utils.db import add_active_chat, remove_active_chat

class MusicCall:
    def __init__(self):
        """Initialize PyTgCalls with userbot client."""
        self.client = Client(
            name="MusicBot",
            api_id=os.getenv("API_ID"),  # Ensure API_ID is set in .env
            api_hash=os.getenv("API_HASH"),  # Ensure API_HASH is set in .env
            session_string=os.getenv("STRING_SESSION"),  # Ensure STRING_SESSION is set in .env
        )
        self.call = PyTgCalls(self.client)

    async def start(self):
        """Start the PyTgCalls client."""
        try:
            await self.call.start()
            print("PyTgCalls client started successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to start PyTgCalls: {str(e)}")

    async def join_call(self, chat_id: int, file_path: str):
        """Join a group call and start streaming an audio file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        if not file_path.lower().endswith(('.mp3', '.wav', '.ogg')):
            raise ValueError(f"Unsupported audio format for file: {file_path}")

        try:
            stream = MediaStream(
                file_path,
                audio_parameters=AudioQuality.STUDIO,
            )
            await self.call.join_group_call(chat_id, stream)
            add_active_chat(chat_id)
            print(f"Joined group call in chat {chat_id} with file {file_path}")
        except NoActiveGroupCall:
            raise RuntimeError("No active group call found.")
        except AlreadyJoinedError:
            raise RuntimeError("Already joined a group call.")
        except Exception as e:
            raise RuntimeError(f"Unexpected error joining group call: {str(e)}")

    async def leave_call(self, chat_id: int):
        """Leave a group call and clean up."""
        try:
            await self.call.leave_group_call(chat_id)
            remove_active_chat(chat_id)
            print(f"Left group call in chat {chat_id}")
        except NoActiveGroupCall:
            raise RuntimeError("No active group call to leave.")
        except Exception as e:
            raise RuntimeError(f"Unexpected error leaving group call: {str(e)}")

    async def change_stream(self, chat_id: int, file_path: str):
        """Change the current stream to another file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        if not file_path.lower().endswith(('.mp3', '.wav', '.ogg')):
            raise ValueError(f"Unsupported audio format for file: {file_path}")

        try:
            stream = MediaStream(
                file_path,
                audio_parameters=AudioQuality.STUDIO,
            )
            await self.call.change_stream(chat_id, stream)
            print(f"Changed stream in chat {chat_id} to {file_path}")
        except NoActiveGroupCall:
            raise RuntimeError("No active group call to change stream.")
        except Exception as e:
            raise RuntimeError(f"Unexpected error changing stream: {str(e)}")

    async def skip_stream(self, chat_id: int, next_file_path: str):
        """Skip current audio and stream the next track."""
        await self.change_stream(chat_id, next_file_path)

# Global instance
Anony = MusicCall()
