import asyncio
import logging
from re import sub

from aiogram import Dispatcher, Bot, F, Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
)
from aiogram.filters import Filter
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_album import AlbumMessage
from aiogram_album.ttl_cache_middleware import TTLCacheAlbumMiddleware

from bots.common.content import FullMessageContent, MessageAttachment
from bots.common.bot import QueueWrapper
from bots.telegram.attachments import AiogramAttachmentsProvider
from bots.telegram.bot_wrapper import AiogramBot
from bots.common.models import SubscriberDTO, UserDTO
from bots.common.db import BaseSubscriberRepo, BaseUserRepo
from bots.telegram.middleware import DbMiddleware


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


router = Router()
TTLCacheAlbumMiddleware(router=router)


class ChatFilter(Filter):
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
            if bytes_io_file:
                attachments.append(
                    MessageAttachment('', '', 'photo', bytes_io_file.read())
                )
        if m.document:
            doc = m.document
            filename = doc.file_name or 'unnamed'
            bytes_io_file = await bot.download(doc)
            if bytes_io_file:
                attachments.append(
                    MessageAttachment(
                        filename, '', 'doc', bytes_io_file.read()
                    )
                )

    text = message.caption or ''
    await bot.vk_posts.put(FullMessageContent(text, attachments))  # type: ignore


@router.message(ChatFilter())
async def process_plain_text(message: Message, bot: Bot):
    message_text = message.text or message.caption or ''
    message_content = FullMessageContent(message_text)

    if message.photo:
        photo = message.photo
        bytes_io_file = await bot.download(photo[-1])
        if bytes_io_file:
            message_content.attachments.append(
                MessageAttachment('', '', 'photo', bytes_io_file.read())
            )
    if message.document:
        doc = message.document
        filename = doc.file_name or 'unnamed'
        bytes_io_file = await bot.download(doc)
        if bytes_io_file:
            message_content.attachments.append(
                MessageAttachment(filename, '', 'doc', bytes_io_file.read())
            )

    await bot.vk_posts.put(message_content)  # type: ignore


@router.message(ChatFilter(), lambda msg: '#дз' in msg.text)
async def process_message_with_homework_tag(
    message: Message, bot: Bot, subscriber_repo: BaseSubscriberRepo
):
    subscribers = await subscriber_repo.get_all_subscribers()
    for subscriber in subscribers:
        await message.send_copy(subscriber.chat_id)


@router.message(Command('subscribeToHomeworkNotifications'))
async def subscribe_to_homework_notificaitons(
    message: Message, bot: Bot, subscriber_repo: BaseSubscriberRepo
):
    print(message)
    subscriber = SubscriberDTO(
        message.from_user.id,  # type: ignore
        message.from_user.username,  # type: ignore
        message.from_user.full_name,  # type: ignore
    )
    await subscriber_repo.add_subscriber(subscriber)
    await message.reply('User added succesfully')


@router.message(Command('start'))
async def start_command(message: Message, bot: Bot, user_repo: BaseUserRepo):
    chat_id = message.from_user.id  # type: ignore
    username = message.from_user.username  # type: ignore
    full_name = message.from_user.full_name  # type: ignore
    user = UserDTO(chat_id, username, full_name)  # type: ignore
    await user_repo.add_user(user)
    await message.reply(f'Helo {username}!')


async def main(config, my_posts, vk_posts, connection_pool):
    dp = Dispatcher()
    dp.include_router(router)

    dp['config'] = config
    dp.message.middleware(DbMiddleware(connection_pool))
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
    bot.vk_posts = vk_posts  # type: ignore

    logger.debug('starting telergam application')
    t1 = asyncio.create_task(queue_wrapper.process_posts(my_posts))
    t2 = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    await asyncio.gather(t1, t2, return_exceptions=False)
