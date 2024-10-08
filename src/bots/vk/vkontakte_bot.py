import logging
import os
import asyncio

from vkbottle import Bot
from vkbottle.tools import (
    LoopWrapper,
    DocMessagesUploader,
    PhotoMessageUploader,
    VideoUploader,
)

from bots.config import load_vk_config
from bots.common.content import (
    MessageAttachment,
    FullMessageContent,
)
from bots.common.bot import QueueWrapper
from .bot_wrapper import VkbottleBot
from .attachments import VkBottleAttachmentsProvider

config = load_vk_config(os.getenv("BOTS_CONFIG_PATH"))

logger = logging.getLogger(__name__)

bot = Bot(config.token)
bot_wrapper = VkbottleBot(
    bot,
    config.chat_id,
    VkBottleAttachmentsProvider(
        PhotoMessageUploader(bot.api),
        VideoUploader(bot.api),
        DocMessagesUploader(bot.api),
        config.chat_id,
    ),
)


@bot.on.message()
async def foo(message):
    # default polling can not provide all the images if there at least 4 images
    # that's why I needed to do another request to get full message and
    # take all the attachments from it.

    # see https://dev.vk.com/ru/method/messages.getByConversationMessageId
    res = await bot.api.messages.get_by_conversation_message_id(
        peer_id=message.peer_id,
        conversation_message_ids=message.conversation_message_id,
    )
    full_message = res.items[0]
    message_content = FullMessageContent(full_message.text)

    for at in full_message.attachments:
        if at.type.value == "doc":
            message_content.attachments.append(
                MessageAttachment(at.doc.title, at.doc.url, "doc")
            )
        if at.type.value == "photo":
            # sort by height and get the second highest
            image_url = sorted(at.photo.sizes, key=lambda x: x.height)[-2].url
            message_content.attachments.append(
                MessageAttachment(at.photo.text, image_url, "photo")
            )
        if at.type.value == "video":
            # TODO implement video support
            pass

    bot.telegram_posts.put_nowait(message_content)
    bot.discord_posts.put_nowait(message_content)
    await message.answer("Hi")


async def main(my_posts, tgbot_posts, dsbot_posts):

    queue_wrapper = QueueWrapper(bot_wrapper)
    bot.telegram_posts = tgbot_posts
    bot.discord_posts = dsbot_posts
    bot.loop_wrapper = LoopWrapper(loop=asyncio.get_running_loop())
    t1 = asyncio.create_task(queue_wrapper.process_posts(my_posts))
    t2 = asyncio.create_task(bot.run_polling())
    await asyncio.gather(t1, t2)
