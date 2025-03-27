from dataclasses import dataclass


@dataclass
class SubscriberDTO:
    chat_id: int
    username: str


@dataclass
class UserDTO:
    chat_id: int
    username: str
    full_name: str | None
