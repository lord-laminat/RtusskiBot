import random

from bots.common.bot import BaseBot
from bots.common.content import FullMessageContent


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
            await self.bot.api.messages.send(
                peer_id=self.chat_id,
                message=message_text,
                random_id=random.randint(1, 10000),
                attachment=','.join(all_attachments),
            )
        # message does not conatin any useful information
        if not (media or documents):
            await self.bot.api.messages.send(
                peer_id=self.chat_id,
                message=message_text,
                random_id=random.randint(1, 100000),
            )
