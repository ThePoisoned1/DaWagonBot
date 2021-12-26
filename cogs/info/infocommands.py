import discord
from discord import embeds
from numpy import mat
from utils import databaseUtils, utils
from database import customInteractions
from usefullobjects import objectParser, gcObjects
from pprint import pprint
buffer = {}


def getTeamApereance(con, unitId):
    if not buffer.get('teams'):
        updateBuffer(con)
    apereances = []
    for team in buffer['teams']:
        if unitId in team.unitNames:
            apereances.append(team.name)
        else:
            for val in team.replacements.values():
                if isinstance(val, (list, tuple)):
                    for charaId in val:
                        if charaId == unitId:
                            apereances.append(team.name)
                else:
                    if val == unitId:
                        apereances.append(team.name)
    return apereances


def getEmbedFromChara(con, chara: gcObjects.Character):
    embed = discord.Embed(title=chara.customName,
                          description=chara.unitName, color=discord.Color.purple())
    embed.set_thumbnail(url=chara.imageUrl)
    embed.add_field(name='AKA', value=', '.join(chara.names), inline=False)
    embed.add_field(name='Rarity', value=chara.rarity)
    embed.add_field(name='Attribute', value=chara.attribute)
    embed.add_field(name='Race', value=', '.join(chara.race))
    embed.add_field(name='Passive', value=chara.passive, inline=False)
    if chara.commandment:
        embed.add_field(name='Commandment',
                        value=chara.commandment, inline=False)
    if chara.grace:
        embed.add_field(name='Grace', value=chara.grace, inline=False)
    if chara.relic:
        embed.add_field(name='Holy Relic', value=chara.relic, inline=False)
    equipData = '\n'.join([gear.getGearData() for gear in chara.gear])
    embed.add_field(name='Skills', value=chara.getSkillData())
    embed.add_field(name='Gear', value=equipData if len(
        equipData) > 0 else 'No sets registered')
    teamApereances = '\n'.join(
        f'-{teamName}' for teamName in getTeamApereance(con, chara.name))
    if len(teamApereances) > 0:
        embed.add_field(name='GW Teams its used in',
                        value=teamApereances, inline=False)
    embed.add_field(name='Database Link',
                    value=f'[{chara.charaUrl}]({chara.charaUrl})', inline=False)
    return embed


def teamSearchResultEmbed(matches, search):
    seaches = '\n'.join(f'-{team.name}'for team in matches)
    embed = discord.Embed(
        title=f'Search results for "{search}"', description=seaches, color=discord.Color.dark_blue())
    embed.set_footer(text='Type one of the options above')
    return embed


def searchResultEmbed(matches, search):
    seaches = '\n'.join(f'-{chara.names[0]}'for chara in matches)
    embed = discord.Embed(
        title=f'Search results for {search}', description=seaches, color=discord.Color.dark_blue())
    embed.set_footer(text='Type one of the options above')
    return embed


def allTeamsEmbed(con):
    if not buffer.get('teams'):
        updateBuffer(con)
    teamNames = '\n'.join([f'-{team.name}' for team in buffer['teams']])
    embed = discord.Embed(
        title=f'Showing all saved teams', description=teamNames, color=discord.Color.dark_blue())
    return embed


def teamSearch(con, search: str):
    if not buffer.get('teams'):
        updateBuffer(con)
    search = search.lower()
    matches = []
    for team in buffer['teams']:
        if team.name.lower() == search:
            return [team]
        elif any(search in name.lower() for name in team.otherNames):
            matches.append(team)
    return matches


def characterSearch(con, search: str):
    if not buffer.get('charas'):
        updateBuffer(con)
    matches = []
    search = search.lower()
    for chara in buffer['charas']:
        if any(search == name.lower() for name in [chara.name, chara.customName, chara.unitName]+chara.names):
            return [chara]
        if any(search in name.lower() for name in [chara.name, chara.customName, chara.unitName]):
            matches.append(chara)
        elif any(search in name.lower() for name in chara.names):
            matches.append(chara)
    return matches


def getCharaInfo(con, charaName):
    charaFromDb = databaseUtils.select(
        con, 'chara', where=f'name="{charaName}"')[0]
    charaObj = objectParser.dbCharaToObj(charaFromDb)
    embed = getEmbedFromChara(charaObj)
    return embed


def getCharaNameFromId(con, charaId):
    if not buffer.get('charas'):
        updateBuffer(con)
    for chara in buffer['charas']:
        if chara.name == charaId:
            return chara.names[0]


def getReplacementsText(con, replacements: dict):
    out = []
    for unitId, replacementIds in replacements.items():
        unitName = getCharaNameFromId(con, unitId)
        replacementNames = [getCharaNameFromId(
            con, name)for name in replacementIds]
        if len(replacementNames) > 0:
            replacementNames = ', '.join(replacementNames)
            out.append(f'{unitName} => {replacementNames}')
    return '\n'.join(out)


