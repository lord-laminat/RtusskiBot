from abc import ABC, abstractmethod

from bots.common.content import MessageAttachment


class BaseAttachmentsProvider(ABC):
    @staticmethod
    @abstractmethod
    def provide_media(attachments: MessageAttachment): ...

    @staticmethod
    @abstractmethod
    def provide_documents(attachments: MessageAttachment): ...
