from bots.common.bot import BaseBot
from bots.common.content import FullMessageContent


class AiogramBot(BaseBot):
    def __init__(self, bot, chat_id, attachments_provider, message_thread_id):
        self.bot = bot
        self.chat_id = chat_id
        self.attachments_provider = attachments_provider
        self.message_thread_id = message_thread_id

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
            await self.bot.send_message(
                self.chat_id,
                message_text,
                message_thread_id=self.message_thread_id,
            )
        else:
            if media:
                media[0].caption = message_text
                await self.bot.send_media_group(
                    self.chat_id,
                    media=media,
                    message_thread_id=self.message_thread_id,
                )
            if documents:
                documents[0].caption = message_text
                await self.bot.send_media_group(
                    self.chat_id,
                    media=documents,
                    message_thread_id=self.message_thread_id,
                )
