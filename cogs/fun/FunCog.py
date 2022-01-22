import imp
import discord
from discord.ext import commands
from utils import utils
from . import RandomCommands


class FunCog(commands.Cog, name="Fun"):
    """
    Fun commands
    """
    def getDescriptions():
        descriptions = {}
        descriptions[
            "8ball"] = "Ask the 8Ball"
        descriptions[
            "choose"] = "Let me choose an option do you (separate with \'|\')"
        descriptions["iq"] = "Shows yours or an user's iq"
        descriptions["ppsize"] = "Flex or cry about your or an user's pp"
        descriptions["avatar"] = "Gives you your avatar or the specified user's"
        descriptions["sus"] = "Just sus"
        descriptions["snipe"] = "Snipe those deleted messages"
        descriptions["editSnipe"] = "Any editted messages in the chat?"
        return descriptions
    descriptions = getDescriptions()

    def __init__(self, bot):
        self.bot = bot
        self.snipedMsgs = {}
        self.editSnipedMsgs = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        self.snipedMsgs[message.guild.id] = message

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        self.editSnipedMsgs[before.guild.id] = [before, after]

    @commands.command(name="8ball", aliases=['8b', 'ball'], brief="<question>", pass_context=True, description=descriptions.get("8ball"))
    async def eightBall(self, ctx, question):
        await utils.send_msg(ctx, RandomCommands.eightBall_())

    @commands.command(name="choose", aliases=['choice'], brief="<option1|option2|....>", pass_context=True, description=descriptions.get("choose"))
    async def choose(self, ctx, *options):
        await utils.send_msg(ctx, RandomCommands.choose_(" ".join(options)))

    @commands.command(name="iq", pass_context=True, brief="(user)", description=descriptions.get("iq"))
    async def iq(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.message.author
        await utils.send_msg(ctx, RandomCommands.iq_(user))

    @commands.command(name="ppsize", aliases=['pp'], brief="(user)", pass_context=True, description=descriptions.get("ppsize"))
    async def ppSize(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.message.author
        await utils.send_msg(ctx, RandomCommands.ppSize_(user))

    @commands.command(name="avatar", brief="(user)", pass_context=True, description=descriptions.get("avatar"))
    async def avatar(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.message.author
        await utils.send_msg(ctx, user.avatar_url)

    @commands.command(name="sus", pass_context=True, description=descriptions.get("sus"))
    async def sus(self, ctx):
        await utils.send_msg(ctx, RandomCommands.sus())

    @commands.command(name="snipe", pass_context=True, description=descriptions.get("snipe"))
    async def snipe(self, ctx):
        snipedMsg = self.snipedMsgs.get(ctx.guild.id)
        if not snipedMsg:
            embed = utils.info_embed('Nothing to snipe')
        else:
            embed = discord.Embed(
                title='Sniped', description=snipedMsg.content, color=discord.Color.red())
            embed.set_footer(
                text=f'{snipedMsg.author.name}#{snipedMsg.author.discriminator} ({utils.parseTime(snipedMsg.created_at)})', icon_url=snipedMsg.author.avatar.url)
        await utils.send_embed(ctx, embed)
    
    @commands.command(name="editSnipe", pass_context=True, description=descriptions.get("editSnipe"))
    async def editSnipe(self, ctx):
        snipedMsg = self.editSnipedMsgs.get(ctx.guild.id)
        if not snipedMsg:
            embed = utils.info_embed('Nothing to snipe')
        else:
            data = f'**Before:**\n{snipedMsg[0].content}\n**After**:\n{snipedMsg[1].content}'
            embed = discord.Embed(
                title='Sniped', description=data, color=discord.Color.red())
            embed.set_footer(
                text=f'{snipedMsg[0].author.name}#{snipedMsg[0].author.discriminator} ({utils.parseTime(snipedMsg[1].edited_at)})', icon_url=snipedMsg[0].author.avatar.url)
        await utils.send_embed(ctx, embed)


def setup(bot):
    bot.add_cog(FunCog(bot))
