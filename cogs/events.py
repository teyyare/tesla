import discord
from discord import Activity
from datetime import datetime
from utils.db import Database
from discord.ext import commands
from discord.ext.commands import errors


numbers = {
    "1️⃣": 1,
    "2️⃣": 2,
    "3️⃣": 3,
    "4️⃣": 4,
    "5️⃣": 5,
    "6️⃣": 6,
    "7️⃣": 7,
    "8️⃣": 8,
    "9️⃣": 9,
}


def setup(bot):
    bot.add_cog(Events(bot))


class Project:
    author = object
    description = str
    vote = int
    url = str


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.db = Database(self.config["firebase"])

    async def reaction_check(self, payload):
        user_reaction_count = 0

        channel = self.bot.get_channel(self.db.get("vote_channel_id"))
        message = await channel.fetch_message(payload.message_id)

        if payload.emoji.name in [_ for _ in numbers.keys()]:
            for r in message.reactions:
                user = await r.users().flatten()

                if payload.user_id in [_.id for _ in user]:
                    user_reaction_count += 1

                if user_reaction_count > 1:
                    await r.clear()
                    return
        else:
            pass

    async def manage_message(self, payload):
        projects = []
        content = ""

        _sum = 0
        reaction_count = 0

        channel = self.bot.get_channel(self.db.get("vote_channel_id"))
        messages = await channel.history(limit=None).flatten()

        for message in messages:
            if len(message.reactions) <= 0:
                continue

            for r in message.reactions:
                reaction_count += r.count
                _sum += numbers[r.emoji] * r.count

            p = Project()
            p.author = message.author
            p.description = message.content
            p.vote = _sum / reaction_count
            p.url = message.jump_url
            projects.append(p)

            _sum = 0
            reaction_count = 0

        newlist = sorted(projects, key=lambda x: x.vote, reverse=True)[0:10]

        for p in newlist:
            content += f"**{newlist.index(p) + 1}** [{p.description}]({p.url}) • Vote: `{p.vote}`\n"

        embed = discord.Embed(color=self.bot.embed_color)
        embed.title = "Projects"
        embed.description = content

        output_channel_id = self.db.get("output_channel_id")
        output_message_id = self.db.get("output_message_id")
        output_channel = self.bot.get_channel(output_channel_id)

        if output_message_id == None:
            output_message = await output_channel.send(embed=embed)
            self.db.update({"output_message_id": output_message.id})
        else:
            output_message = await output_channel.fetch_message(
                output_message_id
            )
            await output_message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.bot.uptime = datetime.now()

        print(
            f"{self.bot.user} (ID: {self.bot.user.id})\n"
            f"discord.py version: {discord.__version__}"
        )

        if self.config["status_type"] == "idle":
            status_type = discord.Status.idle
        elif self.config["status_type"] == "dnd":
            status_type = discord.Status.dnd
        else:
            status_type = discord.Status.online

        if self.config["playing_type"] == "listening":
            playing_type = 2
        elif self.config["playing_type"] == "watching":
            playing_type = 3
        else:
            playing_type = 0

        await self.bot.change_presence(
            status=status_type,
            activity=Activity(type=playing_type, name=self.config["playing"]),
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_id = payload.guild_id
        channel_id = payload.channel_id
        message_id = payload.message_id

        if channel_id != self.db.get("vote_channel_id"):
            return

        await self.reaction_check(payload)
        await self.manage_message(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild_id = payload.guild_id
        channel_id = payload.channel_id
        message_id = payload.message_id

        if channel_id != self.db.get("vote_channel_id"):
            return

        await self.manage_message(payload)
