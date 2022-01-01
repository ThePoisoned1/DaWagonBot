from bs4 import element
import cv2
import discord
from discord.member import M
from utils import databaseUtils, utils
from database import customInteractions
from usefullobjects import objectParser, gcObjects
from pprint import pprint
import random
import numpy as np
from PIL import Image
buffer = {}


def getTeamApereance(con, unitId, gw=False):
    if not buffer.get('teams'):
        updateBuffer(con)
    apereances = []
    for team in buffer['teams']:
        if unitId in team.unitNames:
            apereances.append(team.name)
        else:
            for val in team.replacements.values():
                for charaId in val:
                    if charaId == unitId:
                        if gw and any([position in gcObjects.Team.get_guild_wars_positions() for position in team.position]):
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
    equipData = '\n-------------\n'.join([gear.getGearData()
                                         for gear in chara.gear])
    embed.add_field(name='Skills', value=chara.getSkillData())
    embed.add_field(name='Gear', value=equipData if len(
        equipData) > 0 else 'No sets registered')
    teamApereances = '\n'.join(
        f'-{teamName}' for teamName in getTeamApereance(con, chara.name, gw=True))
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
        elif any(search in name.lower() for name in team.otherNames) or search in team.name.lower():
            matches.append(team)
    return matches


def characterSearch(con, search: str):
    if not buffer.get('charas'):
        updateBuffer(con)
    matches = []
    search = search.lower()
    for chara in buffer['charas']:
        if any(search == name.lower() for name in [chara.name]+chara.names):
            return [chara]
        if any(search in name.lower() for name in [chara.customName, chara.unitName]):
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
    files = [cv2.resize(utils.binary_str_to_nparray(chara.binImg), [
        100, 100])for chara in charaObjs]
    return utils.hconcat_resize_min(files)


def team_name_is_unique(con, teamName):
    if not buffer.get('teams'):
        updateBuffer(con)
    teamName = teamName.lower().strip()
    return not any([team.name.lower() == teamName
                    or any([extraName.lower() == teamName for extraName in team.otherNames])
                    for team in buffer['teams']])


def chara_name_is_unique(con, charaName):
    if not buffer.get('charas'):
        updateBuffer(con)
    charaName = charaName.strip().lower()
    return not any([chara.name.lower() == charaName
                    or any([extraName.lower() == charaName for extraName in chara.names])
                    or chara.customName.lower() == charaName
                    or chara.unitName.lower() == charaName
                    for chara in buffer['charas']])


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


async def condition_accepted(ctx, bot, msg, options=['Yes', 'No']):
    aux = '/'.join(options)
    await utils.send_embed(ctx, utils.info_embed(f'{msg} ({aux})'))
    answer = await utils.getMsgFromUser(ctx, bot)
    if not answer or utils.cancelChecker(answer.content.strip()):
        await utils.send_cancel_msg(ctx)
        return
    return answer.content.capitalize().strip() == options[0]


async def get_new_chara_name(ctx, bot, con, chara):
    await utils.send_embed(ctx, utils.info_embed(f'Trying to add a new name to {chara.name}. Adding the element before it is recommended (gFestGowther can be found searching festgowther)'))
    nameIsAccepted = False
    name = None
    while not nameIsAccepted:
        await utils.send_msg(ctx, 'Enter the new name')
        name = await utils.getMsgFromUser(ctx, bot)
        if not name or utils.cancelChecker(name.content.strip()):
            await utils.send_cancel_msg(ctx)
            return
        name = name.content.strip()
        nameIsAccepted = chara_name_is_unique(con, name)
        if not nameIsAccepted:
            await utils.send_embed(ctx, utils.errorEmbed('The name already exists. You can cancel the procedure with "cancel"'))
    return name


def get_default_gear_embed():
    descLines = []
    for name, gear in gcObjects.GearSet.get_default_gears().items():
        bonuses = '/'.join(gear.bonus)
        rolls = ', '.join(gear.rolls)
        descLines.append(f'-{name}: set => {bonuses} ({rolls})')
    embed = discord.Embed(title='Default gear List',
                          description='\n'.join(descLines), color=discord.Color.orange())
    return embed


