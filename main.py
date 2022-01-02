import os

# discord
import discord
from discord.ext import commands

# utils
from utils import utils, databaseUtils

# conf
import configparser

# cogs
from cogs.errorhandler import errorhandlercog
from cogs.help import helpcog
from cogs.info import infocog
from cogs.dastuff import dastuffcog

# database initializer
from database import startDatabase, customInteractions


def addCogs(bot, conf, con):
    bot.add_cog(errorhandlercog.CommandErrorHandler(bot))
    bot.add_cog(infocog.InfoCog(bot, con, conf['pictures']['channel_id']))
    bot.add_cog(dastuffcog.DaStuffCog(bot, con, conf))
    bot.add_cog(helpcog.HelpCog(bot, conf['bot']))


def connectDb(dbConf):
    exists = os.path.isfile(dbConf['path'])
    con = databaseUtils.connectToDb(dbConf['path'])
    if not exists:
        startDatabase.startDb(con)
    return con


def startBot(conf, update=False):
    intents = discord.Intents.default()
    intents.members = True
    activity = utils.getBotActivity(
        conf['bot']['activity_type'], conf['bot']['avtivity_msg'], url=conf['bot']['streaming_url'])
    status = utils.getBotStatus(conf['bot']['status'])
    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(conf['bot']['prefix']), activity=activity, status=status, help_command=None, intents=intents, case_insensitive=True)

    @ bot.event
    async def on_ready():
        print('------', file=conf['log']['path'])
        print('Logged in as', file=conf['log']['path'])
        print(bot.user.name + "#" + bot.user.discriminator,
              file=conf['log']['path'])
        print(bot.user.id, file=conf['log']['path'])
        print('------', file=conf['log']['path'])

    @ bot.check
    def check_commands(ctx):
        infor = f"{ctx.message.created_at} -> {ctx.message.author} <{ctx.message.author.id}> in '{ctx.guild} <{ctx.guild.id}>': {ctx.message.content}"
        print(infor, file=conf['log']['path'])
        # utils.addToLog(ctx.message.created_at, ctx.message.author,
        # ctx.message.author.id, ctx.guild, ctx.guild.id, ctx.message.content)
        return ';' not in ctx.message.content
    con = connectDb(conf['database'])
    if update:
        customInteractions.run_chara_update(
            con, conf['database']['chara_base_url'])
    addCogs(bot, conf, con)
    # start the bot
    bot.run(conf['bot']['token'])


def getConf(prf):
    conf = configparser.ConfigParser()
    pyProfile = os.environ.get('PYTHON_PROFILE', prf)
    conf.read(os.path.join('conf', f'conf-{pyProfile}.conf'))
    return conf


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Starts the discord bot')
    parser.add_argument('--update', '-u', action='store_true',
                        help='Runs a character update in the database')
    parser.add_argument('-dev', action='store_true',
                        help='Runs the bot with the development conf')
    args = parser.parse_args()
    profile = 'dev' if args.dev else 'pro'
    updateCharas = args.update
    conf = getConf(profile)
    startBot(conf, updateCharas)
