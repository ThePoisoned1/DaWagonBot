from .gcObjects import *


def dbCharaToObj(dbChara):
    chara = Character()
    chara.name = dbChara[0]
    chara.names = dbChara[1].split(',')
    chara.customName = dbChara[2]
    chara.unitName = dbChara[3]
    chara.rarity = dbChara[4]
    chara.attribute = dbChara[5]
    chara.race = dbChara[6].split(',')
    if len(dbChara[7]) > 0:
        gears = dbChara[7].split('|')
        for gearData in gears:
            gearDict = eval(gearData)
            gear = GearSet()
            gear.bonus = gearDict.get('bonus')
            gear.bonus = gear.bonus.split(',') if gear.bonus else gear.bonus
            gear.rolls = gearDict.get('rolls')
            gear.rolls = gear.rolls.split(',') if gear.rolls else gear.rolls
            chara.gear.append(gear)
    chara.imageUrl = dbChara[8]
    skills = dbChara[9].split('|')
    try:
        chara.skills = [Skill.skillFromDictStr(skill) for skill in skills]
    except Exception:
        chara.skills = []
    chara.passive = dbChara[10]
    chara.commandment = dbChara[11]
    chara.grace = dbChara[12]
    chara.relic = dbChara[13]
    chara.charaUrl = dbChara[14]
    chara.binImg = dbChara[15] if len(dbChara) > 15 else ''
    chara.realName = dbChara[16] if len(dbChara) > 16 else ''
    return chara


def dbTeamToObj(dbTeam):
    team = Team()
    team.name = dbTeam[0]
    team.unitNames = dbTeam[1].split(',')
    team.position = dbTeam[2].split(',')
    team.explanation = dbTeam[3]
    team.replacements = eval(dbTeam[4])
    team.picUrl = dbTeam[5]
    team.otherNames = dbTeam[6].split(',')
    return team
