from discord.ext import commands
from utils import utils, databaseUtils
import os
import shutil
from datetime import datetime


class DaStuffCog(commands.Cog, name="DaStuff"):
    """
    DaPo's admin stuff
    """

    def __init__(self, bot, con, conf):
        self.bot = bot
        self.con = con
        self.conf=conf

    @commands.command(name="shutdown", pass_context=True, description="Shuts down the bot")
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down")
        self.con.close()
        await self.bot.logout()

    @commands.command(name="sqlexec", pass_context=True, brief='<sentence>', description="executes an sql sentence")
    @commands.is_owner()
    async def shutdown(self, ctx, *sentence):
        sentence = ' '.join(sentence)
        databaseUtils.customSQL(self.con, sentence)

    @commands.command(name="backup", pass_context=True, description="Backs up the dbs")
    @commands.is_owner()
    async def backup(self, ctx):
        fileFolder = self.conf['datatbase']['folder_path']
        backupFolder = self.conf['datatbase']['backup_folder']
        for file in os.listdir(fileFolder):
            if file.split('.')[-1] == 'sqlite3':
                fileName = file.split(
                    '.')[0]+'_'+str(datetime.utcnow().strftime('%Y%m%d'))+'.sqlite3'
                shutil.copy(os.path.join(fileFolder, file),
                            os.path.join(backupFolder, fileName))
        await utils.send_msg(ctx, msg='Backed up')



def setup(bot, con):
    bot.add_cog(DaStuffCog(bot, con))
