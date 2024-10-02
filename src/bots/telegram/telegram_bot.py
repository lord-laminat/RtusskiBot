# Using https://pytba.readthedocs.io/en/latest/index.html
from time import sleep
from json import load, dump
from queue import Queue
from threading import Thread
import asyncio

from aiogram import Router, Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import Command


router = Router()


@router.message(Command("ping"))
async def ping(message: Message):
    await message.reply("pong")


async def main(token):
    dp = Dispatcher()
    dp.include_router(router)

    bot = Bot(token=token)

    await dp.start_polling(bot, handle_signals=False)


def launch(config):
    print("launching telebot listener")
    asyncio.run(main(config.tgbot.token))
