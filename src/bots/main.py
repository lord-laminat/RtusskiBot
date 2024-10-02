from sys import argv  # получаем список аргументов, с которыми был запущен main.py
from threading import Thread
from queue import Queue
import os

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from telebot import TeleBot

from bots.telegram import telegram_bot
# rom bots.discord import discord_bot
from bots.vk import vkontakte_bot
from bots.config import load_config




def main():
    config = load_config(os.getenv("BOTS_CONFIG_PATH"))

    vk_session = vk_api.VkApi(token=config.vkbot.token)
    longpoll = VkBotLongPoll(vk_session, group_id=config.vkbot.group_id)
    vk = vk_session.get_api()

    tg_posts = Queue()
    ds_posts = Queue()

    vk_bot = Thread(target=vkontakte_bot.launch, args=(longpoll, tg_posts, ds_posts), daemon=True)
    tg_bot = Thread(target=telegram_bot.launch, args=(config,), daemon=True)
    # ds_bot = Thread(target=discord_bot.launch,   args=(ds_posts,), daemon=True)

    vk_bot.start()
    tg_bot.start()
    # ds_bot.start()

    try:
        while vk_bot.is_alive() and tg_bot.is_alive():
            pass
    except KeyboardInterrupt: ...


if __name__ == "__main__":
    main()