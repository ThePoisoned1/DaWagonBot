from types import new_class
import cv2
import discord
from utils import databaseUtils, utils, OptionSelector
from database import customInteractions
from usefullobjects import objectParser, gcObjects
from pprint import pprint
import random
import numpy as np
from PIL import Image
import asyncio
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
    title = await utils.send_embed(ctx, utils.info_embed('Enter the team name'))
    acceptedName = False
    teamName = None
    while not acceptedName:
        msg = await utils.getMsgFromUser(ctx, bot)
        if msg and utils.cancelChecker(msg.content):
            await utils.send_cancel_msg(ctx)
            return
        if edit and msg.content == 'skip':
            await title.delete()
            await msg.delete()
            return origName
        teamName = msg.content
        acceptedName = team_name_is_unique(con, teamName)
        if not acceptedName:
            await utils.send_msg(ctx, msg='The team name already exists', delete_after=5)
    await title.delete()
    await msg.delete()
    return teamName


async def get_team_units(ctx, bot, con, replacements=False, cantBe: str = None, edit=False, orgTeam=None):
    acceptedUnits = False
    acceptedCharas = []
    title = await utils.send_embed(ctx, utils.info_embed('.'))
    while not acceptedUnits:
        await title.edit(embed=utils.info_embed('Enter the unit names, separated by commas (,)'))
        msg = await utils.getMsgFromUser(ctx, bot)
        if not msg or utils.cancelChecker(msg.content) or (replacements and (utils.cancelChecker(msg.content, cancelstr='skip') or utils.cancelChecker(msg.content, cancelstr='skipall'))):
            if not replacements:
                await utils.send_cancel_msg(ctx)
            else:
                await msg.delete()
                await title.delete()
            return
        if edit and msg.content == 'skip':
            acceptedCharas = [characterSearch(
                con, orgName)[0] for orgName in orgTeam]
            await msg.delete()
            break
        charaNames = msg.content.split(',')
        await msg.delete()
        charaNames = [chara.strip() for chara in charaNames]
        rejected = []
        needExpecicifation = False
        for charaName in charaNames:
            matches = characterSearch(con, charaName)
            if not matches or len(matches) < 1:
                rejected.append(charaName)
            elif len(matches) == 1:
                if replacements and cantBe and matches[0].name == cantBe:
                    await utils.send_embed(ctx, utils.errorEmbed('The chara can\'t substitute itself'), delete_after=5)
                    rejected.append(charaName)
                elif not matches[0].name in [chara.name for chara in acceptedCharas]:
                    acceptedCharas.append(matches[0])
            else:
                needExpecicifation = True
                await utils.send_msg(ctx, msg=f'Multiple results were found for {charaName} Try again with one of the options bellow', delete_after=5)
                await utils.send_embed(ctx, searchResultEmbed(matches, charaName), delete_after=5)
        acceptedUnits = len(rejected) == 0 and not needExpecicifation
        if not acceptedUnits:
            await utils.send_msg(ctx, msg='Some of the characters failed to be accepted. You can try again', delete_after=5)
            acceptedNames = ', '.join(
                [accepted.names[0] for accepted in acceptedCharas])
            if acceptedNames:
                await utils.send_embed(ctx, utils.successEmbed(acceptedNames), delete_after=5)
            rejectedNames = ', '.join(rejected)
            if rejectedNames:
                await utils.send_embed(ctx, utils.errorEmbed(rejectedNames), delete_after=5)

    await title.delete()
    return acceptedCharas


async def get_team_replacements(ctx, bot, con, mainCharas):
    title = await utils.send_embed(ctx, utils.info_embed('Time to enter the replacements for the characters in the team'))
    reaplacementsFinal = {}
    replacement = await utils.send_embed(ctx, embed=utils.info_embed('.'))
    for chara in mainCharas:
        await replacement.edit(embed=utils.info_embed(f'Replacements for **{chara.names[0]}** ("skip" to set no replacements)'))
        replacements = await get_team_units(ctx, bot, con, replacements=True, cantBe=chara.name)
        if replacements:
            reaplacementsFinal[chara.name] = [
                replacement.name for replacement in replacements]
    await title.delete()
    await replacement.delete()
    return reaplacementsFinal


