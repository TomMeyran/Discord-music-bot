import discord
from discord.ext import commands
from secrets import *

class Server(commands.Cog):             # this cog runs all things that need to work in the background
    def __init__(self, bot):         # all functions within the cog must have the self as first parameter and bot
        self.bot = bot

    maxCharacters = 2000

    def vcID(self, ctx, vcName): # returns voice channel id for the server
        # default voice channel for server, when vcName is empty
        if vcName == "":                                            # default channels
            if str(ctx.message.guild) == ch1 :
                return discord.utils.get(ctx.guild.voice_channels, name=vc1)  # gets the channel id with it's name
            elif str(ctx.message.guild) == ch2 :
                return discord.utils.get(ctx.guild.voice_channels, name=vc2)
            if str(ctx.message.guild) == ch3 :
                return discord.utils.get(ctx.guild.voice_channels, name=vc3)
        elif vc1_2.startswith(vcName) :                             # handles channels such that shortcuts could also be used
            return discord.utils.get(ctx.guild.voice_channels, name=vc1_2)
        elif vc2_2.startswith(vcName) :
            return discord.utils.get(ctx.guild.voice_channels, name=vc2_2)
        else:
            return discord.utils.get(ctx.guild.voice_channels, name=vcName)   # handles exact names of channels for all other servers



#    @commands.Cog.listener()            # Event on_ready tells how long it takes for the bot to be able to start as well as know when it's ready
#    async  def on_ready(self, ctx):
#        print('Bot is ready')

#    @commands.command()
#    async def bot.add_cog(Server(bot))     # adds the cog to the bot

def setup(bot):
    bot.add_cog(Server(bot))

