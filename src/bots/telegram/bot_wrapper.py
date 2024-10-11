from bots.common.bot import BaseBot
from bots.common.content import FullMessageContent

from aiogram.enums import ParseMode


class AiogramBot(BaseBot):
    def __init__(self, bot, chat_id, attachments_provider, message_thread_id):
        self.bot = bot
        self.chat_id = chat_id
        self.attachments_provider = attachments_provider
        self.message_thread_id = message_thread_id

    async def send_media(self, media, caption=None):
        if caption:
            media[0].caption = caption
        await self.bot.send_media_group(
            self.chat_id,
            media=media,
            message_thread_id=self.message_thread_id,
        )

    async def send_documents(self, documents, caption=None):
        if caption:
            documents[0].caption = caption
        await self.bot.send_media_group(
            self.chat_id,
            media=documents,
            message_thread_id=self.message_thread_id,
        )

    async def send_message(self, message_content: FullMessageContent):
        # basically you want to have this behaviour:
        # text-only: paste text
        # attachment-with-text: use text as caption to attachment

        message_text = message_content.text
        only_text = len(message_text) >= 1000
        media = await self.attachments_provider.provide_media(
            message_content.attachments
        )
        documents = await self.attachments_provider.provide_documents(
            message_content.attachments
        )
        if not (media or documents):  # that was text based message
            await self.bot.send_message(
                self.chat_id,
                message_text,
                message_thread_id=self.message_thread_id,
                parse_mode=ParseMode.HTML,
            )
        else:
            if media:
                if only_text:
                    await self.send_media(media)
                else:
                    await self.send_media(media, caption=message_text)
            if documents:
                if only_text:
                    await self.send_documents(documents)
                else:
                    await self.send_documents(documents, caption=message_text)
            if only_text:
                await self.bot.send_message(
                    self.chat_id,
                    message_text,
                    message_thread_id=self.message_thread_id,
                    parse_mode=ParseMode.HTML,
                )