async def get_team_position(ctx, bot, edit=False, origPos=None):
    accepted = False
    options = ', '.join(gcObjects.Team.get_valid_team_postions())
    positions = []
    title = await utils.send_embed(ctx, embed=utils.info_embed('.'))
    while not accepted:
        await title.edit(embed=utils.info_embed(f'Enter the team poistions separated by a comma ({options})'))
        msg = await utils.getMsgFromUser(ctx, bot)
        if not msg or utils.cancelChecker(msg.content):
            await utils.send_cancel_msg(ctx)
            return
        if edit and msg.content == 'skip':
            await title.delete()
            await msg.delete()
            return origPos
        positions = [position.strip().capitalize()
                     for position in msg.content.split(',')]
        accepted = not any(
            [position not in gcObjects.Team.get_valid_team_postions() for position in positions])
        if not accepted:
            await utils.send_msg(ctx,msg='One or more of the positions were not accepted, type them again', delete_after=5)
    await title.delete()
    await msg.delete()
    return positions


async def get_team_extra_names(ctx, bot, con):
    title = await utils.send_embed(ctx, utils.info_embed('Extra names for the team. "skip" to not set any'))
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
                await utils.send_embed(ctx, utils.successEmbed(', '.join(acceptedNames)), delete_after=5)
            await utils.send_embed(ctx, utils.errorEmbed(', '.join(rejectedNames)), delete_after=5)
            await utils.send_msg(ctx, msg='Some of the names didn\'t go through. You can type "skip" to not add any more names')
    await title.delete()
    await msg.delete()
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
    title = await utils.send_msg(ctx, msg='Enter the description/explanation for the team')
    desc = await utils.getMsgFromUser(ctx, bot, timeout=120)
    if not desc or utils.cancelChecker(desc.content):
        await utils.send_cancel_msg(ctx)
        return
    newTeam.explanation = desc.content
    await title.delete()
    await desc.delete()
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
    title = await utils.send_msg(ctx, msg='Enter the description/explanation for the team')
    desc = await utils.getMsgFromUser(ctx, bot, timeout=120)
    if not desc or utils.cancelChecker(desc.content):
        await utils.send_cancel_msg(ctx)
        return
    if desc.content != 'skip':
        team.explanation = desc.content
    await title.delete()
    await desc.delete()
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
    descLines = get_default_gear_options()
    embed = discord.Embed(title='Default gear List',
                          description='\n'.join(descLines), color=discord.Color.orange())
    return embed


def get_default_gear_options():
    gears = []
    for name, gear in gcObjects.GearSet.get_default_gears().items():
        bonuses = '/'.join(gear.bonus)
        rolls = ', '.join(gear.rolls)
        gears.append(f'-{name}: set => {bonuses} ({rolls})')
    return gears


async def get_gear_set_set(ctx, bot, msg):
    sets = gcObjects.GearSet.get_bonus_weights()
    setsList = list(sets.keys())
    bonusSum = 0
    gearSets = []
    setBonusNum = 1
    while bonusSum < 6:
        chosen, msg = await OptionSelector.option_selector(bot, ctx, sets.keys(), title=f'Enter the {utils.ordinal(setBonusNum)} bonus of the set', msg=msg)
        if chosen == None:
            await utils.send_cancel_msg(ctx)
            return
        bonus = setsList[chosen]
        if bonusSum + sets.get(bonus) <= 6 and bonus not in gearSets:
            gearSets.append(bonus)
            bonusSum += sets.get(bonus)
            setBonusNum += 1
        else:
            await utils.send_embed(ctx, embed=utils.errorEmbed(f'{bonus} in not a valid addition to {", ".join(gearSets)}'), delete_after=5)
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


async def get_gear_rolls(ctx, bot, pieces, msg):
    availableRolls = gcObjects.GearSet.get_rolls().get(pieces)
    rollNum = 0
    selectedRolls = {}

    while rollNum < 10:
        selected = f'({", ".join(selectedRolls.keys())})' if len(
            selectedRolls) > 0 else '\b'
        chosen, msg = await OptionSelector.option_selector(bot, ctx, availableRolls, title=f'Rolls for the {pieces} pieces. '+selected, msg=msg)
        if chosen == None:
            await utils.send_cancel_msg(ctx)
            return
        roll = availableRolls[chosen]
        if roll in selectedRolls.keys():
            await utils.send_embed(ctx, embed=utils.errorEmbed('You already added that roll'), delete_after=5)
            continue
        rolls, msg = await OptionSelector.option_selector(bot, ctx, range(1, 11), title=f'Number of rolls?', msg=msg)
        if rolls == None:
            await utils.send_cancel_msg(ctx)
            return
        rolls += 1
        if rolls + rollNum <= 10:
            rollNum += rolls
            selectedRolls[roll] = rolls
        else:
            await utils.send_embed(ctx, embed=utils.errorEmbed('That surpases the maximum number of rolls for the pieces'), delete_after=5)
    return selectedRolls


