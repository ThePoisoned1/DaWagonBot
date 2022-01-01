import sqlite3

from utils import databaseUtils, gcDatabaseWebScrapper
from pprint import pprint
from usefullobjects.gcObjects import Team
import re


def createTables(con):
    cursor = con.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS attribute(
        name text,
        PRIMARY KEY (name))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS rarity(
        name text,
        PRIMARY KEY (name))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS race(
        name text,
        PRIMARY KEY (name))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS chara(
        name text,
        names text,
        customName text,
        unitName text,
        rarity text,
        attribute text,
        race text,
        gear text,
        imageUrl text,
        skills text,
        passive text,
        commandment text,
        grace text,
        relic text,
        charaUrl text,
        binImg text,
        realName text,
        PRIMARY KEY (name),
        FOREIGN KEY (rarity) REFERENCES rarity(name),
        FOREIGN KEY (attribute) REFERENCES attribute(name))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS team(
        name text,
        unitNames text,
        position text,
        explanation text,
        replacements text,
        picUrl text,
        otherNames text,
        PRIMARY KEY (name))''')
    con.commit()


def insertStuff(con, stuffList, tableName):
    cursor = con.cursor()
    for race in stuffList:
        cursor.execute(
            f'INSERT INTO {tableName} values (?)', [race]
        )
    con.commit()


def insertCharas(con):
    baseUrl = 'https://gcdatabase.com'
    charasUrls = gcDatabaseWebScrapper.getCharaUrls(baseUrl+'/characters')
    allcharas = []
    for charaUrl in charasUrls:
        allcharas.append(gcDatabaseWebScrapper.getCharaDataFromUrl(
            f'{baseUrl}/{charaUrl}'))
    cursor = con.cursor()
    allcharas = gcDatabaseWebScrapper.checkForSrSsr(allcharas)
    for chara in allcharas:
        data = [chara.name, ','.join(chara.names), chara.customName, chara.unitName, chara.rarity,
                chara.attribute, ','.join(chara.race), '|'.join([str(gear)for gear in chara.gear]), chara.imageUrl, '|'.join([str(skill) for skill in chara.skills]), chara.passive, chara.commandment, chara.grace, chara.relic, chara.charaUrl, chara.binImg]
        cursor.execute(
            'insert into chara values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', data)
    con.commit()


def insertGwTeams(con):
    teams = []
    # AM
    amTeam = Team()
    amTeam.name = 'Assault Meliodas'
    amTeam.otherNames = ['AM']
    amTeam.unitNames = ['assault_mode_meliodas1',
                        'drole2', 'sigurd1', 'melascula2']
    amTeam.position = ['Offense']
    amTeam.replacements = {'sigurd1': ['gloxinia2']}
    amTeam.picUrl = 'https://cdn.discordapp.com/attachments/923735234091036722/924456839066812426/file.png'
    teams.append(amTeam)
    # Glue
    glue = Team()
    glue.name = 'T1 Glue Eater'
    glue.otherNames = ['T1 Glue']
    glue.unitNames = ['theone_escanor1',
                      'goddess_elizabeth1', 'gowther4', 'king1']
    glue.position = ['Offense']
    glue.replacements = {}
    glue.picUrl = 'https://cdn.discordapp.com/attachments/923735234091036722/924457591483015198/file.png'
    teams.append(glue)
    # AA
    archangels = Team(name='Archangels')
    archangels.otherNames = ['AA']
    archangels.unitNames = ['elizabeth_hawk4',
                            'tarmiel1', 'margaret_ludociel1', 'sariel1']
    archangels.position = ['Offense', 'Defense']
    archangels.replacements = {'elizabeth_hawk4': [
        'goddess_elizabeth1', 'elizabeth2', 'elizabeth_hawk3']}
    archangels.picUrl = 'https://cdn.discordapp.com/attachments/923735234091036722/924458222599946270/file.png'
    teams.append(archangels)
    # Kyori
    kyori = Team(name='Kyori')
    kyori.otherNames = ['Kyospeet']
    kyori.unitNames = ['fraudrin1', 'kyo1', 'yagami1', 'monspeet2']
    kyori.position = ['Defense']
    kyori.replacements = {
        'fraudrin1': ['athena1', 'drole1'],
        'yagami1': ['executioner_zeldris1', 'eastin2']
    }
    kyori.picUrl = 'https://cdn.discordapp.com/attachments/923735234091036722/924458956829655090/file.png'
    teams.append(kyori)
    cursor = con.cursor()
    for team in teams:
        data = [team.name, ','.join(team.unitNames), ','.join(
            team.position), team.explanation, str(team.replacements), team.picUrl, ','.join(team.otherNames)]
        cursor.execute(
            'insert into team values (?,?,?,?,?,?,?)', data)
    con.commit()


def startDb(con):
    createTables(con)
    races = ['Unknown', 'Goddess', 'Fairy', 'Giant', 'Demon', 'Human']
    insertStuff(con, races, 'race')
    rarities = ['SSR', 'SR', 'R']
    insertStuff(con, rarities, 'rarity')
    attributes = ['Vitality', 'Strength', 'Speed']
    insertStuff(con, attributes, 'attribute')
    insertCharas(con)
    insertGwTeams(con)
