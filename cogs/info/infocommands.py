from dataclasses import replace
from re import match
import discord
from discord import embeds
from utils import databaseUtils, utils
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
        pprint(replacementIds)
        pprint(replacementNames)
        if len(replacementNames) > 0:
            replacementNames = ', '.join(replacementNames)
            out.append(f'{unitName} => {replacementNames}')
    return '\n'.join(out)


def getTeamEmbed(con, team: gcObjects.Team):
    embed = discord.Embed(title=team.name, color=discord.Color.green())

    embed.set_image(url=team.picUrl)
    print(team.picUrl)
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

    


def updateBuffer(con):
    allcharasDb = databaseUtils.select(con, 'chara')
    buffer['charas'] = [objectParser.dbCharaToObj(
        dbchara) for dbchara in allcharasDb]
    allTeamsDb = databaseUtils.select(con, 'team')
    buffer['teams'] = [objectParser.dbTeamToObj(team)for team in allTeamsDb]
