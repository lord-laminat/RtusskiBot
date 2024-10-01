from dataclasses import dataclass

import toml


@dataclass
class DiscordBot:
    token: str
    chat_id: str


@dataclass
class TelegramBot:
    token: str
    chat_id: int


@dataclass
class VkontakteBot:
    token: str
    chat_id: str


@dataclass
class Config:
    dsbot: DiscordBot
    tgbot: TelegramBot
    vkbot: VkontakteBot


def load_config(path: str) -> Config:
    data = toml.load(open(path))
    return Config(
            dsbot=DiscordBot(**data["dsbot"]),
            tgbot=TelegramBot(**data["tgbot"]),
            vkbot=VkontakteBot(**data["vkbot"]),
        )

