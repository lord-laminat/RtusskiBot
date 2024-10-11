import logging
import os
import asyncio

from vkbottle import Bot
from vkbottle.bot import Message
from vkbottle.tools import (
    LoopWrapper,
    DocMessagesUploader,
    PhotoMessageUploader,
)
from vkbottle.dispatch.rules.base import ABCRule

from bots.config import load_vk_config
from bots.common.content import (
    MessageAttachment,
    FullMessageContent,
)
from bots.common.bot import QueueWrapper
from bots.vk.bot_wrapper import VkbottleBot
from bots.vk.attachments import VkBottleAttachmentsProvider
from bots.vk.utils import resolve_vk_links

config = load_vk_config(os.getenv("BOTS_CONFIG_PATH"))

logger = logging.getLogger(__name__)

bot = Bot(config.token)
bot_wrapper = VkbottleBot(
    bot,
    config.chat_id,
    VkBottleAttachmentsProvider(
        PhotoMessageUploader(bot.api),
        DocMessagesUploader(bot.api),
        config.chat_id,
    ),
)

# TODO use regexp to replace [ID|username] to markdown link to https://vk.com/ID

# match something like [Non-Space|Non-Space]


class ChatIdRule(ABCRule):
    def __init__(self, chat_ids):
        self.chat_ids = chat_ids

    async def check(self, event: Message):
        return event.from_id in self.chat_ids


def get_doc_attachment(at):
    return MessageAttachment(at.doc.title, at.doc.url, "doc")


def get_photo_attachment(at):
    image_url = sorted(at.photo.sizes, key=lambda x: x.height)[-2].url
    return MessageAttachment(at.photo.text, image_url, "photo")


def parse_attachments(attachments=[]):
    # using empty list is safe here, we do not mutate it anywhere
    custom_attachments = []
    for at in attachments:
        if at.type.value == "doc":
            custom_attachments.append(get_doc_attachment(at))
        if at.type.value == "photo":
            custom_attachments.append(get_photo_attachment(at))
        if at.type.value == "wall":
            if at.wall.attachments:
                custom_attachments.extend(
                    parse_attachments(at.wall.attachments)
                )
            if at.wall.copy_history:
                for x in at.wall.copy_history:
                    if x.attachments:
                        custom_attachments.extend(
                            parse_attachments(x.attachments)
                        )
    return custom_attachments


def get_wall_attachment_text(attachments):
    text = ""
    for x in attachments:
        if x.type.value == "wall":
            text += f"{x.wall.text}"
            if x.wall.copy_history:
                for post in x.wall.copy_history:
                    text += f"\n\n{post.text}"
    return text.lstrip()


def extract_text_from_thread(message):
    text = message.text
    text += f"\n\n{get_wall_attachment_text(message.attachments)}"
    if message.fwd_messages:
        for fwd_msg in message.fwd_messages:
            wall_text = get_wall_attachment_text(fwd_msg.attachments)
            fwd_tree_text = extract_text_from_thread(fwd_msg)
            text += f"\n{fwd_tree_text}"
            text += f"\n{wall_text}"

    return text.lstrip()


def make_post_text(message):
    # since message is a part of this "thread", treat message as "thread"
    post_text = extract_text_from_thread(message)
    return resolve_vk_links(post_text)


def extract_attachments_from_thread(message):
    attachments = parse_attachments(message.attachments)
    if message.fwd_messages:
        for fwd_msg in message.fwd_messages:
            thread_attachments = extract_attachments_from_thread(fwd_msg)
            attachments.extend(thread_attachments)
    return attachments


def make_post_attachments(message):
    attachments = extract_attachments_from_thread(message)
    return attachments


def make_post(message):
    print(message)
    post_text = make_post_text(message)
    attachments = make_post_attachments(message)
    return FullMessageContent(post_text, attachments)


#@bot.on.message(ChatIdRule(config.admins))
@bot.on.message()
async def foo(message):
    print(message)
    # default polling can not provide all the images if there at least 4 images
    # that's why I needed to do another request to get full message and
    # take all the attachments from it.
    # see https://dev.vk.com/ru/method/messages.getByConversationMessageId
    response = await bot.api.messages.get_by_conversation_message_id(
        peer_id=message.peer_id,
        conversation_message_ids=message.conversation_message_id,
    )
    full_message = response.items[0]
    bot.telegram_posts.put_nowait(FullMessageContent(full_message.from_id))
    # post = make_post(full_message)
    # bot.telegram_posts.put_nowait(post)


async def main(my_posts, tgbot_posts):

    queue_wrapper = QueueWrapper(bot_wrapper)
    bot.telegram_posts = tgbot_posts
    bot.loop_wrapper = LoopWrapper(loop=asyncio.get_running_loop())
    t1 = asyncio.create_task(queue_wrapper.process_posts(my_posts))
    t2 = asyncio.create_task(bot.run_polling())
    await asyncio.gather(t1, t2)
