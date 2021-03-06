from dataclasses import dataclass, field
from collections import OrderedDict
from . import charaNames


@dataclass
class GearSet():
    bonus: list = field(default_factory=list)
    rolls: list = field(default_factory=list)

    def __str__(self):
        return str({
            'bonus': ','.join(self.bonus),
            'rolls': ','.join(self.rolls)
        })

    def __eq__(self, __o: object) -> bool:
        print(self, __o)
        print(len(self.bonus) != len(__o.bonus)
              or len(self.rolls) != len(__o.rolls))
        if isinstance(__o, GearSet):
            if len(self.bonus) != len(__o.bonus) or len(self.rolls) != len(__o.rolls):
                return False
            print(self.bonus)
            for bon in self.bonus:
                print(bon)
                if bon not in __o.bonus:
                    return False
            print(self.rolls)
            for roll in self.rolls:
                print(roll)
                if roll not in __o.rolls:
                    return False
        else:
            return False
        return True

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)

    def getGearData(self):
        out = 'Set => '
        out += '/'.join(self.bonus) if len(self.bonus) > 0 else 'Not set'
        out += '\nSubstats => '
        out += ', '.join(self.rolls) if len(self.rolls) > 0 else 'Not set'
        return out

    def get_gear_short_data(self):
        bonuses = '/'.join(self.bonus)
        substats = ', '.join(self.rolls)
        return f'{bonuses} ({substats})'

    @staticmethod
    def get_bonus_weights():
        weights = OrderedDict()
        weights['Attack'] = 4
        weights['Defense'] = 2
        weights['Hp'] = 4
        weights['Crit Chance'] = 4
        weights['Crit Resistance'] = 2
        weights['Recovery Rate'] = 2
        weights['Crit Damage'] = 2
        weights['Crit Defense'] = 2
        weights['Lifesteal'] = 2
        return weights

    @staticmethod
    def get_bonuses():
        return GearSet.get_bonus_weights().keys()

    @staticmethod
    def get_rolls():
        return {
            'Top': ['Pierce Rate', 'Crit Chance', 'Crit Damage', 'Attack'],
            'Mid': ['Defense', 'Resistance', 'Crit Resistance', 'Crit Defense'],
            'Bottom': ['Hp', 'Regeneration Rate', 'Recovery Rate', 'Lifesteal']
        }

    @staticmethod
    def rolls_per_category():
        return 10

    @staticmethod
    def bonus_total_weight():
        return 6

    @staticmethod
    def get_default_rolls():
        return ['Attack', 'Defense', 'Hp']

    @staticmethod
    def get_default_gears():
        gears = OrderedDict()
        gears['HP/DEF'] = GearSet(bonus=['Hp', 'Defense'],
                                  rolls=GearSet.get_default_rolls())
        gears['ATT/CRIT'] = GearSet(bonus=['Attack', 'Crit Damage'],
                                    rolls=GearSet.get_default_rolls())
        gears['HP/CRIT'] = GearSet(bonus=['Hp', 'Crit Damage'],
                                   rolls=GearSet.get_default_rolls())
        gears['ATT/DEF'] = GearSet(bonus=['Attack', 'Defense'],
                                   rolls=GearSet.get_default_rolls())
        return gears

    @staticmethod
    def get_default_gear(gearName):
        return GearSet.get_default_gears().get(gearName)


@dataclass
class Attribute():
    name: str = ''
    color: str = ''


@dataclass
class Rarity():
    name: str = ''


@dataclass
class Race():
    name: str = ''


@dataclass
class Character():
    name: str = ''
    names: list = field(default_factory=list)
    customName: str = ''
    unitName: str = ''
    rarity: str = ''
    attribute: str = ''
    race: list = field(default_factory=list)
    gear: list = field(default_factory=list)
    imageUrl: str = ''
    skills: list = field(default_factory=list)
    passive: str = ''
    commandment: str = ''
    relic: str = ''
    charaUrl: str = ''
    grace: str = ''
    binImg: str = ''
    realName: str = ''

    def getSkillData(self):
        out = []
        count = 0
        for skill in self.skills:
            if count > 0 and count % 3 == 0:
                out.append('------------------')
            out.append(skill.getSkillData())
            count += 1
        return '\n'.join(out)

    @staticmethod
    def chara_can_go_in_team(team, chara):
        for incompatibility in charaNames.incompatibilities:
            if chara.realName in incompatibility and any(unit.realName in incompatibility for unit in team):
                return False
            if chara.realName in [unit.realName for unit in team]:
                return False
        return True


@dataclass
class Skill():
    effects: list = field(default_factory=list)
    isAoE: bool = ''
    increasesDecresases: list = field(default_factory=list)
    skillType: str = ''

    def __str__(self) -> str:
        skillDict = {
            'effects': ','.join(self.effects),
            'isAoE': str(self.isAoE),
            'increasesDecresases': ','.join(self.increasesDecresases),
            'skillType': self.skillType
        }
        return str(skillDict)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Skill):
            return sorted(self.effects) == sorted(__o.effects)\
                and self.isAoE == __o.isAoE\
                and sorted(self.increasesDecresases) == sorted(__o.increasesDecresases)\
                and self.skillType == __o.skillType
        else:
            return False

    def getSkillData(self):
        effects = ', '.join(self.effects)
        AoE = 'AoE' if self.isAoE else 'Single'
        incDec = ', '.join(self.increasesDecresases) + ' |'
        incDec = incDec if len(incDec) > 2 else ''
        return f'-{self.skillType}: {incDec} {effects} | {AoE}'

    @staticmethod
    def skillFromDictStr(skillData: str):
        skillDict = eval(skillData)
        skill = Skill()
        skill.skillType = skillDict.get('skillType')
        skill.effects = skillDict.get('effects').split(',')if len(
            str(skillDict.get('effects'))) > 0 else []
        skill.isAoE = skillDict.get('isAoE') == 'True'
        skill.increasesDecresases = skillDict.get(
            'increasesDecresases').split(',') if len(str(skillDict.get('increasesDecresases'))) > 5 else []
        return skill


@dataclass
class Team():
    name: str = ''
    unitNames: str = ''
    position: list = field(default_factory=list)
    explanation: str = ''
    replacements: dict = field(default_factory=dict)
    picUrl: str = ''
    otherNames: list = field(default_factory=list)

    def is_valid_team_positions(self, position):
        return position in self.get_valid_team_postions()

    @staticmethod
    def get_valid_team_postions():
        return ['Offense', 'Defense', 'Einek', 'Kelak', 'Akumu', 'Belgius', 'PvP']

    def get_guild_wars_positions():
        return ['Offense', 'Defense']
