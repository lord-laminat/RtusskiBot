from bots.config import (
    load_tg_config,
    load_discord_config,
    load_vk_config,
    TelegramBot,
    DiscordBot,
    VkontakteBot,
)


def test_config_from_path():
    path = 'tests/assets/config.toml.example'

    tgbot_config = load_tg_config(path)
    dsbot_config = load_discord_config(path)
    vkbot_config = load_vk_config(path)

    assert tgbot_config == TelegramBot('abc', 123)
    assert vkbot_config == VkontakteBot('def', 456)
    assert dsbot_config == DiscordBot('ghi', 789)