async def get_gear_set_set(ctx, bot):
    accpetedSets = False
    sets = gcObjects.GearSet.get_bonus_weights()
    setNames = ', '.join(sets.keys())
    gearSets = None
    while not accpetedSets:
        await utils.send_msg(ctx, msg=f'Enter the desired sets for the gear, separated by comma.\n{setNames}')
        gearSets = await utils.getMsgFromUser(ctx, bot)
        if not gearSets or utils.cancelChecker(gearSets.content):
            await utils.send_cancel_msg(ctx)
            return
        gearSets = [gear.strip().title()
                    for gear in gearSets.content.split(',')]
        if len(gearSets) < 2:
            await utils.send_embed(ctx, utils.errorEmbed('Gear need to have at least 2 sets'))
            continue
        if any(gearSet not in sets.keys() for gearSet in gearSets):
            await utils.send_embed(ctx, utils.errorEmbed('One of the sets was not recognized. Try again'))
            continue
        bonusSum = sum([sets.get(gear) for gear in gearSets])
        if bonusSum != 6:
            await utils.send_embed(ctx, utils.errorEmbed(f'The pieces you need to make that set are {bonusSum}, please specify a 6 pieces set'))
        else:
            accpetedSets = True
    return gearSets


async def get_accepted_roll_number(ctx, bot, roll):
    acceptedRoll = False
    numRolls = None
    while not acceptedRoll:
        await utils.send_msg(ctx, msg=f'Enter the number of rolls for {roll}.')
        numRolls = await utils.getMsgFromUser(ctx, bot)
        if not numRolls or utils.cancelChecker(numRolls.content):
            await utils.send_cancel_msg(ctx)
            return
        numRolls = numRolls.content
        if not numRolls.isdigit():
            await utils.send_msg(ctx, msg='Please input a number')
            continue
        numRolls = int(numRolls)
        if numRolls >= 10 or numRolls < 1:
            await utils.send_msg(ctx, msg='You are not supposed to inpout a number like that')
        else:
            acceptedRoll = True
    return numRolls


async def get_number_of_rolls(ctx, bot, rolls):
    rollDict = {}
    for roll in rolls:
        rollNumber = await get_accepted_roll_number(ctx, bot, roll)
        if not rollNumber:
            return
        rollDict[roll] = rollNumber
    return rollDict


async def get_gear_rolls(ctx, bot, pieces):
    acceptedRolls = False
    gearRolls = None
    availableRolls = gcObjects.GearSet.get_rolls().get(pieces)
    rollNames = ', '.join(availableRolls)
    while not acceptedRolls:
        await utils.send_msg(ctx, msg=f'Enter the rolls for the {pieces} pieces, separated by comma.\n{rollNames}')
        gearRolls = await utils.getMsgFromUser(ctx, bot)
        if not gearRolls or utils.cancelChecker(gearRolls.content):
            await utils.send_cancel_msg(ctx)
            return
        gearRolls = [gear.strip().title()
                     for gear in gearRolls.content.split(',')]
        if any(gearRoll not in availableRolls for gearRoll in gearRolls):
            await utils.send_embed(ctx, utils.errorEmbed('One of the rolls was not recognized. Try again'))
            continue
        if len(gearRolls) != 1:
            rolls = await get_number_of_rolls(ctx, bot, gearRolls)
            if not rolls:
                return
            if not sum([roll for roll in rolls.values()]) == 10:
                await utils.send_msg(ctx, msg='The total rolls for the substats must be 10, try again')
                continue
            gearRolls = [f'{roll}({num})' for roll, num in rolls.items()]
        acceptedRolls = True
    return gearRolls


async def create_custom_gear(ctx, bot):
    await utils.send_embed(ctx, utils.info_embed('You are now creatating a custom gear'))
    gear = gcObjects.GearSet()
    gearSets = await get_gear_set_set(ctx, bot)
    if not gearSets:
        return
    gear.bonus = gearSets
    gearRolls = []
    for piece in ['Top', 'Mid', 'Bottom']:
        pieceRoll = await get_gear_rolls(ctx, bot, piece)
        if not pieceRoll:
            return
        gearRolls.append(', '.join(pieceRoll))
    gear.rolls = gearRolls
    return gear