def getTeamEmbed(con, team: gcObjects.Team):
    embed = discord.Embed(title=team.name, color=discord.Color.green())
    embed.set_image(url=team.picUrl)
    if len(str(''.join(team.otherNames))) > 0:
        embed.add_field(name='AKA',
                        value=', '.join(team.otherNames), inline=False)
    mainCharaNames = [getCharaNameFromId(
        con, chara)for chara in team.unitNames]
    embed.add_field(name='Team Composition',
                    value=', '.join(mainCharaNames), inline=False)
    embed.add_field(name='Team Usage', value=', '.join(
        team.position), inline=False)
    embed.add_field(name='Description',
                    value=team.explanation if team.explanation else 'Not set', inline=False)
    replacementsText = getReplacementsText(con, team.replacements)
    if replacementsText:
        embed.add_field(name='Replacements',
                        value=replacementsText, inline=False)
    return embed


def concatCharaPics(charaObjs):
    urls = [chara.imageUrl for chara in charaObjs]
    files = [utils.downloadImgFromUrl(url) for url in urls]
    return utils.hconcat_resize_min(files)


def team_name_is_unique(con, teamName):
    if not buffer.get('teams'):
        updateBuffer(con)
    teamName = teamName.lower().strip()
    return not any([team.name.lower() == teamName
                    or any([extraName.lower() == teamName for extraName in team.otherNames])
                    for team in buffer['teams']])


async def get_team_name(ctx, bot, con, edit=False, origName=None):
    await utils.send_embed(ctx, utils.info_embed('Enter the team name'))
    acceptedName = False
    teamName = None
    while not acceptedName:

        msg = await utils.getMsgFromUser(ctx, bot)
        if msg and utils.cancelChecker(msg.content):
            await utils.send_cancel_msg(ctx)
            return
        if edit and msg.content == 'skip':
            return origName
        teamName = msg.content
        acceptedName = team_name_is_unique(con, teamName)
        if not acceptedName:
            await utils.send_msg(ctx, msg='The team name already exists')
    return teamName


async def get_team_units(ctx, bot, con, replacements=False, cantBe: str = None, edit=False, orgTeam=None):
    acceptedUnits = False
    acceptedCharas = []
    while not acceptedUnits:
        await utils.send_embed(ctx, utils.info_embed('Enter the unit names, separated by commas (,)'))
        msg = await utils.getMsgFromUser(ctx, bot)
        if not msg or (utils.cancelChecker(msg.content) or (replacements and utils.cancelChecker(msg.content, cancelstr='skip'))):
            if not replacements:
                await utils.send_cancel_msg(ctx)
            return
        if edit and msg.content == 'skip':
            return [characterSearch(con, orgName)[0] for orgName in orgTeam]
        charaNames = msg.content.split(',')
        charaNames = [chara.strip() for chara in charaNames]
        rejected = []
        needExpecicifation = False
        for charaName in charaNames:
            matches = characterSearch(con, charaName)
            if not matches or len(matches) < 1:
                rejected.append(charaName)
            elif len(matches) == 1:
                if replacements and cantBe and matches[0].name == cantBe:
                    await utils.send_embed(ctx, utils.errorEmbed('The chara can\'t substitute itself'))
                    rejected.append(charaName)
                elif not matches[0].name in [chara.name for chara in acceptedCharas]:
                    acceptedCharas.append(matches[0])
            else:
                needExpecicifation = True
                await utils.send_msg(ctx, msg=f'Multiple results were found for {charaName} Try again with one of the options bellow')
                await utils.send_embed(ctx, searchResultEmbed(matches, charaName))
        acceptedUnits = len(rejected) == 0 and not needExpecicifation
        if not acceptedUnits:
            await utils.send_msg(ctx, msg='Some of the characters failed to be accepted. You can try again')
            acceptedNames = ', '.join(
                [accepted.names[0] for accepted in acceptedCharas])
            if acceptedNames:
                await utils.send_embed(ctx, utils.successEmbed(acceptedNames))
            rejectedNames = ', '.join(rejected)
            if rejectedNames:
                await utils.send_embed(ctx, utils.errorEmbed(rejectedNames))
    return acceptedCharas


async def get_team_replacements(ctx, bot, con, mainCharas):
    await utils.send_embed(ctx, utils.info_embed('Time to enter the replacements for the characters in the team'))
    reaplacementsFinal = {}
    for chara in mainCharas:
        await utils.send_msg(ctx, msg=f'Replacements for **{chara.names[0]}** ("skip" to set no replacements)')
        reaplacements = await get_team_units(ctx, bot, con, replacements=True, cantBe=chara.name)
        if reaplacements:
            reaplacementsFinal[chara.name] = [
                replacement.name for replacement in reaplacements]
    return reaplacementsFinal


async def get_team_position(ctx, bot, edit=False, origPos=None):
    accepted = False
    options = ', '.join(gcObjects.Team.get_valid_team_postions())
    positions = []
    while not accepted:
        await utils.send_msg(ctx, msg=f'Enter the team poistions separated by a comma ({options})')
        msg = await utils.getMsgFromUser(ctx, bot)
        if not msg or utils.cancelChecker(msg.content):
            await utils.send_cancel_msg(ctx)
            return
        if edit and msg.content == 'skip':
            return origPos
        positions = [position.strip().capitalize()
                     for position in msg.content.split(',')]
        accepted = not any(
            [position not in gcObjects.Team.get_valid_team_postions() for position in positions])
        if not accepted:
            await utils.send_msg('One or more of the positions were not accepted, type them again')
    return positions


