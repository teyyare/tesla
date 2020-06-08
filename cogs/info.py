import time
import discord
import humanize
from discord.utils import get
from discord.ext import commands


def setup(bot):
    bot.add_cog(Info(bot))


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_bot_uptime(self):
        # humanize.i18n.activate("tr_TR")
        return humanize.naturaldelta(self.bot.uptime)

    @commands.command()
    async def uptime(self, ctx):
        await ctx.send(f"Uptime: `{self.get_bot_uptime()}`")

    @commands.command()
    async def ping(self, ctx):
        before = time.monotonic()
        message = await ctx.send("Pinging...")
        ping = (time.monotonic() - before) * 1000

        await message.edit(content=f"Pong! `{ping:.2f}`ms")

    @commands.command()
    async def avatar(self, ctx, *, user: discord.Member = None):
        user = user or ctx.author

        embed = discord.Embed()
        avatar = user.avatar_url_as(static_format="png")
        embed.set_author(name=user)
        embed.set_image(url=avatar)

        await ctx.send(embed=embed)
