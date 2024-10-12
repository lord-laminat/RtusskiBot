from bots.common.attachments import BaseAttachmentsProvider
from bots.common.content import FullMessageContent


class VkBottleAttachmentsProvider(BaseAttachmentsProvider):
    def __init__(self, photo_uploader, document_uploader, peer_id):
        self.photo_uploader = photo_uploader
        self.document_uploader = document_uploader
        self.peer_id = peer_id

    async def provide_media(self, message_content: FullMessageContent):
        # vkontakte does not allow bots to upload any videos
        media = []
        attachments = message_content.attachments
        for at in attachments:
            if at.type == "photo":
                attachment = await self.photo_uploader.upload(
                    # move this constant if you need. It just works now.
                    file_source=at.content, peer_id=2000000004
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
