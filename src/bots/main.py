import asyncio
import logging

from bots.telegram import telegram_bot
from bots.vk import vkontakte_bot

logger = logging.getLogger()
logger.setLevel(logging.INFO)


async def launch():
    tg_posts = asyncio.Queue()
    ds_posts = asyncio.Queue()
    vk_posts = asyncio.Queue()

    vkbot = asyncio.create_task(
        vkontakte_bot.main(vk_posts, tg_posts, ds_posts)
    )

    tgbot = asyncio.create_task(
        telegram_bot.main(tg_posts, ds_posts, vk_posts)
    )

    await asyncio.gather(vkbot, tgbot, return_exceptions=False)


def main():  # script in pyproject.toml
    asyncio.run(launch())
