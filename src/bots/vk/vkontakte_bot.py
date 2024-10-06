import logging
import os
import asyncio

from vkbottle import Bot
from vkbottle.tools import LoopWrapper, DocMessagesUploader, PhotoMessageUploader

from bots.config import load_vk_config
from bots.common.content import MessageAttachment, FullMessageContent
from bots.common.attachments import BaseAttachmentsProvider

config = load_vk_config(os.getenv("BOTS_CONFIG_PATH"))

bot = Bot(config.token)

logger = logging.getLogger(__name__)


# class VkBottleAttachmentsProvider(BaseAttachmentsProvider):
#     @staticmethod
#     def provide_media(attachments: MessageAttachment):
#         media = []
#         for at in attachments:
#             if at.type == "photo":
#                 media.append(InputMediaPhoto(URLInputFile(url=at.url))) if at.type == "video":
#                 media.append(
#                     InputMediaVideo(
#                         URLInputFile(url=at.url, filename=at.title)
#                     )
#                 )
#         return media
#     @staticmethod
#     def provide_documents(attachments: MessageAttachment):
#         media = []
#         for at in attachments:
#             if at.type == "photo":
#                 media.append(InputMediaPhoto(URLInputFile(url=at.url)))
#             if at.type == "video":
#                 media.append(
#                     InputMediaVideo(
#                         URLInputFile(url=at.url, filename=at.title)
#                     )
#                 )
#         return media


# class BotCommands:
#     def __init__(self, bot, chat_id):
#         self.bot = bot
#         self.chat_id = chat_id
#         self.attachments_provider

#     async def send_messages(self, message_content: FullMessageContent):
#         # basically you want to have this behaviour:
#         # text-only: paste text
#         # attachment-with-text: use text as caption to attachment

#         message_text = message_content.text
#         media = self.attachments_provider.provide_media(message_content)
#         documents = self.attachments_provider.provide_documents(message_content)

#         if not (media or documents):  # that was text based message
#             await bot.send_message(self.chat_id, message_text)
#         else:
#             if media:
#                 media[0].caption = message_text
#                 await bot.send_media_group(self.chat_id, media=media)
#             if documents:
#                 documents[0].caption = message_text
#                 await bot.send_media_group(self.chat_id, media=documents)


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

    bot.telegram_queue.put_nowait(message_content)
    bot.discord_posts.put_nowait(message_content)
    await message.answer("Hi")


# async def check_queue(queue):
#     while True:
#         attachments = await queue.get()
#         bot_commands.send_messages(attachments)
#         queue.task_done()


async def main(my_posts, tgbot_posts, dbot_queue):

    bot.telegram_queue = tgbot_posts
    bot.discord_posts = dbot_queue
    bot.loop_wrapper = LoopWrapper(loop=asyncio.get_running_loop())
    # t1 = asyncio.create_task(check_queue(my_posts))
    t2 = asyncio.create_task(bot.run_polling())
    await t2
    # await asyncio.wait([t2], return_when="FIRST_EXCEPTION")
