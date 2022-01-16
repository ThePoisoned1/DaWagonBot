from discord.ext import commands
#from . import commands_file


class gwManagerCog(commands.Cog, name="GWManager"):
    """
    Commands to help guild leaders to manage GW
    """

    def __init__(self, bot, con):
        self.bot = bot
        self.con = con

    def getDescriptions():
        descriptions = {}
        descriptions['a'] = 'b'
        return descriptions

    descriptions = getDescriptions()

    @commands.command(name="commandname", aliases=['alias1', 'alias2'], pass_context=True, brief="parameters needed", description=descriptions.get('a'))
    async def commandname(self, ctx):
        # get responses from the commands file
        pass


def setup(bot):
    bot.add_cog(gwManagerCog(bot))

# to add a cog import this file in main and:
# bot.add_cog(filename.CogName(bot))
