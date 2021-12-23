import os

# discord
import discord
from discord.ext import commands

# utils
from utils import utils
# conf
import configparser


# dev/pro
profile = 'dev'

def addCogs(bot):
    # bot.add_cog(Cog(bot,*))
    pass


def startBot(conf):
    intents = discord.Intents.default()
    intents.members = True
    activity = utils.getBotActivity(
        conf['bot']['activity_type'], conf['bot']['avtivity_msg'], url=conf['bot']['streaming_url'])
    status = utils.getBotStatus(conf['bot']['status'])
    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(conf['bot']['prefix']), activity=activity, status=status, help_command=None, intents=intents,case_insensitive=True)

    @ bot.event
    async def on_ready():
        print('------')
        print('Logged in as')
        print(bot.user.name + "#" + bot.user.discriminator)
        print(bot.user.id)
        print('------')

    @ bot.check
    def check_commands(ctx):
        infor = f"{ctx.message.created_at} -> {ctx.message.author} <{ctx.message.author.id}> in '{ctx.guild} <{ctx.guild.id}>': {ctx.message.content}"
        # utils.addToLog(ctx.message.created_at, ctx.message.author,
        # ctx.message.author.id, ctx.guild, ctx.guild.id, ctx.message.content)
        return ';' not in ctx.message.content

    addCogs(bot)
    # start the bot
    bot.run(conf['bot']['token'])


def getConf():
    conf = configparser.ConfigParser()
    pyProfile = os.environ.get('PYTHON_PROFILE', profile)
    conf.read(os.path.join('conf', f'conf-{pyProfile}.conf'))
    return conf


if __name__ == '__main__':
    conf = getConf()
    startBot(conf)
