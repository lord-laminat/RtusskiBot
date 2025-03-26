from dataclasses import dataclass


@dataclass
class SubscriberDTO:
    username: str
    chat_id: int
    tag: str
