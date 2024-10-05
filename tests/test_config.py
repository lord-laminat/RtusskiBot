from bots.config import load_config, TelegramBot, DiscordBot, VkontakteBot


def test_config_from_path():
    path = "tests/assets/config.toml.example"
    config = load_config(path)

    assert config.dsbot == DiscordBot("abc", "not sure")
    assert config.tgbot == TelegramBot("def", 125)
    assert config.vkbot == VkontakteBot("ghi", "not sure too")
