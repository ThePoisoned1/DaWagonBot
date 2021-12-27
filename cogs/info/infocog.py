from discord.ext import commands
from . import infocogconf, infocommands
from utils import utils
from pprint import pprint


class InfoCog(commands.Cog, name="GcInfo"):
    """
    Info about characters and teams in 7DSGC
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
        descriptions['addteam'] = 'Adds a team to the database'
        descriptions['editteam'] = 'Edits a team in the database'
        descriptions['addName'] = 'Adds a name to the AKA section of the character'
        descriptions['addGear'] = 'Adds a Gear Set to a characer'
        return descriptions

    descriptions = getDescriptions()

    def userInAuthPpl(ctx):
        return ctx.author.id in infocogconf.authedUsers.values()

    @commands.command(name="teamInfo", aliases=['tinfo'], pass_context=True, brief="<teamName>", description=descriptions.get('teamInfo'))
    @commands.check_any(commands.is_owner(), commands.has_any_role(*infocogconf.authedRoles.values()))
    async def teamInfo(self, ctx, *teamName):
        teamName = ' '.join(teamName)
        team = None
        matches = infocommands.teamSearch(self.con, teamName)
        if len(matches) == 1:
            embed = infocommands.getTeamEmbed(self.con, matches[0])
            team = matches[0]
        elif len(matches) < 1:
            embed = utils.errorEmbed('No team found')
        elif len(matches) > 10:
            embed = utils.errorEmbed('Too much results for that bro')
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
    @commands.check_any(commands.is_owner(), commands.has_any_role(*infocogconf.authedRoles.values()))
    async def charaInfo(self, ctx, charaName):
        matches = infocommands.characterSearch(self.con, charaName)
        team = None
        if len(matches) == 1:
            embed = infocommands.getEmbedFromChara(self.con, matches[0])
            team = matches[0]
        elif len(matches) < 1:
            embed = utils.errorEmbed('No character found')
        elif len(matches) > 20:
            embed = utils.errorEmbed('Too much results for that bro')
        else:
            await utils.send_embed(ctx, infocommands.searchResultEmbed(matches, charaName))
            msg = await utils.getMsgFromUser(ctx, self.bot)
            if not msg or utils.cancelChecker(msg.content):
                await utils.send_msg(ctx, msg='Operation canceled')
                return
            chara = infocommands.characterSearch(self.con, msg.content)
            if chara:
                team = chara[0]
            else:
                await utils.errorEmbed('No character found')
                return
            embed = infocommands.getEmbedFromChara(self.con, team)
        await utils.send_embed(ctx, embed)
        return team

    @commands.command(name="listTeams", aliases=['teams'], pass_context=True, description=descriptions.get('listTeams'))
    @commands.check_any(commands.is_owner(), commands.has_any_role(*infocogconf.authedRoles.values()))
    async def listTeams(self, ctx):
        await utils.send_embed(ctx, infocommands.allTeamsEmbed(self.con))

    @commands.command(name="addTeam", pass_context=True, description=descriptions.get('addteam'))
    @commands.check(userInAuthPpl)
    async def addTeam(self, ctx):
        team = await infocommands.create_team(ctx, self.bot, self.con, self.picChannelId)
        if not team:
            return
        await utils.send_embed(ctx, infocommands.getTeamEmbed(self.con, team))
        #infocommands.add_team_to_db(self.con, team)

    @commands.command(name="editTeam", pass_context=True, brief="<teamName>", description=descriptions.get('editteam'))
    @commands.check(userInAuthPpl)
    async def editTeam(self, ctx, *teamName):
        team = await self.teamInfo(ctx, ' '.join(teamName))
        if not team:
            return
        team = await infocommands.edit_team(ctx, self.bot, self.con, self.picChannelId, team)
        if team:
            embed = infocommands.getTeamEmbed(self.con, team)
            await utils.send_embed(ctx, embed)
            infocommands.edit_team_in_db(self.con, team)

    @commands.command(name="addName", pass_context=True, brief="<targetChara>", description=descriptions.get('addName'))
    @commands.check(userInAuthPpl)
    async def addName(self, ctx, targetChara):
        chara = await self.charaInfo(ctx, targetChara)
        if not chara:
            return
        newCharaName = await infocommands.get_new_chara_name(ctx, self.bot, self.con, chara)
        infocommands.edit_chara_names(self.con, chara, newCharaName)
        await utils.send_embed(ctx,utils.successEmbed('Name Added'))

    @commands.command(name="addGear", pass_context=True, brief="<targetChara>", description=descriptions.get('addGear'))
    @commands.check(userInAuthPpl)
    async def addGear(self, ctx, targetChara):
        chara = await self.charaInfo(ctx, targetChara)
        if not chara:
            return
        gear = await infocommands.create_gear(ctx, self.bot, chara)
        infocommands.edit_chara_gears(self.con, chara, gear)
        await utils.send_embed(ctx,utils.successEmbed('Gear Added'))

    @commands.command(name="concatCharaImg", aliases=['concatImg'], pass_context=True, description=descriptions.get('listTeams'), hidden=True)
    @commands.is_owner()
    async def concatCharaImg(self, ctx, *charas):
        charas = (' '.join(charas)).split(',')
        charaObjs = [infocommands.characterSearch(
            self.con, charaName)[0] for charaName in charas]
        img = infocommands.concatCharaPics(charaObjs)
        img = await utils.send_img(ctx, img)
        # await utils.send_msg(ctx, img.attachments[0].url)


def setup(bot):
    bot.add_cog(InfoCog(bot))
