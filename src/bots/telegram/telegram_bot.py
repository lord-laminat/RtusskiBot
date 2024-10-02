# Using https://pytba.readthedocs.io/en/latest/index.html
from time import sleep
from json import load, dump
from queue import Queue
from threading import Thread

import telebot


# Reading configs.json into config (token)
with open("bots/telegram/config.json", "r") as config_file:
    config = load(config_file)

bot = telebot.TeleBot(config["token"])

# Adding functions to the bot


@bot.message_handler(commands=["register"])
def get_chat_id(message: telebot.types.Message):
    config["chat_id"] = message.chat.id
    with open("bots/telegram/config.json", "w") as file:
        dump(config, file)


# This function is called on the "ping" and "Ping" commands
@bot.message_handler(commands=["ping", "Ping"])
def ping(message):
    bot.reply_to(message, "pong")


def publish_post(post: map):
    if post["photo"] or post["video"]:
        #print(len(post["photo"]))
        #print(post["photo"])
        bot.send_media_group(chat_id=config["chat_id"], media=post["photo"]+post["video"])
    if post["text"]:
        bot.send_message(chat_id=config["chat_id"], text=post["text"])
    if post["doc"]:
        bot.send_media_group(chat_id=config["chat_id"], media=post["doc"])


# Launch bot's loop and handlers
def launch(posts_stream: Queue):
    print("Launching: TG bot")
    try:
        handlers = Thread(target=bot.infinity_polling, daemon=True)
        handlers.start()
    except Exception as ex:
        print(ex)

    # Если бот еще не знает chat_id
    if not config["chat_id"]:
        print("Bot was not registered. Send /register to solve this.")
        while not config["chat_id"]:
            pass

    while True:
        if not posts_stream.empty():
            publish_post(posts_stream.get())
        sleep(5)


# if __name__ == "__main__":
# 	launch(Queue())
