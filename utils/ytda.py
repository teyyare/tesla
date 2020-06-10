class YouTubeDataAPI:
    def __init__(self, bot, api_key):
        self.session = bot.session
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3/"

    async def get(self, params):
        async with self.session.get(self.base_url + params) as resp:
            return await resp.json()

    async def get_channel_statistics(self, channel_id):
        params = f"channels?key={self.api_key}&id={channel_id}&part=snippet,statistics"

        return await self.get(params)

    async def get_video_statistics(self, video_id):
        params = f"videos?key={self.api_key}&id={video_id}&part=statistics"

        return await self.get(params)

    async def get_last_video_statistics(self, channel_id):
        params = f"search?key={self.api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=1"

        data = await self.get(params)
        video_id = data["items"][0]["id"]["videoId"]
        snippet = data["items"][0]["snippet"]

        video_statistics = await self.get_video_statistics(video_id)

        video_statistics["title"] = snippet["title"]
        video_statistics["publishedAt"] = snippet["publishedAt"]

        return video_statistics

    async def get_last_comment(self, channel_id):
        params = f"commentThreads?key={self.api_key}&part=snippet&allThreadsRelatedToChannelId={channel_id}&maxResults=1&textFormat=plainText"

        return await self.get(params)
