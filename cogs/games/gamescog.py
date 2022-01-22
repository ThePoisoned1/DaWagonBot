import discord
from discord.ext import commands

from . import Games


class GamesCog(commands.Cog, name="Games"):
    """
    Game related commands
    """
    def getDescriptions():
        descriptions = {}
        descriptions[
            "russianroulette"] = "Play russian roulette with you friends, what can go wrong"
        return descriptions
    descriptions = getDescriptions()

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="russianroulette", aliases=['rr', 'bang'], description=descriptions.get("russianroulette"), pass_context=True)
    async def russianRoulette(self, ctx):
        await Games.russianRoulette_(ctx, self.bot)

def setup(bot):
    bot.add_cog(GamesCog(bot))
