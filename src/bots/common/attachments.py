from abc import ABC, abstractmethod
from typing import Any

from bots.common.content import FullMessageContent


class BaseAttachmentsProvider(ABC):
    # it may require to download files asynchronously
    @abstractmethod
    async def provide_media(self, message_content: FullMessageContent) -> Any:
        pass

    # it may require to download files asynchronously
    @abstractmethod
    async def provide_documents(
        self, message_content: FullMessageContent
    ) -> Any:
        pass
