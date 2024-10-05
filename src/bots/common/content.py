from dataclasses import dataclass, field


@dataclass
class Content:
    title: str
    url: str
    type: str


@dataclass
class Attachments:
    text: str = ""
    images: list[Content] = field(default_factory=list)
    videos: list[Content] = field(default_factory=list)
    documents: list[Content] = field(default_factory=list)

    def text_only(self):
        return not (self.images or self.videos or self.documents)

    def gte_media(self):
        return self.videos + self.images
