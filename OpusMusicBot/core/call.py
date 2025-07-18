from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream.input_file import InputAudioStream
from pyrogram.types import Chat
from OpusMusicBot.core.userbot import userbot
from OpusMusicBot.utils.db import add_active_chat, remove_active_chat
import os

class MusicCall:
    def __init__(self):
        self.call = PyTgCalls(userbot)

    async def start(self):
        await self.call.start()

    async def join_call(self, chat_id: int, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found for VC stream")

        await self.call.join_group_call(
            chat_id,
            InputStream(
                InputAudioStream(
                    file_path,
                )
            )
        )
        await add_active_chat(chat_id)

    async def leave_call(self, chat_id: int):
        await self.call.leave_group_call(chat_id)
        await remove_active_chat(chat_id)

    async def change_stream(self, chat_id: int, file_path: str):
        await self.call.change_stream(
            chat_id,
            InputStream(
                InputAudioStream(
                    file_path,
                )
            )
        )

Anony = MusicCall()
