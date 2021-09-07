from discord.ext import commands
from .lib.gochiira_client import GochiiraClient
import random
import discord


class GochiiraCog(commands.Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.gochiira = GochiiraClient(
            config.gochiira_token,
            config.gochiira_endpoint
        )
        self.cdn = config.gochiira_cdn

    @commands.command()
    async def chino(self, ctx):
        resp = self.gochiira.searchWithTag(id=1)["data"]["imgs"]
        resp = [r for r in resp if not r["nsfw"]]
        resp = random.choice(resp)
        embed = discord.Embed(
            title=resp["title"],
            url=resp["originUrl"],
            description=resp["artist"]["name"],
            color=0x7accff
        )
        embed.set_thumbnail(
            url=f"{self.cdn}/illusts/large/{resp['illustID']}.jpg"
        )
        embed.add_field(name="登録日", value=resp["date"], inline=False)
        embed.set_footer(text="Provided from Gochiira")
        await ctx.send(embed=embed)
