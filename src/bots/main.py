import asyncio
import logging
import os

import asyncpg

from bots.telegram import telegram_bot
from bots.vk import vkontakte_bot
from bots.config import load_db_config, load_tg_config, load_vk_config

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(module)s %(name)s)', level=logging.INFO)
logging.info('starting app')


async def get_db_connection_pool(uri):
    pool = await asyncpg.create_pool(uri)
    return pool


async def launch():
    config_path = os.environ.get('BOT_CONFIG_PATH', '/etc/botconf.toml')
    tg_config = load_tg_config(config_path)
    vk_config = load_vk_config(config_path)
    db_config = load_db_config(config_path)

    connection_pool = await get_db_connection_pool(db_config.connection_uri)

    tg_posts = asyncio.Queue()
    vk_posts = asyncio.Queue()

    # vkbot = asyncio.create_task(vkontakte_bot.main(vk_config, vk_posts, tg_posts))

    tgbot = asyncio.create_task(
        telegram_bot.main(tg_config, tg_posts, vk_posts, connection_pool)
    )
    await asyncio.gather(tgbot)  # , tgbot)


def main():  # script in pyproject.toml
    asyncio.run(launch())


if __name__ == '__main__':
    main()
