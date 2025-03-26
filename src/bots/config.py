from dataclasses import dataclass, field

import toml


@dataclass
class TelegramBot:
    token: str
    chat_id: int
    thread_id: int


@dataclass
class VkontakteBot:
    token: str
    chat_id: str
    admins: list[int] = field(default_factory=list)


def load_tg_config(path: str) -> TelegramBot:
    data = toml.load(open(path))
    return TelegramBot(**data['tgbot'])


def load_vk_config(path: str) -> VkontakteBot:
    data = toml.load(open(path))
    return VkontakteBot(**data['vkbot'])
