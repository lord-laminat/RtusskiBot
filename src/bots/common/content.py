from dataclasses import dataclass, field


@dataclass
class MessageAttachment:
    title: str
    url: str = ""
    type: str = ""
    content: bytes = b""


@dataclass
class FullMessageContent:
    text: str
    attachments: list[MessageAttachment] = field(default_factory=list)
