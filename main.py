from discord.ext import commands
from cogs.gochiira import GochiiraCog
from cogs.weather import WeatherCog
import discord
import dataclasses


@dataclasses.dataclass
class Config:
    weather_endpoint: str
    gochiira_endpoint: str
    gochiira_token: str
    gochiira_cdn: str


class MyBot(commands.Bot):
    async def on_ready(self):
        print('-----')
        print(self.user.name)
        print(self.user.id)
        print('-----')

    async def on_command_error(self, error):
        if isinstance(error, commands.CommandNotFound):
            await self.send("**Invalid command. Try using** `help` **to figure out commands!**")
        if isinstance(error, commands.MissingRequiredArgument):
            await self.send('**Please pass in all requirements.**')
        if isinstance(error, commands.MissingPermissions):
            await self.send("**You don't have all the requirements or permissions for using this command :angry:**")
        embed = discord.Embed(title="エラー情報", description="", color=0xf00)
        embed.add_field(name="エラー発生サーバー名", value=self.guild.name, inline=False)
        embed.add_field(name="エラー発生サーバーID", value=self.guild.id, inline=False)
        embed.add_field(name="エラー発生ユーザー名", value=self.author.name, inline=False)
        embed.add_field(name="エラー発生ユーザーID", value=self.author.id, inline=False)
        embed.add_field(name="エラー発生コマンド", value=self.message.content, inline=False)
        embed.add_field(name="発生エラー", value=error, inline=False)
        await self.send(embed=embed)


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    load_dotenv()

    TOKEN = os.getenv('BOT_TOKEN')
    config = Config(
        weather_endpoint=os.getenv('WEATHER_ENDPOINT'),
        gochiira_endpoint=os.getenv('GOCHIIRA_ENDPOINT'),
        gochiira_token=os.getenv('GOCHIIRA_TOKEN'),
        gochiira_cdn=os.getenv('GOCHIIRA_CDN')
    )
    bot = commands.Bot(command_prefix='!')
    bot.add_cog(GochiiraCog(bot, config))
    bot.add_cog(WeatherCog(bot, config))
    bot.run(TOKEN)
