import discord
from discord.ext import commands
from utils import utils
from pprint import pprint

from . import helpcommands


class HelpCog(commands.Cog, name="Help"):
    """
    Help stuff
    """

    def __init__(self, bot, botConf):
        self.bot = bot
        self.botConf = botConf

    @commands.command(name="help", pass_context=True, brief="(module name)", description="Sends the global help message or the help of a specified module")
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def help(self, ctx, *module):
        if not isinstance(module, list) and not isinstance(module, tuple):
            module = [module]
        embed = await helpcommands.help(ctx, self.bot, self.botConf, module=module)
        await utils.send_embed(ctx, embed)

    @commands.command(name="invite", pass_context=True, hidden=True, description="(owner only) creates and invite for the bot")
    @commands.is_owner()
    async def invite(self, ctx):
        await ctx.send(await helpcommands.invite(self.botConf['id']), delete_after=5)

    @commands.command(name="ping", pass_context=True, description="Pings the bot")
    async def ping(self, ctx):
        await ctx.send('Pong! {0}ms'.format(round(self.bot.latency*1000, 3)))
        a = 1/0

def setup(bot):
    bot.add_cog(HelpCog(bot))
