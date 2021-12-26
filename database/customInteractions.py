from pprint import pprint
from utils import databaseUtils, gcDatabaseWebScrapper
from usefullobjects import objectParser


def update_names_on_chara(con, charaId, newNames: list):
    databaseUtils.update(
        con, 'chara', {'names': ','.join(newNames)}, f'name="{charaId}"')


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
    for chara in charasToUpdate:
        print(chara.name)
        delete_chara(con, chara)
        insert_chara(con, chara)
    con.commit()
    return True


def get_update_charas_list(oldCharas, updateCharas):
    toUpdate = []
    count = 0
    for upChara in updateCharas:
        chara = [chara for chara in oldCharas if chara.name == upChara.name]
        if len(chara) < 1:
            toUpdate.append(upChara)
            continue
        chara = chara[0]
        if not (chara.passive == upChara.passive and
                str(chara.skills) == str(upChara.skills) and
                chara.relic == upChara.relic and
                chara.commandment == upChara.commandment and
                chara.grace == upChara.grace):
            # print(chara.passive == upChara.passive, str(chara.skills) == str(upChara.skills), chara.relic ==
            # upChara.relic, chara.commandment == upChara.commandment, chara.grace == upChara.grace)
            chara.passive = upChara.passive
            chara.skills = upChara.skills
            chara.relic = upChara.relic
            chara.commandment = upChara.commandment
            chara.grace = upChara.grace
            toUpdate.append(chara)
    return toUpdate


def run_chara_update(con, baseUrl):
    charaUrls = gcDatabaseWebScrapper.getCharaUrls(baseUrl+'/characters')
    charas = [gcDatabaseWebScrapper.getCharaDataFromUrl(
        f'{baseUrl}/{charaUrl}') for charaUrl in charaUrls]
    currentCharas = databaseUtils.select(con, 'chara')
    currentCharas = [objectParser.dbCharaToObj(
        dbChara) for dbChara in currentCharas]
    charasToUpdate = get_update_charas_list(currentCharas, charas)
    if update_charas(con, charasToUpdate):
        print('Updated sucesfully')


def delete_chara(con, chara):
    databaseUtils.delete(con, 'chara', f'name = "{chara.name}"')
    con.commit()


def insert_chara(con, chara):
    cursor = con.cursor()
    data = [chara.name, ','.join(chara.names), chara.customName, chara.unitName, chara.rarity,
            chara.attribute, ','.join(chara.race), '|'.join([str(gear)for gear in chara.gear]), chara.imageUrl, '|'.join([str(skill) for skill in chara.skills]), chara.passive, chara.commandment, chara.grace, chara.relic, chara.charaUrl]
    cursor.execute(
        'insert into chara values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', data)
    con.commit()
