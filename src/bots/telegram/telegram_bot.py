# Using https://pytba.readthedocs.io/en/latest/index.html
import telebot
from json import load

# Reading configs.json into config (token)
with open("telegram/config.json", "r") as config_file:
	config = load(config_file)

bot = telebot.TeleBot(config["token"])


# Adding functions to the bot

@bot.message_handler(commands=["ping", "Ping"]) # This function is called on the "ping" and "Ping" commands
def Ping(message):
	bot.reply_to(message, "pong")


# Launching function
def launch():
	bot.infinity_polling()


if __name__ == "__main__":
	launch()