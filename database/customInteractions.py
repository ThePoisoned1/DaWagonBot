from pprint import pprint
from utils import databaseUtils, gcDatabaseWebScrapper
from usefullobjects import objectParser
from utils import utils


def update_names_on_chara(con, charaId, newNames: list):
    databaseUtils.update(
        con, 'chara', {'names': ','.join(newNames)}, f'name="{charaId}"')


def update_gears_on_chara(con, charaId, newGears: list):
    databaseUtils.update(
        con, 'chara', {'gear': '|'.join([str(gear)for gear in newGears])}, f'name="{charaId}"')


def delete_team(con, teamId):
    databaseUtils.delete(con, 'team', f'name = "{teamId}"')


def insert_team(con, team):
    cursor = con.cursor()
    data = [team.name, ','.join(team.unitNames), ','.join(
            team.position), team.explanation, str(team.replacements), team.picUrl, ','.join(team.otherNames)]
    cursor.execute(
        'insert into team values (?,?,?,?,?,?,?)', data)
    con.commit()


def update_charas(con, charasToUpdate):
    #cursor = con.cursor()
    #cursor.execute('ALTER TABLE chara ADD realName text;')
    for chara in charasToUpdate:
        print(chara.name)
        delete_chara(con, chara)
        insert_chara(con, chara)
    con.commit()
    return True


def get_update_charas_list(oldCharas, updateCharas):
    toUpdate = []
    updateDict = {}
    for chara in oldCharas:
        if isinstance(chara,list):
            print(chara[0])
    print('---')
    for chara in updateCharas:
        if isinstance(chara,list):
            print(chara[0])
    for upChara in updateCharas:
        chara = [chara for chara in oldCharas if chara.name == upChara.name]
        if len(chara) < 1:
            toUpdate.append(upChara)
            if not updateDict.get('New Characters'):
                updateDict['New Characters'] = []
            updateDict['New Characters'].append(upChara.names[0])
            continue
        chara = chara[0]
        update = False
        if chara.names[0]!= upChara.names[0]:
            if not updateDict.get('Name Updates'):
                updateDict['Name Updates'] = []
            updateDict['Name Updates'].append(f'{chara.names[0]} > {upChara.names[0]}')
            chara.names[0]=upChara.names[0]
            update = True
            
        if chara.attribute != upChara.attribute:
            if not updateDict.get('Attribute Updates'):
                updateDict['Attribute Updates'] = []
            chara.attribute=upChara.attribute
            update = True
            updateDict['Attribute Updates'].append(upChara.names[0])
        if chara.passive != upChara.passive:
            if not updateDict.get('Passive Updates'):
                updateDict['Passive Updates'] = []
            chara.passive = upChara.passive
            update = True
            updateDict['Passive Updates'].append(upChara.names[0])
        if chara.skills != upChara.skills:
            if not updateDict.get('Skill Updates'):
                updateDict['Skill Updates'] = []
            chara.skills = upChara.skills
            update = True
            updateDict['Skill Updates'].append(upChara.names[0])
        if chara.relic != upChara.relic:
            if not updateDict.get('Relic Updates'):
                updateDict['Relic Updates'] = []
            chara.relic = upChara.relic
            update = True
            updateDict['Relic Updates'].append(upChara.names[0])
        if chara.commandment != upChara.commandment:
            if not updateDict.get('Commandment Updates'):
                updateDict['Commandment Updates'] = []
            update = True
            chara.commandment = upChara.commandment
            updateDict['Commandment Updates'].append(upChara.names[0])
        if chara.grace != upChara.grace:
            if not updateDict.get('Grace Updates'):
                updateDict['Grace Updates'] = []
            update = True
            chara.grace = upChara.grace
            updateDict['Grace Updates'].append(upChara.names[0])
        # print(chara.passive == upChara.passive, str(chara.skills) == str(upChara.skills), chara.relic ==
        # upChara.relic, chara.commandment == upChara.commandment, chara.grace == upChara.grace)
        if chara.binImg != upChara.binImg:
            chara.binImg = upChara.binImg
            update = True
        if chara.realName != upChara.realName:
            chara.realName = upChara.realName
            update = True
        if update:
            toUpdate.append(chara)
    return toUpdate, updateDict

def run_chara_update(con, baseUrl):
    charaUrls = gcDatabaseWebScrapper.getCharaUrls(baseUrl+'/characters')
    charas = [gcDatabaseWebScrapper.getCharaDataFromUrl(
        f'{baseUrl}/{charaUrl}') for charaUrl in charaUrls]
    charas = gcDatabaseWebScrapper.checkForSrSsr(charas)
    currentCharas = databaseUtils.select(con, 'chara')
    currentCharas = [objectParser.dbCharaToObj(
        dbChara) for dbChara in currentCharas]
    charasToUpdate, updateDict = get_update_charas_list(currentCharas, charas)
    pprint(updateDict)

    if update_charas(con, charasToUpdate):
        print('Updated sucesfully')
    if len(updateDict)<1:
        updateDict = {'Nothing':'LMAO'}
    return utils.embed_from_dict('Database Updated','Following charas have been altered',updateDict)


def delete_chara(con, chara):
    databaseUtils.delete(con, 'chara', f'name = "{chara.name}"')
    con.commit()


def insert_chara(con, chara):
    cursor = con.cursor()
    data = [chara.name, ','.join(chara.names), chara.customName, chara.unitName, chara.rarity,
            chara.attribute, ','.join(chara.race), '|'.join([str(gear)for gear in chara.gear]), chara.imageUrl, '|'.join([str(skill) for skill in chara.skills]), chara.passive, chara.commandment, chara.grace, chara.relic, chara.charaUrl, chara.binImg, chara.realName]
    cursor.execute(
        'insert into chara values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', data)
    con.commit()
