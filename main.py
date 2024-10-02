from sys import argv  # получаем список аргументов, с которыми был запущен main.py
from threading import Thread
from queue import Queue

from bots.telegram import telegram_bot
from bots.discord import discord_bot
from bots.vk import vkontakte_bot


def main():
    tg_posts = Queue()
    ds_posts = Queue()

    vk_bot = Thread(target=vkontakte_bot.launch, args=(tg_posts, ds_posts), daemon=True)
    tg_bot = Thread(target=telegram_bot.launch, args=(tg_posts,), daemon=True)
    # ds_bot = Thread(target=discord_bot.launch,   args=(ds_posts,), daemon=True)

    vk_bot.start()
    tg_bot.start()
    # ds_bot.start()

    try:
        while vk_bot.is_alive() and tg_bot.is_alive(): ...
    except KeyboardInterrupt: ...


if __name__ == "__main__":
    main()