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
from bots.common.content import Attachments


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

config = load_tg_config(os.getenv("BOTS_CONFIG_PATH"))

dp = Dispatcher()

bot = Bot(token=config.token)


# maybe move it to another place
class BotCommands:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

    async def send_messages(self, attachments: Attachments):
        # TODO add videos support
        # TODO split this function into smaller ones
        # basically you want to have thi behaviour:
        # text-only: paste text
        # attachment-with-text: use text as caption to attachment
        if attachments.text_only():
            await bot.send_message(self.chat_id, attachments.text)
        else:
            if attachments.images:
                first_photo = attachments.images[0]
                images = [
                    InputMediaPhoto(
                        media=URLInputFile(first_photo.url, filename=""),
                        caption=attachments.text,
                    )
                ]
                for img in attachments.images[1:]:
                    images.append(
                        InputMediaPhoto(
                            media=URLInputFile(img.url, filename=""),
                        )
                    )
                await bot.send_media_group(self.chat_id, media=images)
            if attachments.documents:
                documents = [
                    InputMediaDocument(
                        media=URLInputFile(doc.url, filename=doc.title)
                    )
                    for doc in attachments.documents
                ]
                await bot.send_media_group(self.chat_id, media=documents)


bot_commands = BotCommands(bot, config.chat_id)


@dp.message(Command("ping"))
async def ping(message: Message):
    await message.reply("pong")


async def check_query(queue):
    while True:
        attachments = await queue.get()
        await bot_commands.send_messages(attachments)


async def main(my_posts, ds_posts, vk_posts):
    logger.info("starting the application")
    await asyncio.create_task(check_query(my_posts))
    await dp.start_polling(bot, handle_signals=False)
