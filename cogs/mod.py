import discord
from discord.ext import commands


def setup(bot):
    bot.add_cog(Mod(bot))


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.command()
    async def clear(self, ctx, amount: int):
        channel = ctx.message.channel
        deleted = await channel.purge(limit=amount + 1)

        await ctx.send(f"`{len(deleted)-1}` message cleared.", delete_after=3.0)
