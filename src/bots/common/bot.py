from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseBot(ABC):
    def __init__(self, bot, chat_id, attachments_provider):
        self.bot = bot
        self.chat_id = chat_id
        self.attachments_provider = attachments_provider

    @abstractmethod
    async def send_message(self, message_content):
        ...


class QueueWrapper:
    def __init__(self, bot_wrapper: BaseBot):
        self.bot_wrapper = bot_wrapper

    async def process_posts(self, queue):
        while True:
            message_content = await queue.get()
            try:
                await self.bot_wrapper.send_message(message_content)
            except Exception as e:
                logger.exception(e)
