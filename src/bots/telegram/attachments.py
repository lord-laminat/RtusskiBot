from bots.common.attachments import BaseAttachmentsProvider
from bots.common.content import MessageAttachment
from aiogram.types import (
    URLInputFile,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
)


class AiogramAttachmentsProvider(BaseAttachmentsProvider):
    # TODO add videos support
    async def provide_media(self, attachments: list[MessageAttachment]):
        media = []
        for at in attachments:
            if at.type == 'photo':
                media.append(InputMediaPhoto(media=URLInputFile(url=at.url)))
            if at.type == 'video':
                media.append(
                    InputMediaVideo(
                        media=URLInputFile(url=at.url, filename=at.title)
                    )
                )
        return media

    async def provide_documents(self, attachments: list[MessageAttachment]):
        documents = []
        for at in attachments:
            if at.type == 'doc':
                documents.append(
                    InputMediaDocument(
                        media=URLInputFile(url=at.url, filename=at.title)
                    )
                )
        return documents
