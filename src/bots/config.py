from dataclasses import dataclass

import toml


@dataclass
class DiscordBot:
    token: str
    guild_id: str


@dataclass
class TelegramBot:
    token: str
    chat_id: int


@dataclass
class VkontakteBot:
    token: str
    chat_id: str


def load_tg_config(path: str) -> TelegramBot:
    data = toml.load(open(path))
    return TelegramBot(**data["tgbot"])


def load_discord_config(path: str) -> DiscordBot:
    data = toml.load(open(path))
    return DiscordBot(**data["dsbot"])


def load_vk_config(path: str) -> VkontakteBot:
    data = toml.load(open(path))
    return VkontakteBot(**data["vkbot"])
