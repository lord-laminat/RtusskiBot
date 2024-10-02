# Using https://pytba.readthedocs.io/en/latest/index.html
from time import sleep
from json import load, dump
from queue import Queue
from threading import Thread

import telebot


class Commands:
    def __init__(self, chat_id, bot):
        self.chat_id = chat_id
        self.bot = bot
        self.add_command(self.ping, commands=["ping"])

    def ping(self, message):
        self.bot.reply_to(message, "pong")

    def add_command(self, handler, commands):
        self.bot.message_handler(commands=commands)(handler)

    def publish_post(self, post: map):
        if post["photo"] or post["video"]:
            self.bot.send_media_group(chat_id=self.chat_id, media=post["photo"] + post["video"])
        if post["text"]:
            self.bot.send_message(chat_id=self.chat_id, text=post["text"])
        if post["doc"]:
            self.bot.send_media_group(chat_id=self.chat_id, media=post["doc"])


# Launch bot's loop and handlers
def launch(bot, chat_id, posts_stream: Queue):
    print("Launching: TG listener")
    commands = Commands(chat_id, bot)

    try:
        handlers = Thread(target=bot.infinity_polling, daemon=True)
        handlers.start()
    except Exception as ex:
        print(ex)

    while True:
        c = commands.publish_post(posts_stream.get(True))
        print(c)
