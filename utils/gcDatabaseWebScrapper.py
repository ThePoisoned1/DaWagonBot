import requests
from bs4 import BeautifulSoup
from usefullobjects.gcObjects import *
from pprint import pprint
import re
from utils import utils


rarities = {
    'rarity_ssr': 'SSR',
    'rarity_sr': 'SR',
    'rarity_r': 'R'
}
attributes = {
    'attribute_vitality': 'Vitality',
    'attribute_strength': 'Strength',
    'attribute_speed': 'Speed'
}
races = {
    'race_human': 'Human',
    'race_demon': 'Demon',
    'race_giant': 'Giant',
    'race_fairy': 'Fairy',
    'race_goddess': 'Goddess',
    'race_unknown': 'Unknown',
}
attributeColors = {
    'Vitality': 'Green',
    'Strength': 'Red',
    'Speed': 'Blue'
}


def getHTMLFromUrl(url):
    page = requests.get(url)
    page = BeautifulSoup(page.content, "html.parser")
    return page


def getInfoFromHtmlLine(line, matches: dict):
    out = []
    for key, val in matches.items():
        if re.search(key, str(line)):
            out.append(val)
    return out


def getSkillMultiplier(line):
    rejex = '\d+%'
    result = re.search(rejex, line)
    return result.string


def getSkillEffects(line):
    regex = '<b style="color:#00d4fe">[A-Za-z ()-]+</b>'
    extraRejexes = {
        'Skill Ranks': 'Skill Rank',
        'of diminished HP': 'Restores dimished HP',
        'Max HP by': 'HP',
        '[d|D]epletes Ultimate Move Gauge': 'Depletes orbs (end of turn)',
        '>Evasion<': 'Evasion',
        '[h|H]eals HP': 'Heal',
        'Ultimate Move damage': 'Ultimate Move damage',
        'Recovers HP': 'Recovers HP'
    }
    out = []
    effects = re.findall(regex, line)
    if effects:
        for effect in effects:
            toAdd = effect[25].upper()+effect[26:-4]
            if toAdd == 'Depletes':
                toAdd = 'Depletes orbs'
            elif toAdd == 'Fills':
                toAdd = 'Fills orbs'
            elif toAdd == '(Excludes Rupture)':
                toAdd = 'Shield'
            out.append(toAdd)
    for extraRegex, val in extraRejexes.items():
        if re.findall(extraRegex, line):
            out.append(val)
    return out


def incOrDec(line):
    increaseRejex = '[I|i]ncrease'
    decreaseRejex = '[D|d]ecrease'
    out = []
    if re.findall(increaseRejex, line):
        out.append('Increases')
    if re.findall(decreaseRejex, line):
        out.append('Decreases')
    return out


def isAoE(line):
    # (on|of)( all)?
    aoeRegexAllies = 'allies'
    aoeRegexEnemies = 'enemies'
    if len(re.findall(aoeRegexAllies, line)) > 0 or len(re.findall(aoeRegexEnemies, line)) > 0:
        return True
    return False


def checkForSrSsr(allcharas):
    out = []
    moreThan3Charas = [chara.name[:-1]
                       for chara in allcharas if int(chara.name[-1]) > 3]
    for chara in allcharas:
        name = chara.name[:-1]
        outChara = chara
        if chara.name == 'gowther3':
            outChara.rarity = 'SR'
        if name in moreThan3Charas:
            atributes = [
                chara.attribute for chara in allcharas if chara.name[:-1] == name]
            if atributes.count(outChara.attribute) > 1 and outChara.rarity != 'SSR':
                print(outChara.rarity, outChara.names[0])
                outChara.names[0] = outChara.names[0][0] + \
                    outChara.rarity+outChara.names[0][1:]

        out.append(outChara)
    return out


def getCharaDataFromUrl(url):
    baseUrl = '/'.join(url.split('/')[:3])
    page = getHTMLFromUrl(url)
    chara = Character()
    # name
    chara.name = ''.join(url.split('/')[-2:])
    result = page.find_all("div", class_="pt-3")
    name = result[0]
    chara.customName = name.find('h5', class_='whitetext').text
    chara.unitName = name.find('h4', class_='whitetext').text
    pos = 0
    # rarity, attribute, race
    result = page.find_all(
        'table', class_='table table-dark table-striped table-bordered')
    data = result[pos].find_all('td')
    chara.rarity = getInfoFromHtmlLine(data[1].img, rarities)[0]
    chara.attribute = getInfoFromHtmlLine(data[3].img, attributes)[0]
    chara.race = getInfoFromHtmlLine(data[5].img, races)
    chara.imageUrl = baseUrl + '/' + \
        page.find_all('img')[0].get('src').replace('../', '')
    # first name
    color = attributeColors[chara.attribute]
    fName = utils.camel_case(f'{color[0].lower()} {chara.name[:-1]}')
    chara.names.append(fName)
    # skill effects
    print(url)
    pos += 1
    if any(header.text == 'Associated with' for header in page.find_all("h2", class_="whitetext")):
        pos += 1
    for skill in result[pos:pos+2]:
        skillData = skill.find_all('td')
        charaSkill = Skill()
        charaSkill.effects = getSkillEffects(str(skillData[7]))
        charaSkill.isAoE = isAoE(skillData[7].text)
        charaSkill.skillType = skillData[8].text
        charaSkill.increasesDecresases = incOrDec(skillData[7].text)
        chara.skills.append(charaSkill)
    pos += 2
    # ultimate
    ultData = result[pos].find_all('td')
    charaSkill = Skill()
    charaSkill.effects = getSkillEffects(
        str(ultData[1]))+getSkillEffects(str(ultData[2]))
    charaSkill.isAoE = isAoE(ultData[1].text)
    charaSkill.skillType = 'Ultimate'
    charaSkill.increasesDecresases = incOrDec(ultData[1].text)
    chara.skills.append(charaSkill)
    pos += 1
    # pasive
    pasiveData = result[pos].find_all('td')
    chara.passive = pasiveData[0].text
    pos += 1
    # holy relic
    if any(header.text == 'Holy Relic' for header in page.find_all("h2", class_="whitetext")):
        weirdosRejexes = ['^merlin\d$', '^slater\d$', '^roxy\d$']
        if any([re.match(weidoRejex, chara.name) for weidoRejex in weirdosRejexes]):
            aux = pos+1
            chara.relic = result[aux].find_all('td')[1].text
        else:
            chara.relic = result[pos].find_all('td')[1].text
    # commandment
    if any(header.text == 'Commandment' for header in page.find_all("h2", class_="whitetext")):
        chara.commandment = result[pos].find_all('td')[0].text
    if any(header.text == 'Grace' for header in page.find_all("h2", class_="whitetext")):
        chara.grace = result[pos].find_all('td')[0].text
    chara.charaUrl = url
    return chara


def getCharaUrls(mainUrl):
    data = getHTMLFromUrl(mainUrl)
    result = data.find_all('td')
    urls = []
    regex = 'characters/[a-z_]+/\d'
    for res in result:
        aux = str(res)
        url = re.search(regex, aux)
        if url:
            points = url.span()
            out = aux[points[0]:points[1]]
            urls.append(out)
    return urls