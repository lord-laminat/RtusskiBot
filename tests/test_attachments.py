import io

from vkbottle.tools import PhotoMessageUploader, DocMessagesUploader
from aiogram.types import InputMediaDocument, URLInputFile

from bots.telegram.attachments import AiogramAttachmentsProvider
from bots.vk.attachments import VkBottleAttachmentsProvider
from bots.common.content import FullMessageContent, MessageAttachment


async def test_aiogram_document_provider():
    documents = [
        MessageAttachment(
            title='mydocument.doc',
            url='https://example.com/mydocument.doc',
            type='doc',
        )
    ]
    provider = AiogramAttachmentsProvider()
    attachment = (await provider.provide_documents(documents))[0]

    expected = InputMediaDocument(
        media=URLInputFile(
            url=documents[0].url,
            filename=documents[0].title,
        )
    )

    assert attachment.media.url == expected.media.url
    assert attachment.media.filename == expected.media.filename
