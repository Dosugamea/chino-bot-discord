from discord.ext import commands
from .lib.weather_client import WeatherClient


class WeatherCog(commands.Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.weather_client = WeatherClient(config.weather_endpoint)

    @commands.command("今日の天気")
    async def now_weather(self, ctx, arg):
        if arg is None:
            await ctx.send("引数に天気を入力してください。")
            return
        resp = self.weather_client.get_weather(arg)
        await ctx.send(resp)
