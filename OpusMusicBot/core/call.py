from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream.input_file import InputAudioStream
from pytgcalls.exceptions import GroupCallNotFound, NoActiveGroupCall
from OpusMusicBot.core.userbot import userbot
from OpusMusicBot.utils.db import add_active_chat, remove_active_chat
import os
import asyncio

class MusicCall:
    def __init__(self):
        """Initialize the PyTgCalls client with the userbot."""
        self.call = PyTgCalls(userbot)

    async def start(self):
        """Start the PyTgCalls client."""
        try:
            await self.call.start()
        except Exception as e:
            raise RuntimeError(f"Failed to start PyTgCalls: {str(e)}")

    async def join_call(self, chat_id: int, file_path: str):
        """
        Join a group call and start streaming an audio file.

        Args:
            chat_id (int): The Telegram chat ID of the group call.
            file_path (str): Path to the audio file to stream.

        Raises:
            FileNotFoundError: If the audio file does not exist.
            RuntimeError: If joining the group call fails.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Optional: Validate file format
        if not file_path.lower().endswith(('.mp3', '.wav', '.ogg')):
            raise ValueError(f"Unsupported audio format for file: {file_path}")

        try:
            await self.call.join_group_call(
                chat_id,
                InputStream(
                    InputAudioStream(file_path)
                )
            )
            add_active_chat(chat_id)
        except (GroupCallNotFound, NoActiveGroupCall) as e:
            raise RuntimeError(f"Failed to join group call: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error joining group call: {str(e)}")

    async def leave_call(self, chat_id: int):
        """
        Leave a group call and remove the chat from active chats.

        Args:
            chat_id (int): The Telegram chat ID of the group call.

        Raises:
            RuntimeError: If leaving the group call fails.
        """
        try:
            await self.call.leave_group_call(chat_id)
            remove_active_chat(chat_id)
        except (GroupCallNotFound, NoActiveGroupCall) as e:
            raise RuntimeError(f"Failed to leave group call: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error leaving group call: {str(e)}")

    async def change_stream(self, chat_id: int, file_path: str):
        """
        Change the current audio stream to a new file.

        Args:
            chat_id (int): The Telegram chat ID of the group call.
            file_path (str): Path to the new audio file to stream.

        Raises:
            FileNotFoundError: If the audio file does not exist.
            RuntimeError: If changing the stream fails.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        if not file_path.lower().endswith(('.mp3', '.wav', '.ogg')):
            raise ValueError(f"Unsupported audio format for file: {file_path}")

        try:
            await self.call.change_stream(
                chat_id,
                InputStream(
                    InputAudioStream(file_path)
                )
            )
        except (GroupCallNotFound, NoActiveGroupCall) as e:
            raise RuntimeError(f"Failed to change stream: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error changing stream: {str(e)}")

    async def skip_stream(self, chat_id: int, next_file_path: str):
        """
        Skip the current track and play the next one.

        Args:
            chat_id (int): The Telegram chat ID of the group call.
            next_file_path (str): Path to the next audio file to stream.

        Raises:
            FileNotFoundError: If the next audio file does not exist.
            RuntimeError: If skipping the stream fails.
        """
        # Delegate to change_stream (assuming queue logic is handled externally)
        await self.change_stream(chat_id, next_file_path)

# Global instance
Anony = MusicCall()
