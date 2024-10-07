import logging
import os
import random
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
from bots.common.attachments import BaseAttachmentsProvider
from bots.common.bot import BaseBot, QueueWrapper

config = load_vk_config(os.getenv("BOTS_CONFIG_PATH"))

logger = logging.getLogger(__name__)


class VkBottleAttachmentsProvider(BaseAttachmentsProvider):
    def __init__(
        self, photo_uploader, video_uploader, document_uploader, peer_id
    ):
        self.photo_uploader = photo_uploader
        self.video_uploader = video_uploader
        self.document_uploader = document_uploader
        self.peer_id = peer_id

    async def provide_media(self, message_content: FullMessageContent):
        media = []
        attachments = message_content.attachments
        for at in attachments:
            if at.type == "photo":
                attachment = await self.photo_uploader.upload(
                    file_source=at.content, peer_id=self.peer_id
                )
                media.append(attachment)
            if at.type == "video":
                attachment = await self.video_uploader.upload(
                    file_source=at.content, peer_id=self.peer_id
                )
                media.append(attachment)
        return media

    async def provide_documents(self, message_content: FullMessageContent):
        attachments = message_content.attachments
        documents = []
        for at in attachments:
            if at.type == "doc":
                document = await self.document_uploader.upload(
                    file_source=at.content,
                    peer_id=self.peer_id,
                    title=at.title,
                )
                documents.append(document)
        return documents


class VkbottleBot(BaseBot):
    async def send_message(self, message_content: FullMessageContent):
        # basically you want to have this behaviour:
        # text-only: paste text
        # attachment-with-text: use text as caption to attachment

        message_text = message_content.text

        media = await self.attachments_provider.provide_media(message_content)
        documents = await self.attachments_provider.provide_documents(
            message_content
        )
        # vk does not care about type of attachment
        all_attachments = media + documents
        if all_attachments:
            await bot.api.messages.send(
                peer_id=self.chat_id,
                message=message_text,
                random_id=random.randint(1, 10000),
                attachment=",".join(all_attachments),
            )
        # message does not conatin any useful information
        if not (media or documents):
            await bot.api.messages.send(
                peer_id=self.chat_id,
                message=message_text,
                random_id=random.randint(1, 100000),
            )


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
