import asyncio
import os
import logging

from aiogram import Dispatcher, Bot, F, Router
from aiogram.types import (
    Message,
)
from aiogram.filters import Filter
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_album import AlbumMessage
from aiogram_album.ttl_cache_middleware import TTLCacheAlbumMiddleware

from bots.config import load_tg_config
from bots.common.content import FullMessageContent, MessageAttachment
from bots.common.bot import QueueWrapper
from bots.telegram.attachments import AiogramAttachmentsProvider
from bots.telegram.bot_wrapper import AiogramBot
from bots.common.models import subscriberDTO


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


router = Router()
TTLCacheAlbumMiddleware(router=router)


class ChatFilter(Filter):
    def __init__(self, topic_name):
        self.topic_name = topic_name

    async def __call__(self, message: Message, config):
        # since mailing chat is the same for from messages and to messages
        # we can use chat_id and thred_id here
        if message.chat.id == config.chat_id:
            return message.message_thread_id == config.thread_id
        return False


@router.message(F.media_group_id, ChatFilter())
async def process_message_with_attachments(message: AlbumMessage, bot: Bot):
    attachments = []
    for m in message:
        if m.photo:
            photo = m.photo
            bytes_io_file = await bot.download(photo[-1])
            attachments.append(
                MessageAttachment('', '', 'photo', bytes_io_file.read())
            )
        if m.document:
            doc = m.document
            filename = doc.file_name
            bytes_io_file = await bot.download(doc)
            attachments.append(
                MessageAttachment(filename, '', 'doc', bytes_io_file.read())
            )

    await bot.vk_posts.put(FullMessageContent(message.caption, attachments))


@router.message(ChatFilter())
async def process_plain_text(message: Message, bot: Bot):
    message_text = message.text or message.caption
    message_content = FullMessageContent(message_text)

    if message.photo:
        photo = message.photo
        bytes_io_file = await bot.download(photo[-1])
        message_content.attachments.append(
            MessageAttachment('', '', 'photo', bytes_io_file.read())
        )
    if message.document:
        doc = message.document
        filename = doc.file_name
        bytes_io_file = await bot.download(doc)
        message_content.attachments.append(
            MessageAttachment(filename, '', 'doc', bytes_io_file.read())
        )

    await bot.vk_posts.put(message_content)


@router.message(ChatFilter(), lambda msg: '#дз' in msg.text)
async def process_message_with_homework_tag(
    message: Message, bot: Bot, db_connection
):
    message_text = message.text or message.caption
    user_repo = UserRepo(db_connection)
    for subscriber in user_repo.get_homework_subscribers():
        await message.send_copy(subscriber.chat_id)


@router.message(Command('subscribeToHomeworkNotifications'))
async def subscribe_to_homework_notificaitons(
    message: Message, bot: Bot, db_connection
):

    subscriber = SubscriberDTO()


async def main(my_posts, vk_posts):
    config = load_tg_config(os.getenv('BOTS_CONFIG_PATH'))

    dp = Dispatcher()
    dp.include_router(router)

    dp['config'] = config

    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML, link_preview_is_disabled=True
        ),
    )

    bot_wrapper = AiogramBot(
        bot, config.chat_id, AiogramAttachmentsProvider(), config.thread_id
    )

    queue_wrapper = QueueWrapper(bot_wrapper)
    bot.vk_posts = vk_posts

    logger.debug('starting telergam application')
    t1 = asyncio.create_task(queue_wrapper.process_posts(my_posts))
    t2 = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    await asyncio.gather(t1, t2, return_exceptions=False)
