import json
import aiohttp
import discord
from os import environ as env
from discord.ext import commands
from collections import namedtuple as nt


config_file = "config.json"

description = """
Groups the votes added to the message
"""

extensions = [
    "cogs.mod",
    "cogs.info",
    "cogs.vote",
    "cogs.events",
    "cogs.youtube",
]


class Tesla(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.config["prefix"], description=description,
        )

        self.uptime = ""
        self.embed_color = 0xE28274
        self.log_channel_id = 720413610811064391

        self.session = aiohttp.ClientSession(loop=self.loop)

        for cog in extensions:
            try:
                self.load_extension(cog)
            except Exception as exc:
                print(f"{cog} {exc.__class__.__name__}: {exc}")

        self.load_extension("jishaku")

    @property
    def __version__(self):
        return "2.0"

    @property
    def owners(self):
        return [self.get_user(_) for _ in set(self.config["owners"])]

    @property
    def config(self):
        try:
            with open(config_file, encoding="UTF-8") as data:
                return json.load(data)

        except AttributeError:
            raise AttributeError("Unknown argument")

        except FileNotFoundError:
            config_dict = {}
            firebase = {}

            key_list = [
                "token",
                "prefix",
                "playing",
                "playing_type",
                "status_type",
                "yt_api_key",
            ]
            firebase_key_list = [
                "apiKey",
                "authDomain",
                "databaseURL",
                "storageBucket",
            ]

            for _ in key_list:
                if _ == "prefix":
                    config_dict[_] = env.get(_).split(",")
                else:
                    config_dict[_] = env.get(_)

            for _ in firebase_key_list:
                firebase[_] = env.get(_)

            config_dict["firebase"] = firebase

            return config_dict

    async def on_resumed(self):
        print("Resumed...")

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        super().run(self.config["token"], reconnect=True)
