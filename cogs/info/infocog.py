import discord
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
        descriptions['randomTeam'] = 'Gives you a random team with 4 units'
        descriptions['randomUnit'] = 'Gives you a random unit or the specified ammount of them'
        descriptions['deleteGear'] = 'Removes a gear from the specified unit'
        return descriptions

    descriptions = getDescriptions()

    @commands.check
    def userInAuthPpl(ctx):
        return ctx.author.id in infocogconf.authedUsers.values()

    @commands.command(name="teamInfo", aliases=['tinfo'], pass_context=True, brief="<teamName>", description=descriptions.get('teamInfo'))
    @commands.check_any(commands.is_owner(), commands.has_any_role(*infocogconf.authedRoles.values()))
    async def teamInfo(self, ctx, *teamName):
        if isinstance(teamName, (list, tuple)):
            teamName = ' '.join(teamName)
        print(teamName)
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
    async def charaInfo(self, ctx, *charaName):
        if isinstance(charaName, (list, tuple)):
            charaName = ' '.join(charaName)
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
                await utils.send_embed(ctx, utils.errorEmbed('No character found'))
                return
            embed = infocommands.getEmbedFromChara(self.con, team)
        await utils.send_embed(ctx, embed)
        return team

    @commands.command(name="listTeams", aliases=['teams'], pass_context=True, description=descriptions.get('listTeams'))
    @commands.check_any(commands.is_owner(), commands.has_any_role(*infocogconf.authedRoles.values()))
    async def listTeams(self, ctx):
        await utils.send_embed(ctx, infocommands.allTeamsEmbed(self.con))

    @commands.command(name="addTeam", pass_context=True, description=descriptions.get('addteam'))
    @commands.check_any(userInAuthPpl, commands.has_any_role(*infocogconf.editRoles.values()))
    async def addTeam(self, ctx):
        team = await infocommands.create_team(ctx, self.bot, self.con, self.picChannelId)
        if not team:
            return
        await utils.send_embed(ctx, infocommands.getTeamEmbed(self.con, team))
        msg = 'The team showed above will be added. All good?'
        confirmation = await infocommands.condition_accepted(ctx, self.bot, msg)
        if confirmation:
            infocommands.add_team_to_db(self.con, team)
            await utils.send_embed(ctx, utils.successEmbed('Team added'))
        else:
            await utils.send_cancel_msg(ctx)

    @commands.command(name="editTeam", pass_context=True, brief="<teamName>", description=descriptions.get('editteam'))
    @commands.check_any(userInAuthPpl, commands.has_any_role(*infocogconf.editRoles.values()))
    async def editTeam(self, ctx, *teamName):
        if isinstance(teamName, (list, tuple)):
            teamName = ' '.join(teamName)
        team = await self.teamInfo(ctx, teamName)
        if not team:
            return
        
        team = await infocommands.edit_team(ctx, self.bot, self.con, self.picChannelId, team)
        if team:
            embed = infocommands.getTeamEmbed(self.con, team)
            await utils.send_embed(ctx, embed)
            msg = f'The team ***{team.name}*** will be edited into the shown data. All good?'
            confirmation = await infocommands.condition_accepted(ctx, self.bot, msg)
            if confirmation == True:
                infocommands.edit_team_in_db(self.con, team)
                await utils.send_embed(ctx, utils.successEmbed('Team edited'))
            else:
                await utils.send_cancel_msg(ctx)

    @commands.command(name="addName", pass_context=True, brief="<targetChara>", description=descriptions.get('addName'))
    @commands.check_any(userInAuthPpl, commands.has_any_role(*infocogconf.editRoles.values()))
    async def addName(self, ctx, targetChara):
        chara = await self.charaInfo(ctx, targetChara)
        if not chara:
            return
        newCharaName = await infocommands.get_new_chara_name(ctx, self.bot, self.con, chara)
        if not newCharaName:
            return
        msg = f'The name ***{newCharaName}*** will be edited into **{chara.names[0]}**. All good?'
        confirmation = await infocommands.condition_accepted(ctx, self.bot, msg)
        if confirmation:
            infocommands.add_chara_name(self.con, chara, newCharaName)
            await utils.send_embed(ctx, utils.successEmbed('Name Added'))
        else:
            await utils.send_cancel_msg(ctx)

    @commands.command(name="addGear", pass_context=True, brief="<targetChara>", description=descriptions.get('addGear'))
    @commands.check_any(userInAuthPpl, commands.has_any_role(*infocogconf.editRoles.values()))
    async def addGear(self, ctx, targetChara):
        chara = await self.charaInfo(ctx, targetChara)
        if not chara:
            return
        gear = await infocommands.create_gear(ctx, self.bot, chara)
        if not gear:
            return
        print('asdfasdf')
        bonuses = '/'.join(gear.bonus)
        rolls = ', '.join(gear.rolls)
        gearInfo = f'=> {bonuses} ({rolls})'
        msg = f'The gear ***{gearInfo}*** will be edited into **{chara.names[0]}**. All good?'
        confirmation = await infocommands.condition_accepted(ctx, self.bot, msg)
        if confirmation:
            infocommands.add_chara_gear(self.con, chara, gear)
            await utils.send_embed(ctx, utils.successEmbed('Gear Added'))
        else:
            await utils.send_cancel_msg(ctx)

    @commands.command(name="concatCharaImg", aliases=['concatImg'], pass_context=True, hidden=True)
    @commands.is_owner()
    async def concatCharaImg(self, ctx, *charas):
        charas = (' '.join(charas)).split(',')
        charaObjs = [infocommands.characterSearch(
            self.con, charaName)[0] for charaName in charas]
        img = infocommands.concatCharaPics(charaObjs)
        img = await utils.send_img(ctx, img)
        # await utils.send_msg(ctx, img.attachments[0].url)

    @commands.command(name="chadGearAdd", pass_context=True, hidden=True)
    @commands.is_owner()
    async def chadGearAdd(self, ctx, defaultGear):
        charaNames = await utils.getMsgFromUser(ctx, self.bot)
        if not charaNames or utils.cancelChecker(charaNames.content):
            return
        gear = infocommands.get_default_gear_from_name(defaultGear)
        if not gear:
            await utils.send_embed(ctx, utils.errorEmbed('Rip, Gear not found'))
            return
        charas = [infocommands.get_chara_from_id(
            self.con, charaName)for charaName in charaNames.content.split(',')]
        for chara in charas:
            infocommands.add_chara_gear(self.con, chara, gear)
        await utils.send_embed(ctx, utils.successEmbed('Gears Added'))

    @commands.command(name="checkGears", pass_context=True, hidden=True)
    @commands.is_owner()
    async def checkGears(self, ctx):
        charaNames = await utils.getMsgFromUser(ctx, self.bot)
        if not charaNames or utils.cancelChecker(charaNames.content):
            return
        charas = [infocommands.get_chara_from_id(
            self.con, charaName)for charaName in charaNames.content.split(',')]
        for chara in charas:
            if len(chara.gear) > 0:
                await utils.send_msg(ctx, msg=chara.name)
        await utils.send_embed(ctx, utils.successEmbed('Finished scanning'))

    @commands.command(name="FixNames", pass_context=True, hidden=True)
    @commands.is_owner()
    async def fixNames(self, ctx):
        if infocommands.fix_chara_names(self.con):
            await utils.send_embed(ctx, utils.successEmbed('Finished Fixing'))

    @commands.command(name="randomTeam", aliases=['rteam', 'ranteam'], brief='(numRerolls)', pass_context=True, description=descriptions.get('randomTeam'))
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def randomTeam(self, ctx, rerolls: int = 0):
        if rerolls > 7:
            await utils.send_embed(ctx, embed=utils.errorEmbed('Thats a bit to much ma boi'))
            return
        randTeam, queue = infocommands.get_random_team(
            self.con, rerollable=True)
        img = infocommands.concatCharaPics(randTeam)
        url = await utils.send_img(ctx, img, channel=self.bot.get_channel(self.picChannelId))
        embed = discord.Embed(title='Here it is, an epic random team',
                              color=discord.Color.blurple())
        embed.set_image(url=url.attachments[0].url)
        embed.set_footer(
            text=f'Requested by {ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar.url)
        msg = await utils.send_embed(ctx, embed)
        if rerolls > 0:
            await infocommands.charaReroller(self.bot, ctx, msg, embed, randTeam, queue, rerolls, self.bot.get_channel(self.picChannelId))

    @commands.command(name="randomUnit", aliases=['runit', 'ranunit'], pass_context=True, brief="(ammount)", description=descriptions.get('randomUnit'))
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def randomUnit(self, ctx, ammount: int = 1):
        if ammount < 1:
            await utils.send_embed(ctx, utils.errorEmbed('That num kinda sus man'))
            return
        elif ammount > 20:
            await utils.send_embed(ctx, utils.errorEmbed('Isn\'t that a bit too much'))
            return
        # elif ammount % 4 != 0:
        #     await utils.send_embed(ctx, utils.errorEmbed('For now only multiples of 4 pls'))
        #     return
        charas = infocommands.get_random_charas(self.con, ammount)
        img = infocommands.get_img_for_charas(charas)
        url = await utils.send_img(ctx, img, channel=self.bot.get_channel(self.picChannelId))
        embed = discord.Embed(title='Here you have sir',
                              color=discord.Color.blurple())
        embed.set_image(url=url.attachments[0].url)
        embed.set_footer(
            text=f'Requested by {ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar.url)
        await utils.send_embed(ctx, embed)

    @commands.command(name="deleteGear", aliases=['dGear', 'rGear', 'removeGear'], pass_context=True, brief="<Character>", description=descriptions.get('deleteGear'))
    @commands.check_any(userInAuthPpl, commands.has_any_role(*infocogconf.editRoles.values()))
    async def deleteGear(self, ctx, charaName):
        if isinstance(charaName, (list, tuple)):
            charaName = ' '.join(charaName)
        chara = await self.charaInfo(ctx, charaName)
        if not chara:
            return
        gearToDelete = await infocommands.get_gear_to_delete(ctx, self.bot, chara)
        if isinstance(gearToDelete, (list, tuple)):
            msg = f'All the gears for {chara.names[0]} will be deleted'
        else:
            msg = f'{gearToDelete.get_gear_short_data()}\nwill be deleted from {chara.names[0]}'
            gearToDelete = [gearToDelete]
        confirmation = await infocommands.condition_accepted(ctx, self.bot, msg)
        if confirmation:
            for gear in gearToDelete:
                infocommands.del_chara_gear(self.con, chara, gear)
            await utils.send_embed(ctx, utils.successEmbed('Gear Deleted'))
        else:
            await utils.send_cancel_msg(ctx)


def setup(bot):
    bot.add_cog(InfoCog(bot))
