import discord
from discord.ext import commands 

class botmanagement(commands.Cog):
    PostThreshold = 0.33
    World = "Exodus"
    Region = "North-America"
    Ping = False

    def __init__(self,bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(botmanagement(bot))