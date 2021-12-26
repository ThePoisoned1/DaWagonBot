from re import search
from discord.ext import commands
from numpy import mat
from . import infocogconf, infocommands
from utils import utils
from pprint import pprint


class InfoCog(commands.Cog, name="GwTeams"):
    """
    Character and Teams info related commands
    """

    def __init__(self, bot, con, picChanelId):
        self.bot = bot
        self.con = con
        self.picChannelId = int(picChanelId)

    def getDescriptions():
        descriptions = {}
        descriptions['teamInfo'] = 'Shows the info of the specified team'
        descriptions['charaInfo'] = 'Shows the info of the specified chara'
        descriptions['listTeams'] = 'Shows a list with all the registered teams'
        return descriptions

    descriptions = getDescriptions()

    def userInAuthPpl(ctx):
        return ctx.author.id in infocogconf.authedUsers.values()

    @commands.command(name="teamInfo", aliases=['tinfo'], pass_context=True, brief="<teamName>", description=descriptions.get('teamInfo'))
    async def teamInfo(self, ctx, *teamName):
        teamName = ' '.join(teamName)
        team = None
        matches = infocommands.teamSearch(self.con, teamName)
        if len(matches) == 1:
            embed = infocommands.getTeamEmbed(self.con, matches[0])
            team = matches[0]
        elif len(matches) < 1:
            embed = utils.errorEmbed('No team found')
        else:
            await utils.send_embed(ctx, infocommands.teamSearchResultEmbed(matches, teamName))
            msg = await utils.getMsgFromUser(ctx, self.bot)
            if not msg or utils.cancelChecker(msg.content):
                await utils.send_msg(ctx, msg='Operation canceled')
                return
            matches = infocommands.teamSearch(self.con, msg.content)
            if matches:
                team = matches[0]
            else:
                await utils.errorEmbed('No team found')
                return
            embed = infocommands.getTeamEmbed(self.con, team)
        await utils.send_embed(ctx, embed)
        return team

    @commands.command(name="charaInfo", aliases=['cinfo'], pass_context=True, brief="<unitname>", description=descriptions.get('charaInfo'))
    async def charaInfo(self, ctx, charaName):
        matches = infocommands.characterSearch(self.con, charaName)
        if len(matches) == 1:
            embed = infocommands.getEmbedFromChara(self.con, matches[0])
        elif len(matches) < 1:
            embed = utils.errorEmbed('No character found')
        else:
            await utils.send_embed(ctx, infocommands.searchResultEmbed(matches, charaName))
            msg = await utils.getMsgFromUser(ctx, self.bot)
            if not msg or utils.cancelChecker(msg.content):
                await utils.send_msg(ctx, msg='Operation canceled')
                return
            chara = infocommands.characterSearch(self.con, msg.content)
            if chara:
                chara = chara[0]
            else:
                await utils.errorEmbed('No character found')
                return
            embed = infocommands.getEmbedFromChara(self.con, chara)
        await utils.send_embed(ctx, embed)

    @commands.command(name="listTeams", aliases=['teams'], pass_context=True, description=descriptions.get('listTeams'))
    async def listTeams(self, ctx):
        await utils.send_embed(ctx, infocommands.allTeamsEmbed(self.con))

    @commands.command(name="concatCharaImg", aliases=['concatImg'], pass_context=True, description=descriptions.get('listTeams'))
    @commands.is_owner()
    async def concatCharaImg(self, ctx, *charas):
        charas = (' '.join(charas)).split(',')
        charaObjs = [infocommands.characterSearch(
            self.con, charaName)[0] for charaName in charas]
        img = infocommands.concatCharaPics(charaObjs)
        img = await utils.send_img(ctx, img)
        await utils.send_msg(ctx, img.attachments[0].url)

    @commands.command(name="addTeam", pass_context=True, description=descriptions.get('listTeams'))
    @commands.check(userInAuthPpl)
    async def addTeam(self, ctx):
        team = await infocommands.create_team(ctx, self.bot, self.con, self.picChannelId)
        if not team:
            return
        await utils.send_embed(ctx, infocommands.getTeamEmbed(self.con, team))
        infocommands.add_team_to_db(self.con, team)

    @commands.command(name="", pass_context=True, brief="<teamName>", description=descriptions.get('listTeams'))
    @commands.check(userInAuthPpl)
    async def editTeam(self, ctx, *teamName):
        team = await self.teamInfo(ctx, ' '.join(teamName))
        pprint(team)
        if not team:
            return
        team = await infocommands.edit_team(ctx, self.bot, self.con, self.picChannelId, team)
        if team:
            embed = infocommands.getTeamEmbed(self.con, team)
            await utils.send_embed(ctx, embed)
            infocommands.edit_team_in_db(self.con, team)


def setup(bot):
    bot.add_cog(InfoCog(bot))
