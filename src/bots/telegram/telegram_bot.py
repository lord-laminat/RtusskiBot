import asyncio
import os
import logging

from aiogram import Dispatcher, Bot, F
from aiogram.types import (
    Message,
)
from aiogram_album import AlbumMessage
from aiogram_album.ttl_cache_middleware import TTLCacheAlbumMiddleware

from bots.config import load_tg_config
from bots.common.content import FullMessageContent, MessageAttachment
from bots.common.bot import QueueWrapper
from .attachments import AiogramAttachmentsProvider
from .bot_wrapper import AiogramBot


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

config = load_tg_config(os.getenv("BOTS_CONFIG_PATH"))

dp = Dispatcher()
TTLCacheAlbumMiddleware(router=dp)

bot = Bot(token=config.token)
bot_wrapper = AiogramBot(bot, config.chat_id, AiogramAttachmentsProvider())


@dp.message(F.media_group_id, F.caption.contains("#важное"))
async def process_message_with_attachments(message: AlbumMessage):
    for m in message:
        if m.photo:
            photo = m.photo
            bytes_io_file = await bot.download(photo[-1])
            FullMessageContent(message.caption).attachments.append(
                MessageAttachment("", "", "photo", bytes_io_file.read())
            )
        if m.video:
            video = m.video
            bytes_io_file = await bot.download(video[-1])
            FullMessageContent(message.caption).attachments.append(
                MessageAttachment("", "", "photo", bytes_io_file.read())
            )
        if m.document:
            doc = m.document
            filename = doc.file_name
            bytes_io_file = await bot.download(doc)
            FullMessageContent(message.caption).attachments.append(
                MessageAttachment(filename, "", "doc", bytes_io_file.read())
            )

    await bot.vk_posts.put(FullMessageContent(message.caption))
    await message.reply("Resending with attachments...")


@dp.message(F.text.contains("#важное"))
async def process_plain_text(message: Message):
    message_text = message.text or message.caption
    message_content = FullMessageContent(message_text)

    if message.photo:
        photo = message.photo
        bytes_io_file = await bot.download(photo[-1])
        message_content.attachments.append(
            MessageAttachment("", "", "photo", bytes_io_file.read())
        )
    if message.video:
        video = message.video
        bytes_io_file = await bot.download(video)
        message_content.attachments.append(
            MessageAttachment("", "", "video", bytes_io_file.read())
        )
    if message.document:
        doc = message.document
        filename = doc.file_name
        bytes_io_file = await bot.download(doc)
        message_content.attachments.append(
            MessageAttachment(filename, "", "doc", bytes_io_file.read())
        )

    await bot.vk_posts.put(message_content)


async def main(my_posts, vk_posts):
    logger.info("starting the application")
    queue_wrapper = QueueWrapper(bot_wrapper)
    bot.vk_posts = vk_posts
    t1 = asyncio.create_task(queue_wrapper.process_posts(my_posts))
    t2 = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    await asyncio.gather(t1, t2, return_exceptions=False)