async def get_team_extra_names(ctx, bot, con):
    await utils.send_embed(ctx, utils.info_embed('Extra names for the team. "skip" to not set any'))
    acceptedName = False
    acceptedNames = []
    while not acceptedName:
        msg = await utils.getMsgFromUser(ctx, bot)
        if msg and utils.cancelChecker(msg.content):
            await utils.send_cancel_msg(ctx)
            return
        teamNames = msg.content.strip()
        if teamNames.lower() == 'skip':
            break
        rejectedNames = []
        teamNames = [teamName.strip() for teamName in teamNames.split(',')]
        for teamName in teamNames:
            if not team_name_is_unique(con, teamName):
                rejectedNames.append(teamName)
            else:
                if teamName not in acceptedNames:
                    acceptedNames.append(teamName)
                else:
                    rejectedNames.append(teamName)
        acceptedName = len(rejectedNames) < 1
        if not acceptedName:
            if len(acceptedNames) > 0:
                await utils.send_embed(ctx, utils.successEmbed(', '.join(acceptedNames)))
            await utils.send_embed(ctx, utils.errorEmbed(', '.join(rejectedNames)))
            await utils.send_msg(ctx, msg='Some of the names didn\'t go through. You can type "skip" to not add any more names')
    return acceptedNames if len(acceptedNames) > 0 else None


async def create_team(ctx, bot, con, picChannelId):
    await utils.send_embed(ctx, utils.info_embed('Creating the team, type "cancel" at any point to stop the procedure'))
    teamName = await get_team_name(ctx, bot, con)
    if not teamName:
        return
    newTeam = gcObjects.Team(name=teamName)
    extraNames = await get_team_extra_names(ctx, bot, con)
    if extraNames:
        newTeam.otherNames = extraNames
    teamMembers = await get_team_units(ctx, bot, con)
    if not teamMembers:
        return
    newTeam.unitNames = [member.name for member in teamMembers]
    newTeam.replacements = await get_team_replacements(ctx, bot, con, teamMembers)
    teamPos = await get_team_position(ctx, bot)
    if not teamPos:
        return
    newTeam.position = teamPos
    await utils.send_msg(ctx, msg='Enter the description/explanation for the team')
    desc = await utils.getMsgFromUser(ctx, bot, timeout=120)
    if not desc or utils.cancelChecker(desc.content):
        await utils.send_cancel_msg(ctx)
        return
    newTeam.explanation = desc.content
    teamPic = concatCharaPics(teamMembers)
    outputChannel = bot.get_channel(picChannelId)
    pic = await utils.send_img(ctx, teamPic, channel=outputChannel)
    newTeam.picUrl = pic.attachments[0].url
    return newTeam


async def edit_team(ctx, bot, con, picChannelId, team):
    await utils.send_embed(ctx, utils.info_embed('Editing the team, type "cancel" to stop or "skip" to not change that '))
    teamName = await get_team_name(ctx, bot, con, edit=True, origName=team.name)
    if not teamName:
        return
    team.name = teamName
    extraNames = await get_team_extra_names(ctx, bot, con)
    if extraNames:
        team.otherNames = extraNames
    teamMembers = await get_team_units(ctx, bot, con, edit=True, orgTeam=team.unitNames)
    if not teamMembers:
        return
    team.unitNames = [member.name for member in teamMembers]
    replacements = await get_team_replacements(ctx, bot, con, teamMembers)
    if replacements:
        team.replacements = replacements
    teamPos = await get_team_position(ctx, bot, edit=True, origPos=team.position)
    if not teamPos:
        return
    team.position = teamPos
    await utils.send_msg(ctx, msg='Enter the description/explanation for the team')
    desc = await utils.getMsgFromUser(ctx, bot, timeout=120)
    if not desc or utils.cancelChecker(desc.content):
        await utils.send_cancel_msg(ctx)
        return
    if desc.content != 'skip':
        team.explanation = desc.content
    teamPic = concatCharaPics(teamMembers)
    outputChannel = bot.get_channel(picChannelId)
    pic = await utils.send_img(ctx, teamPic, channel=outputChannel)
    team.picUrl = pic.attachments[0].url
    return team


def add_team_to_db(con, team):
    customInteractions.insert_team(con, team)
    updateBuffer(con)


def edit_team_in_db(con, team):
    customInteractions.delete_team(con, team.name)
    customInteractions.insert_team(con, team)
    updateBuffer(con)


def updateBuffer(con):
    allcharasDb = databaseUtils.select(con, 'chara')
    buffer['charas'] = [objectParser.dbCharaToObj(
        dbchara) for dbchara in allcharasDb]
    allTeamsDb = databaseUtils.select(con, 'team')
    buffer['teams'] = [objectParser.dbTeamToObj(team)for team in allTeamsDb]
