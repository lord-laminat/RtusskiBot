# Using https://discordpy.readthedocs.io/en/latest/index.html
import asyncio
import os
import logging
import requests

from discord import Client, File, Intents, Message

from bots.config import load_discord_config
from bots.common.content import Attachments

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

config = load_discord_config(os.getenv("BOTS_CONFIG_PATH"))

intents = Intents.default()
intents.message_content = True

client: Client = Client(
    command_prefix="/",
    intents=intents
)

class clientCommands:
    def __init__(self, client: Client, channel_id: int):
        self.client = client
        self.channel = None
        #logger.debug(*self.client.get_all_channels(), self.channel)

    async def send_messages(self, attachments: Attachments):
        # TODO add videos support
        # TODO split this function into smaller ones
        # basically you want to have thi behaviour:
        # text-only: paste text
        # attachment-with-text: use text as caption to attachment

        if attachments.text_only():
            print(*client.get_all_channels())
            await self.channel.send(content=attachments.text)
        else:
            # Getting files' bytes
            _files = []
            for attachment in attachments.documents + attachments.images + attachments.videos:
                response = requests.get(attachment.url)
                if response.status_code == 200:
                    _files.append(File(fp=response.content, filename=attachment.title))
                else: ...
            await self.channel.send(
                content=attachments.text,
                files=_files
            )

client_commands = clientCommands(client, config.channel_id)

@client.event
async def on_ready():
    global client_commands
    client_commands.channel = client.get_channel(config.channel_id)
    logger.debug(f"Current channel: '{client_commands.channel}'")


async def check_query(queue):
    while True:
        attachments = await queue.get()
        await client_commands.send_messages(attachments)


async def main(my_posts, tg_posts, vk_posts):
    #logger.info("starting the application")
    t1 = asyncio.create_task(check_query(my_posts))
    t2 = asyncio.create_task(client.start(token=config.token))
    await asyncio.gather(t1, t2)