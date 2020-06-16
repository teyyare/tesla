import sys
import discord
import humanize
from datetime import datetime
from utils.db import Database
from utils.ytda import YouTubeDataAPI
from discord.ext import commands, tasks


def setup(bot):
    bot.add_cog(Youtube(bot))


class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.db = Database(self.config["firebase"])
        self.ytda = YouTubeDataAPI(self.bot, self.config["yt_api_key"])

        self.youtube_channel_id = self.db.get("youtube_channel_id")
        self.statistics_channel_id = self.db.get("statistics_channel_id")

        self.update_statistics.start()

    def naturaltime(self, date_time):
        native = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ")
        return humanize.naturaltime(native)

    async def send_or_edit(self, embed) -> None:
        statistics_message_id = self.db.get("statistics_message_id")
        channel = self.bot.get_channel(self.statistics_channel_id)

        if statistics_message_id == None:
            statistics_message = await channel.send(embed=embed)
            self.db.update({"statistics_message_id": statistics_message.id})
        else:
            statistics_message = await channel.fetch_message(
                statistics_message_id
            )
            await statistics_message.edit(embed=embed)

    def cog_unload(self):
        self.update_statistics.cancel()

    @tasks.loop(minutes=15.0)
    async def update_statistics(self):
        print("Tasks...")

        try:
            channel = await self.ytda.get_channel_statistics(
                self.youtube_channel_id
            )
            video = await self.ytda.get_last_video_statistics(
                self.youtube_channel_id
            )
            comment = await self.ytda.get_last_comment(self.youtube_channel_id)
        except Exception as e:
            print("Exception:", e)
            return

        snippet = channel["items"][0]["snippet"]
        statistics = channel["items"][0]["statistics"]
        video_id = video["items"][0]["id"]
        video_statistics = video["items"][0]["statistics"]
        top_level_comment = comment["items"][0]["snippet"]["topLevelComment"][
            "snippet"
        ]

        embed = discord.Embed(
            title=f"{snippet['title']} YouTube Channel Statistics",
            url="https://youtube.com/channel/{channel['items'][0]['id']}",
            color=self.bot.embed_color,
            timestamp=datetime.utcnow(),
        )

        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/teyyare/nepercos-artworks/"
            "master/logo/nepercos_circle1_color_800x800.png"
        )

        embed.description = (
            f"Video count: `{int(statistics['videoCount']):,d}`\n"
            f"Subscriber count: `{int(statistics['subscriberCount']):,d}`\n"
            f"View count: `{int(statistics['viewCount']):,d}`\n\n"
            # f"Published date: `{self.naturaltime(snippet['publishedAt'])}`"
        )

        embed.add_field(
            name=f"Latest Video ({self.naturaltime(video['publishedAt'])})",
            value=(
                f"Title: [{video['title']}](https://www.youtube.com/watch?v={video_id})\n\n"
                f"View count: `{int(video_statistics['viewCount']):,d}`\n"
                f"Like count: `{int(video_statistics['likeCount']):,d}`\n"
                f"Dislike count: `{int(video_statistics['dislikeCount']):,d}`"
            ),
            inline=False,
        )

        embed.add_field(
            name=f"Last Comment ({self.naturaltime(top_level_comment['publishedAt'])})",
            value=(
                f"Author: [{top_level_comment['authorDisplayName']}]"
                f"({top_level_comment['authorChannelUrl']})\n"
                f"{top_level_comment['textDisplay']}"
            ),
            inline=False,
        )

        embed.set_footer(text="Last update")

        await self.send_or_edit(embed)

    @update_statistics.before_loop
    async def before_printer(self):
        print("Waiting...")

        await self.bot.wait_until_ready()

    @update_statistics.error
    async def error_printer(self):
        log_channel = self.bot.get_channel(self.bot.log_channel_id)

        embed = discord.Embed(color=discord.Colour.red())
        embed.description = f"```{sys.stderr}```"

        await log_channel.send(embed=embed)

    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.group(invoke_without_command=True)
    async def yt(self, ctx):
        youtube_channel_id = self.db.get("youtube_channel_id")
        channel_id = self.db.get("statistics_channel_id")
        channel = self.bot.get_channel(channel_id)

        if channel == None:
            return await ctx.send("Invalid channel.")

        await ctx.send(
            f"YouTube channel ID: `{youtube_channel_id}`\n"
            f"Statistics channel: {channel.mention} (ID: `{channel_id}`)"
        )

    @yt.command(name="set-channel")
    async def set_channel(self, ctx, channel_id):
        self.db.update({"youtube_channel_id": channel_id})

        await ctx.send(f"YouTube channel set.")

    @yt.command(name="set-statistics-channel")
    async def set_statistics_channel(self, ctx, channel: discord.TextChannel):
        self.db.update({"statistics_channel_id": channel.id})

        await ctx.send(f"Statistics channel set.")
