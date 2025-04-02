from dataclasses import dataclass


@dataclass
class SubscriberDTO:
    user_id: int
    channel_id: int


@dataclass
class UserDTO:
    chat_id: int
    username: str | None
    full_user_name: str | None
