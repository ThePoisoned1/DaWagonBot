from discord.ext import commands
#from . import commands_file


class CogName(commands.Cog, name="Any name"):
    """
    x related commands
    """

    def __init__(self, bot):
        self.bot = bot
    
    def getDescriptions():
        descriptions={}
        descriptions['a']='b'
        return descriptions

    descriptions=getDescriptions()

    @commands.command(name="commandname", aliases=['alias1','alias2'], pass_context=True,brief="parameters needed",description=descriptions.get('a'))
    async def commandname(self,ctx):
        #get responses from the commands file
        pass

def setup(bot):
    bot.add_cog(CogName(bot))

#to add a cog import this file in main and:
#bot.add_cog(filename.CogName(bot))
