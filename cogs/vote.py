import discord
from utils.db import Database
from discord.ext import commands


def setup(bot):
    bot.add_cog(Vote(bot))


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(self.bot.config["firebase"])

    @commands.guild_only()
    @commands.command(name="output-channel")
    async def output_channel(self, ctx):
        channel_id = self.db.get("output_channel_id")
        channel = self.bot.get_channel(channel_id)

        if channel == None:
            return await ctx.send("Invalid channel.")

        await ctx.send(
            f"Output channel: {channel.mention} (ID: `{channel_id}`)"
        )

    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.command(name="set-output-channel")
    async def set_output_channel(self, ctx, channel: discord.TextChannel):
        self.db.update({"output_channel_id": channel.id})

        await ctx.send(f"Output channel set.")

    @commands.guild_only()
    @commands.command(name="vote-channel")
    async def vote_channel(self, ctx):
        channel_id = self.db.get("vote_channel_id")
        channel = self.bot.get_channel(channel_id)

        if channel == None:
            return await ctx.send("Invalid channel.")

        await ctx.send(f"Vote channel: {channel.mention} (ID: `{channel_id}`)")

    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.command(name="set-vote-channel")
    async def set_vote_channel(self, ctx, channel: discord.TextChannel):
        self.db.update({"vote_channel_id": channel.id})

        await ctx.send(f"Vote channel set.")

    @commands.guild_only()
    @commands.command(name="ending-project-channel")
    async def ending_project_channel(self, ctx):
        channel_id = self.db.get("ending_project_channel_id")
        channel = self.bot.get_channel(channel_id)

        if channel == None:
            return await ctx.send("Invalid channel.")

        await ctx.send(
            f"Ending project channel: {channel.mention} (ID: `{channel_id}`)"
        )

    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.command(name="set-ending-project-channel")
    async def set_ending_project_channel(
        self, ctx, channel: discord.TextChannel
    ):
        self.db.update({"ending_project_channel_id": channel.id})

        await ctx.send(f"Ending project channel set.")
