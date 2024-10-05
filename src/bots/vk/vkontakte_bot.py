import logging
import os
import asyncio

from vkbottle import Bot
from vkbottle.tools import LoopWrapper

from bots.config import load_vk_config
from bots.common.content import Content, Attachments

config = load_vk_config(os.getenv("BOTS_CONFIG_PATH"))

bot = Bot(config.token)

logger = logging.getLogger(__name__)


@bot.on.message()
async def foo(message):
    # default polling can not provide all the images if there at least 4 images
    # that's why I needed to do another request to get full message and
    # take all the attachments from it.

    # see https://dev.vk.com/ru/method/messages.getByConversationMessageId
    data = {
        "peer_id": message.peer_id,
        "conversation_message_ids": message.conversation_message_id,
    }
    res = await bot.api.request(
        "messages.getByConversationMessageId", data=data
    )
    full_message = res["response"]["items"][0]
    attachments = Attachments(text=full_message["text"])

    for at in full_message["attachments"]:
        if at["type"] == "doc":
            attachments.documents.append(
                Content(at["doc"]["title"], at["doc"]["url"])
            )
        if at["type"] == "photo":
            # sort by height and get the second highest
            image_url = sorted(
                at["photo"]["sizes"], key=lambda x: x["height"]
            )[-2]["url"]
            attachments.images.append(Content(at["photo"]["text"], image_url))
        if at["type"] == "video":
            # TODO implement video support
            pass

    bot.telegram_queue.put_nowait(attachments)
    bot.discord_posts.put_nowait(attachments)
    await message.answer("Hi")


async def main(my_posts, tgbot_posts, dbot_queue):

    bot.telegram_queue = tgbot_posts
    bot.discord_posts = dbot_queue
    bot.loop_wrapper = LoopWrapper(loop=asyncio.get_running_loop())
    await bot.run_polling()
