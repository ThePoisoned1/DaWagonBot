from discord.ext import commands
from utils import utils
import discord


async def invite(botId):
    return discord.utils.oauth_url(str(botId), permissions=discord.Permissions(2151017536))


async def help(ctx, bot, botConf, module=None):
    """Shows all modules of the bot"""
    prefix = botConf['prefix']
    version = botConf['version']
    owner = ""
    ownerId = int(botConf['owner_id'])
    ownerName = botConf['owner_name']

    # checks if cog parameter was given
    # if not: sending all modules and commands not associated with a cog
    if module and len(module) > 0:
        module = [" ".join(module)]
    if not module:
        # checks if owner is on this server - used to 'tag' owner
        owner = await ctx.guild.fetch_member(ownerId)
        if owner != None:
            owner = f"<@{ownerId}>"
        else:
            owner = ownerName

        # starting to build embed
        emb = discord.Embed(title='Commands and modules', color=discord.Color.blue(),
                            description=f'Use **{prefix}help (module)** to gain more information about that module')

        # iterating trough cogs, gathering descriptions
        cogs_desc = ''
        for cog in bot.cogs:
            if "DaStuff" not in cog and "CommandErrorHandler" not in cog:
                cogs_desc += f'__{cog}__: {bot.cogs[cog].description}\n'

        # adding 'list' of cogs to embed
        emb.add_field(name='Modules', value=cogs_desc, inline=False)

        # integrating trough uncategorized commands
        commands_desc = ''
        for command in bot.walk_commands():
            # if cog not in a cog
            # listing command if cog name is None and command isn't hidden
            if not command.cog_name and not command.hidden:
                commands_desc += f'{command.name} - {command.help}\n'

        # adding those commands to embed
        if commands_desc:
            emb.add_field(name='Not belonging to a module',
                          value=commands_desc, inline=False)

        # setting information about author
        emb.add_field(
            name="About", value=f"Bot developed by {owner}, based on discord.py.\n")
        emb.set_footer(text=f"Bot is running in verison {version}")

    # block called when one cog-name is given
    # trying to find matching cog and it's commands
    elif len(module) == 1:

        # iterating trough cogs
        for cog in bot.cogs:
            # check if cog is the matching one
            if cog.lower() == module[0].lower():
                # making title - getting description from doc-string below class
                emb = discord.Embed(title=f'{cog}', description=f"{bot.cogs[cog].description} - <required> (optional) [alias]",
                                    color=discord.Color.green())

                # getting commands from cog
                for command in bot.get_cog(cog).get_commands():
                    # if cog is not hidden
                    if not command.hidden:
                        aliases = command.aliases
                        if len(aliases) > 0:
                            aliases = '- [{}]'.format("|".join(aliases))
                        else:
                            aliases = ""
                        brief = command.brief
                        if not brief:
                            brief = ""
                        desc = command.description
                        if not desc:
                            desc = u'\u200B'
                        emb.add_field(
                            name=f"{prefix}{command.name} {brief} {aliases}".strip().replace("  ", " "), value=desc, inline=False)
                break

        # if input not found
        # yes, for-loops have an else statement, it's called when no 'break' was issued
        else:
            emb = discord.Embed(title="Tf man",
                                description=f"What do you mean by {module[0]}, is not a module",
                                color=discord.Color.orange())

    # too many cogs requested - only one at a time allowed
    else:
        emb = discord.Embed(title="It's a magical place.",
                            description="How did we end here",
                            color=discord.Color.red())
    return emb
