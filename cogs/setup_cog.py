import discord
from discord.ext import commands

class Setup(commands.Cog):   
    def __init__(self, bot):         
        self.bot = bot

    @commands.Cog.listener()            # Event on_ready tells how long it takes for the bot to be able to start as well as know when it's ready
    async def on_ready(self):
        print(f'Bot is ready after {round(self.bot.latency * 1000)} ms')

    @commands.command(aliases = ['ping'])
    async def check_latency(self, ctx):
        print(f'Bot is ready after {round(self.bot.latency*1000)} ms')

def setup(bot):
    bot.add_cog(Setup(bot))
