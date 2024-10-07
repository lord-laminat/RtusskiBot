from bots.config import (
    load_tg_config,
    load_discord_config,
    load_vk_config,
    TelegramBot,
    DiscordBot,
    VkontakteBot,
)


def test_config_from_path():
    path = "tests/assets/config.toml.example"

    tgbot_config = load_tg_config(path)
    dsbot_config = load_discord_config(path)
    vkbot_config = load_vk_config(path)

    assert dsbot_config == DiscordBot("abc", "not sure")
    assert tgbot_config == TelegramBot("def", 125)
    assert vkbot_config == VkontakteBot("ghi", "not sure too")
