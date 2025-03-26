import asyncio
import logging


from bots.telegram import telegram_bot
from bots.vk import vkontakte_bot

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(module)s %(name)s)', level=logging.INFO)
logging.info('starting app')


async def launch():
    tg_posts = asyncio.Queue()
    vk_posts = asyncio.Queue()

    vkbot = asyncio.create_task(vkontakte_bot.main(vk_posts, tg_posts))

    tgbot = asyncio.create_task(telegram_bot.main(tg_posts, vk_posts))
    await asyncio.gather(vkbot, tgbot)


def main():  # script in pyproject.toml
    asyncio.run(launch())


if __name__ == '__main__':
    main()
