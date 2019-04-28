"""
Filename: simbot.py
Author:   contact@simshadows.com
"""

import sys
import asyncio

from discord import Client # python3 -m pip install -U discord.py[voice]

from .utils_logging import get_new_logger

logger = get_new_logger(__name__)


class Simbot(Client):

    async def on_ready(self):
        logger.info(f"Logged in as {self.user.name}, with User ID {self.user.id}.")
        return

    async def on_message(self, msg):
        if msg.content == "!hello":
            logger.info("I just got greeted by a kind user! <3")
            await msg.channel.send("Hello, World!")
        return


async def start_client(token):
    client = Simbot()
    await client.login(token)
    await client.connect(reconnect=False)
    return


def run(config):
    bot_login_token = config["bot_login_token"]
    if not isinstance(bot_login_token, str):
        raise TypeError("Bot login token must be a string.")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_client(bot_login_token))
    finally:
        try:
            loop.close()
        except:
            pass
    return 0

