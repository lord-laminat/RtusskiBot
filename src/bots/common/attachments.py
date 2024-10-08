from abc import ABC, abstractmethod

from bots.common.content import MessageAttachment


class BaseAttachmentsProvider(ABC):
    # it may require to download files asynchronously
    @abstractmethod
    async def provide_media(attachments: MessageAttachment): ...

    # it may require to download files asynchronously
    @abstractmethod
    async def provide_documents(attachments: MessageAttachment): ...
