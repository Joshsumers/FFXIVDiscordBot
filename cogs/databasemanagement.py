import discord
import pandas as pd
from discord.ext import commands 

class databasemanagement(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    def QueryDatabase() -> pd.DataFrame:

        return df


def setup(bot):
    bot.add_cog(databasemanagement(bot))