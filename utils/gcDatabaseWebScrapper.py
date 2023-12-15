import requests
from bs4 import BeautifulSoup
from usefullobjects.gcObjects import *
from usefullobjects import charaNames
from pprint import pprint
import re
from utils import utils
import cv2


rarities = {
    'rarity_lr':'LR',
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
        r'basic stats': 'Basic Stats',
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


def get_skills_ult(tables):
    skills = []
    for skill in tables[:2]:
        skillData = skill.find_all('td')
        charaSkill = Skill()
        charaSkill.effects = getSkillEffects(
            str(skillData[7]), skillData[7].text)
        charaSkill.isAoE = isAoE(skillData[7].text)
        charaSkill.skillType = skillData[8].text
        charaSkill.increasesDecresases = incOrDec(skillData[7].text)
        skills.append(charaSkill)

    # ultimate
    ultData = tables[2].find_all('td')
    charaSkill = Skill()
    charaSkill.effects = getSkillEffects(str(ultData[1]), ultData[1].text)
    if len(ultData) > 2:
        charaSkill.effects += getSkillEffects(str(ultData[2]), ultData[2].text)
    charaSkill.isAoE = isAoE(ultData[1].text)
    charaSkill.skillType = 'Ultimate'
    charaSkill.increasesDecresases = incOrDec(ultData[1].text)
    skills.append(charaSkill)
    if len(tables)>3:
        skills+=tables[3:]
    return skills


def get_chara_real_name(charaId):
    charaId = charaId.lower()
    for name, rejexes in charaNames.unitNames.items():
        if any(len(re.findall(rejex.lower(), charaId)) > 0 for rejex in rejexes):
            print(name)
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
    elif chara.name == 'elizabeth_of_reincarnation1':
        chara.imageUrl='https://gcdatabase.com/images/characters/elizabeth_of_reincarnation/ssrl_portrait.png'
    elif chara.name == 'slater2':
        chara.names[0]= 'rSRSlater'
    return chara

def get_atributes_order(data):
    attrs = [x.text for x in data.find_all("h2", class_="whitetext")]
    out = []
    for att in attrs:
        if any(att == aux for aux in ['Commandment','Grace','Holy Relic','Bind']) and att not in out:
            out.append(att)
    return out

def skips(page:BeautifulSoup,pos):
    skiped_table_headers = {'Associated with':1,'Misc. Info':4}
    for header in page.find_all("h2", class_="whitetext"):
        if header.text == 'Skills': ##we reached destination
            break
        if header.text in skiped_table_headers:
            pos += skiped_table_headers[header.text]
    return pos

def getTables(page:BeautifulSoup):
    headers = page.find_all("h2", class_="whitetext")
    tables = {}
    for header in headers:
        table = header.find_next('div')
        if table:
            tables[header.text]=table.find_all(
        'table', class_='table table-dark table-striped table-bordered')
            if len(tables[header.text]) ==1:
                tables[header.text]=tables[header.text][0]
    return tables

def getTransformationKey(tables):
    tKeys = ['Passive/Unique (Titan Form)','Passive/Unique (Post-Transformation)']
    for k in tKeys:
        if k in tables:
            return k
        
def getCharaSkills(tables):
    skills = []
    skillLabels = ['Skills','SSR Skills','LR Skills']
    for label in skillLabels:
        if label in tables:
            skills+=get_skills_ult(tables[label])
    return skills


def getCharaPassives(tables):
    passiveLabels = ['Passive/Unique','SSR Passive','LR Passive','Passive/Unique (Titan Form)','Passive/Unique (Post-Transformation)']
    passives = []
    for label in passiveLabels:
        if label in tables:
            passives.append(parseText(tables[label].find_next('td').text))
    return '\n------------------\n'.join(passives)

def parseText(txt:str):
    return txt.replace("\n","").replace("\t","")

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
    # rarity, attribute, race
    tables = getTables(page)
    data = tables['Basic Info'].find_all('td')
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
    #pos += 1
    #pos = skips(page,pos)
    chara.skills = getCharaSkills(tables)
    # pasive
    chara.passive = getCharaPassives(tables)
    if 'Commandment' in tables:
        chara.commandment = parseText(tables['Commandment'].find_next('td').text)
    if 'Grace' in tables:
        chara.grace = parseText(tables['Grace'].find_next('td').text)
    if 'Holy Relic' in tables:
        chara.relic = parseText(tables['Holy Relic'].find_all('td')[-1].text)
    if 'Bind' in tables:
        pass
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