def parse_piece_rolls(rolls):
    if len(rolls) == 1:
        return rolls.keys()
    else:
        return [f'{roll}({num})'for roll, num in rolls.items()]


async def create_custom_gear(ctx, bot, msg):
    gear = gcObjects.GearSet()
    gearSets = await get_gear_set_set(ctx, bot, msg)
    if not gearSets:
        return
    gear.bonus = gearSets
    gearRolls = []
    for piece in ['Top', 'Mid', 'Bottom']:
        pieceRoll = await get_gear_rolls(ctx, bot, piece, msg)
        if not pieceRoll:
            return
        pieceRoll = parse_piece_rolls(pieceRoll)
        gearRolls.append(', '.join(pieceRoll))
    gear.rolls = gearRolls
    return gear


async def create_gear(ctx, bot, chara):
    await utils.send_embed(ctx, utils.info_embed(f'Creating gear for *{chara.names[0]}*'))
    options = get_default_gear_options()
    options.append('Custom')
    chosen, msg = await OptionSelector.option_selector(bot, ctx, options)
    if chosen == None:
        await utils.send_cancel_msg(ctx)
        return
    if chosen != len(options)-1:
        gear = list(gcObjects.GearSet.get_default_gears().values())[chosen]
    else:
        gear = await create_custom_gear(ctx, bot, msg)
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
            newName = None
            if extraName[0] != elementLetter:
                newName = f'{elementLetter}{extraName[0].upper()}{extraName[1:]}'
                needsFix = True
            if ' ' in extraName:
                if not newName:
                    newName = extraName
                newName = newName.replace(' ', '')
                needsFix = True
            if needsFix:
                newNames.append(newName)
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


def get_random_team(con, rerollable=False):
    randomized = get_shuffled_charas(con)
    selected = []
    while len(selected) < 4:
        chara = randomized.pop(0)
        if gcObjects.Character.chara_can_go_in_team(selected, chara):
            selected.append(chara)
    return selected if not rerollable else selected, randomized


def reroll_chara(charas, queue, toReroll):
    charas.pop(toReroll)
    while len(queue) > 0:
        chara = queue.pop(0)
        if gcObjects.Character.chara_can_go_in_team(charas, chara):
            charas.insert(toReroll, chara)
            break
    return charas, queue


async def charaReroller(bot, ctx, msg, embed, charas, queue, rerolls, picChannel):
    emojiOptions = OptionSelector.emojiOptions
    for x in range(len(charas)):
        await msg.add_reaction(emojiOptions[x])
    await msg.add_reaction(OptionSelector.emojiCancel)
    ogRerolls = rerolls
    history = ''
    while rerolls > 0:

        try:
            reaction, user = await bot.wait_for(
                "reaction_add",
                timeout=25,
                check=lambda reaction, user: str(
                    reaction.emoji) in emojiOptions[:len(charas)]
                and user.id != bot.user.id
                and reaction.message.id == msg.id
                and user.id == ctx.author.id
            )
        except asyncio.TimeoutError:
            await msg.clear_reactions()
            break
        else:
            emojistr = str(reaction.emoji)
            await reaction.remove(user)
            if emojistr == OptionSelector.emojiCancel:
                await msg.clear_reactions()
                break
            chosen = OptionSelector.getEmojiValue(str(reaction.emoji))
            history += f'\n {charas[chosen].names[0]} => '
            charas, queue = reroll_chara(charas, queue, chosen)
            history += charas[chosen].names[0]
            newPic = concatCharaPics(charas)
            picMsg = await utils.send_img(ctx, newPic, channel=picChannel)
            embed.set_image(url=picMsg.attachments[0].url)
            rerolls -= 1
            embed.description = f'({rerolls}/{ogRerolls} rerolls left)'+history
            await msg.edit(embed=embed)
    else:
        await msg.clear_reactions()


async def get_gear_to_delete(ctx, bot, chara):
    gears = chara.gear
    if len(gears) < 1:
        await utils.send_embed(ctx, utils.errorEmbed('That chara has no gears man'))
        return

    options = [gear.get_gear_short_data() for gear in gears]
    options.append('All')
    selectedOption, msg = await OptionSelector.option_selector(bot, ctx, options)
    if selectedOption == None:
        await utils.send_cancel_msg(ctx)
        return
    if selectedOption >= len(gears):
        return gears
    else:
        return gears[selectedOption]


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


def del_chara_gear(con, chara, delGear):
    newGears = []
    for gear in chara.gear:
        if gear != delGear:
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