async def create_gear(ctx, bot, chara):
    await utils.send_embed(ctx, utils.info_embed(f'Creating gear for *{chara.names[0]}*'))
    await utils.send_msg(ctx, msg='If you want one of the default gears, type it \'s name. Type "custom" to make a custom one')
    await utils.send_embed(ctx, get_default_gear_embed())
    acceptedAnswer = False
    gear = None
    while not acceptedAnswer:
        msg = await utils.getMsgFromUser(ctx, bot)
        if not msg or utils.cancelChecker(msg.content):
            await utils.send_cancel_msg(ctx)
            return
        answer = msg.content.upper()
        if answer not in gcObjects.GearSet.get_default_gears().keys() and answer != 'CUSTOM':
            await utils.send_embed(ctx, utils.errorEmbed('I did not like that answer, try again'))
            continue
        if answer != 'CUSTOM':
            gear = gcObjects.GearSet.get_default_gear(answer)
        else:
            gear = await create_custom_gear(ctx, bot)
        acceptedAnswer = True
    return gear


def get_fixed_names(con):
    if not buffer.get('teams'):
        updateBuffer(con)
    toFix = []
    for chara in buffer['charas']:
        elementLetter = chara.names[0][0]
        needsFix = False
        auxChara = chara
        newNames = []
        for extraName in chara.names:
            if extraName[0] != elementLetter:
                newName = f'{elementLetter}{extraName[0].upper()}{extraName[1:]}'
                newNames.append(newName)
                needsFix = True
            else:
                newNames.append(extraName)
        if needsFix:
            auxChara.names = newNames
            toFix.append(auxChara)
    return toFix


def fix_chara_names(con):
    toFix = get_fixed_names(con)
    for chara in toFix:
        update_chara_names(con, chara.name, chara.names)
    return True


def get_default_gear_from_name(name):
    return gcObjects.GearSet.get_default_gear(name)


def get_shuffled_charas(con):
    if not buffer.get('charas'):
        updateBuffer(con)
    toShuffle = buffer['charas'].copy()
    random.shuffle(toShuffle)
    return toShuffle


def get_random_charas(con, ammount: int):
    randomized = get_shuffled_charas(con)
    selected = []
    for x in range(ammount):
        selected.append(randomized.pop(0))
    return selected


def get_img_for_charas(charas):
    rows = list(utils.chunks(charas, 4))
    rows = [concatCharaPics(row) for row in rows]
    if len(charas) % 4 == 0 and len(charas) > 4:
        return utils.vconcat_resize_min(rows)
    else:
        if len(charas) <= 4:
            return rows[0]
        else:
            img = utils.vconcat_resize_min(rows[:-1])
            lastRowImg = rows[-1]
            fillerImg = Image.open(
                '.\\imgs\\charaFillerImg.png').convert('RGB')
            fillerImg = np.asarray(fillerImg)
            for x in range(4-len(charas) % 4):
                lastRowImg = utils.hconcat_resize_min([lastRowImg, fillerImg])
            img = utils.vconcat_resize_min([img, lastRowImg])
            return img


def get_random_team(con):
    randomized = get_shuffled_charas(con)
    selected = []
    while len(selected) < 4:
        chara = randomized.pop(0)
        if gcObjects.Character.chara_can_go_in_team(selected, chara):
            selected.append(chara)
    return selected


def get_chara_from_id(con, charaId):
    if not buffer.get('charas'):
        updateBuffer(con)
    for chara in buffer['charas']:
        if chara.name == charaId:
            return chara


def update_chara_names(con, charaId, newCharaNames):
    customInteractions.update_names_on_chara(con, charaId, newCharaNames)
    updateBuffer(con)


def add_chara_gear(con, chara, gear):
    newGears = chara.gear
    newGears.append(gear)
    customInteractions.update_gears_on_chara(con, chara.name, newGears)
    updateBuffer(con)


def add_chara_name(con, chara, newName):
    newNames = chara.names
    newNames.append(newName)
    update_chara_names(con, chara.name, newNames)


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
