import asyncio
import os
import logging

from aiogram import Dispatcher, Bot
from aiogram.types import (
    Message,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
    URLInputFile,
)
from aiogram.filters import Command

from bots.config import load_tg_config
from bots.common.attachments import BaseAttachmentsProvider
from bots.common.content import FullMessageContent, MessageAttachment


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

config = load_tg_config(os.getenv("BOTS_CONFIG_PATH"))

dp = Dispatcher()

bot = Bot(token=config.token)


class AiogramAttachmentsProvider(BaseAttachmentsProvider):
    @staticmethod
    # TODO add videos support
    def provide_media(attachments: list[MessageAttachment]):
        media = []
        for at in attachments:
            if at.type == "photo":
                media.append(InputMediaPhoto(media=URLInputFile(url=at.url)))
            if at.type == "video":
                media.append(
                    InputMediaVideo(
                        media=URLInputFile(url=at.url, filename=at.title)
                    )
                )
        return media

    @staticmethod
    def provide_documents(attachments: list[MessageAttachment]):
        documents = []
        for at in attachments:
            if at.type == "doc":
                documents.append(
                    InputMediaDocument(
                        media=URLInputFile(url=at.url, filename=at.title)
                    )
                )
        return documents


class BotCommands:
    def __init__(self, bot, chat_id, attachments_provider):
        self.bot = bot
        self.chat_id = chat_id
        self.attachments_provider = attachments_provider

    async def send_messages(self, message_content: FullMessageContent):
        # basically you want to have this behaviour:
        # text-only: paste text
        # attachment-with-text: use text as caption to attachment

        message_text = message_content.text
        media = self.attachments_provider.provide_media(
            message_content.attachments
        )
        documents = self.attachments_provider.provide_documents(
            message_content.attachments
        )

        if not (media or documents):  # that was text based message
            await bot.send_message(self.chat_id, message_text)
        else:
            if media:
                media[0].caption = message_text
                await bot.send_media_group(self.chat_id, media=media)
            if documents:
                documents[0].caption = message_text
                await bot.send_media_group(self.chat_id, media=documents)


bot_commands = BotCommands(bot, config.chat_id, AiogramAttachmentsProvider())


@dp.message()
async def ping(message: Message):
    print(message.photo)
    await message.reply("hello")


async def check_queue(queue):
    while True:
        message_content = await queue.get()
        await bot_commands.send_messages(message_content)


async def main(my_posts, ds_posts, vk_posts):
    logger.info("starting the application")
    t1 = asyncio.create_task(check_queue(my_posts))
    t2 = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    await asyncio.gather(t1, t2, return_exceptions=False)
