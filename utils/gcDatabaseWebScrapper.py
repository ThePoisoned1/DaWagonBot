import requests
from bs4 import BeautifulSoup
from usefullobjects.gcObjects import *
from usefullobjects import charaNames
from pprint import pprint
import re
from utils import utils
import cv2


rarities = {
    'rarity_ssr': 'SSR',
    'rarity_sr': 'SR',
    'rarity_r': 'R'
}
attributes = {
    'attribute_vitality': 'Vitality',
    'attribute_strength': 'Strength',
    'attribute_speed': 'Speed',
    'attribute_dark': 'Dark',
    'attribute_light': 'Light'
}
races = {
    'race_human': 'Human',
    'race_demon': 'Demon',
    'race_giant': 'Giant',
    'race_fairy': 'Fairy',
    'race_goddess': 'Goddess',
    'race_unknown': 'Unknown',
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


def getSkillEffects(line, rawLine):
    regex = '<b style="color:#00d4fe">[A-Za-z ()-]+</b>'
    extraRejexes = {
        r'of diminished HP': 'Restores dimished HP',
        r'depletes Ultimate Move Gauge': 'Depletes orbs (end of turn)',
        r'depletes the Ultimate Move Gauge': 'Depletes orbs',
        r'>Evasion<': 'Evasion',
        r'heals( diminished)? HP': 'Heal',
        r'Recovers HP': 'Recovers HP',
        r'disables everything including Ultimate Moves except for Debuff Skills': 'Disables everything but Debuff Skills',
        r'disables Rank 2 and above': 'Disables Rank 2+',
        r'Removes Debuffs': 'Removes Debuffs',
        r'counter': 'Counter',
        r'Attack when taking attacks': 'Counter',
        r'Allows the use of only Rank 1 Skills': 'Only Rank 1 Skills',
        r'reduces the final damage taken':'Reduces allies damage taken',
        r'restores the HP of all allies by':'Restores HP'
    }
    incDecRejexes = {
        r'Skill Ranks': 'Skill Rank',
        r'Max HP by': 'HP',
        r'Max HP of the hero by':'own HP',
        r'Ultimate Move damage': 'Ultimate Move damage',
        r'all stats': 'All stats',
        r'Crit Resistance': 'Crit Resistance',
        r'Crit Defense': 'Crit Defense',
        r'damage dealt':'Damage dealt',
        r'damage taken':'Damage taken',
        r'Attack of':'Attack',

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
            elif toAdd in ['Decreases skill ranks','(Excludes Stances and Recovery Skills)','(Excludes Stance and Recovery Skills)','(Excluding Stance and Recovery Skills)']:
                continue
            elif toAdd == ['Blocks all skill effects including those of Ultimate Moves','Blocks all enemies\' skill effects including those of Ultimate Moves']:
                toAdd == 'Disable'
            if effect not in toAdd:
                out.append(toAdd)
    for extraRegex, val in extraRejexes.items():
        if len(re.findall(extraRegex, rawLine,flags=re.IGNORECASE)) > 0:
            if not (extraRegex == 'Removes Debuffs' and 'Removes Debuffs' in out):
                out.append(val)
    out=list(set(out))
    for incDecRejexe, val in incDecRejexes.items():
        if val not in out and len(re.findall(incDecRejexe, rawLine,flags=re.IGNORECASE)) > 0:
            out.insert(0, val)
    return out


def incOrDec(line):
    increaseRejex = '[I|i]ncreas'
    decreaseRejex = '[D|d]ecreas'
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
    if (len(re.findall(aoeRegexAllies, line)) > 0 or len(re.findall(aoeRegexEnemies, line)) > 0) and 'taunt' not in line.lower():
        return True
    return False


def checkForSrSsr(allcharas):
    out = []
    moreThan3Charas = [chara.name[:-1]
                       for chara in allcharas if int(chara.name[-1]) > 3]
    print(moreThan3Charas)
    for chara in allcharas:
        name = chara.name[:-1]
        outChara = chara
        if name in moreThan3Charas:
            atributes = [
                chara.attribute for chara in allcharas if chara.name[:-1] == name]
            print(atributes)
            if atributes.count(outChara.attribute) > 1 and outChara.rarity != 'SSR':
                outChara.names[0] = outChara.names[0][0] + \
                    outChara.rarity+outChara.names[0][1:]

        out.append(outChara)
    print(len(out))
    return out


def get_skills_ult(result, pos):
    skills = []
    for skill in result[pos:pos+2]:
        skillData = skill.find_all('td')
        charaSkill = Skill()
        charaSkill.effects = getSkillEffects(
            str(skillData[7]), skillData[7].text)
        charaSkill.isAoE = isAoE(skillData[7].text)
        charaSkill.skillType = skillData[8].text
        charaSkill.increasesDecresases = incOrDec(skillData[7].text)
        skills.append(charaSkill)
    pos += 2
    # ultimate
    ultData = result[pos].find_all('td')
    charaSkill = Skill()
    charaSkill.effects = getSkillEffects(str(ultData[1]), ultData[1].text)
    if len(ultData) > 2:
        charaSkill.effects += getSkillEffects(str(ultData[2]), ultData[2].text)
    charaSkill.isAoE = isAoE(ultData[1].text)
    charaSkill.skillType = 'Ultimate'
    charaSkill.increasesDecresases = incOrDec(ultData[1].text)
    skills.append(charaSkill)
    return skills, pos


def get_chara_real_name(charaId):
    charaId = charaId.lower()
    for name, rejexes in charaNames.unitNames.items():
        if any(len(re.findall(rejex.lower(), charaId)) > 0 for rejex in rejexes):
            return name
    print('PEPEGA', charaId)

def fixes_cuz_db_kekega(chara:Character):
    if chara.name == 'howzer4':
        chara.attribute = 'Speed'
        chara.names[0]='bHowzer'
    elif chara.name == 'blessing_of_earth_diane1':
        chara.imageUrl='https://gcdatabase.com/images/characters/blessing_of_earth_diane/ssrg_portrait.png'
    elif chara.name == 'jormungandr1' or chara.name == 'awakened_lillia1':
        chara.skills[0].isAoE=False
    return chara

def get_atributes_order(data):
    attrs = [x.text for x in data.find_all("h2", class_="whitetext")]
    out = []
    for att in attrs:
        if any(att == aux for aux in ['Commandment','Grace','Holy Relic']) and att not in out:
            out.append(att)
    return out

def getCharaDataFromUrl(url):
    baseUrl = '/'.join(url.split('/')[:3])
    page = getHTMLFromUrl(url)
    print(url)
    chara = Character()
    # name
    chara.name = ''.join(url.split('/')[-2:])
    chara.realName = get_chara_real_name(chara.name)
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
    color = charaNames.attributeColors[chara.attribute]
    fName = utils.camel_case(f'{color[0].lower()} {chara.name[:-1]}')
    chara.names.append(fName)
    # skill effects
    pos += 1
    if any(header.text == 'Associated with' for header in page.find_all("h2", class_="whitetext")):
        pos += 1
    chara.skills, pos = get_skills_ult(result, pos)
    # Transforming unit
    pos += 1
    transforming = False
    if 'Transforms' in chara.skills[-1].effects:
        transforming = True
        moreSkills, pos = get_skills_ult(result, pos)
        chara.skills += moreSkills
        pos += 1
    # pasive
    pasiveData = result[pos].find_all('td')
    chara.passive = pasiveData[0].text
    pos += 1
    if transforming:
        pasiveData = result[pos].find_all('td')
        chara.passive += '\n------------------\n'
        chara.passive += pasiveData[0].text
        pos += 1
    atts = get_atributes_order(page)
    for att in atts:
        # commandment
        if att == 'Commandment':
            chara.commandment = result[pos].find_all('td')[0].text
            pos+=1
        # grace
        elif att == 'Grace':
            chara.grace = result[pos].find_all('td')[0].text
            pos+=1
        # holy relic
        elif att =='Holy Relic':
            chara.relic = result[pos].find_all('td')[1].text
            pos+=1
    chara.charaUrl = url
    chara = fixes_cuz_db_kekega(chara)
    chara.binImg = utils.downloadImgFromUrl(chara.imageUrl)    
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
