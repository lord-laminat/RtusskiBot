import asyncio
import os
import logging

from aiogram import Dispatcher, Bot, F
from aiogram.types import (
    Message,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
    URLInputFile,
)
from aiogram_album import AlbumMessage
from aiogram_album.ttl_cache_middleware import TTLCacheAlbumMiddleware

from bots.config import load_tg_config
from bots.common.attachments import BaseAttachmentsProvider
from bots.common.content import FullMessageContent, MessageAttachment
from bots.common.bot import BaseBot, QueueWrapper


class AiogramAttachmentsProvider(BaseAttachmentsProvider):
    # TODO add videos support
    async def provide_media(self, attachments: list[MessageAttachment]):
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

    async def provide_documents(self, attachments: list[MessageAttachment]):
        documents = []
        for at in attachments:
            if at.type == "doc":
                documents.append(
                    InputMediaDocument(
                        media=URLInputFile(url=at.url, filename=at.title)
                    )
                )
        return documents


class AiogramBot(BaseBot):
    def __init__(self, bot, chat_id, attachments_provider):
        self.bot = bot
        self.chat_id = chat_id
        self.attachments_provider = attachments_provider

    async def send_message(self, message_content: FullMessageContent):
        # basically you want to have this behaviour:
        # text-only: paste text
        # attachment-with-text: use text as caption to attachment

        message_text = message_content.text
        media = await self.attachments_provider.provide_media(
            message_content.attachments
        )
        documents = await self.attachments_provider.provide_documents(
            message_content.attachments
        )
        if not (media or documents):  # that was text based message
            await self.bot.send_message(self.chat_id, message_text)
        else:
            if media:
                media[0].caption = message_text
                await self.bot.send_media_group(self.chat_id, media=media)
            if documents:
                documents[0].caption = message_text
                await self.bot.send_media_group(self.chat_id, media=documents)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

config = load_tg_config(os.getenv("BOTS_CONFIG_PATH"))

dp = Dispatcher()
TTLCacheAlbumMiddleware(router=dp)

bot = Bot(token=config.token)
bot_wrapper = AiogramBot(bot, config.chat_id, AiogramAttachmentsProvider())


@dp.message(F.media_group_id)
async def process_message_with_attachments(message: AlbumMessage):
    message_content = FullMessageContent(message.caption)
    for m in message:
        if m.photo:
            photo = m.photo
            bytes_io_file = await bot.download(photo[-1])
            message_content.attachments.append(
                MessageAttachment("", "", "photo", bytes_io_file.read())
            )
        if m.video:
            video = m.video
            bytes_io_file = await bot.download(video[-1])
            message_content.attachments.append(
                MessageAttachment("", "", "photo", bytes_io_file.read())
            )
        if m.document:
            doc = m.document
            filename = doc.file_name
            bytes_io_file = await bot.download(doc)
            message_content.attachments.append(
                MessageAttachment(filename, "", "doc", bytes_io_file.read())
            )

    await bot.vk_posts.put(message_content)
    await message.reply("Resending with attachments...")


@dp.message()
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
    await message.reply("Resending...")


async def main(my_posts, ds_posts, vk_posts):
    logger.info("starting the application")
    queue_wrapper = QueueWrapper(bot_wrapper)
    bot.ds_posts = ds_posts
    bot.vk_posts = vk_posts
    t1 = asyncio.create_task(queue_wrapper.process_posts(my_posts))
    t2 = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    await asyncio.gather(t1, t2, return_exceptions=False)
