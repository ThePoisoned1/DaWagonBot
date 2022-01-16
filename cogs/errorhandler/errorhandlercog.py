from pprint import pprint
import discord
import traceback
import sys
from utils import utils
from discord.ext import commands


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot, logFile):
        self.bot = bot
        self.logFile = logFile

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.errors.RoleNotFound):
            await ctx.send('Could not find that role')
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                await ctx.send('I could not find that member. Please try again.')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Where is the {} parameter".format(error.param.name))

        elif isinstance(error, commands.NotOwner):
            await ctx.send("This command is restricted to the owner")

        elif isinstance(error, commands.CheckAnyFailure):
            await ctx.send('You didn\'t pass the test to use this')
        elif isinstance(error, commands.CheckFailure):
            if "global" in str(error):
                await ctx.send("Commands don't allow the usage of ';' ")
            elif isinstance(error, commands.errors.MissingAnyRole):
                await ctx.send('You don\'t have any of the required roles to use this')
            else:
                await ctx.send('You didn\'t pass the test to use this')
        elif isinstance(error, commands.CommandOnCooldown):
            await utils.send_embed(ctx, utils.errorEmbed(f'Command on cooldown, try again in {error.retry_after:.2f} sec'))
        else:
            log = open(self.logFile, 'a+', encoding='utf-8')
            print('Ignoring exception in command {}:'.format(
                ctx.command), file=log)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=log)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
