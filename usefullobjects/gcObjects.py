from dataclasses import dataclass, field


@dataclass
class GearSet():
    bonus: list = field(default_factory=list)
    rolls: list = field(default_factory=list)

    def __str__(self):
        return str({
            'bonus': ','.join(self.bonus),
            'rolls': ','.join(self.rolls)
        })

    def getGearData(self):
        out = 'Set => '
        out += '/'.join(self.bonus) if len(self.bonus) > 0 else 'Not set\n'
        out += 'Substats => '
        out += ', '.join(self.rolls) if len(self.rolls) > 0 else 'Not set'
        return out


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

    def getSkillData(self):
        return '\n'.join([skill.getSkillData() for skill in self.skills])


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
        skill.effects = skillDict.get('effects').split(',')
        skill.isAoE = skillDict.get('isAoE') == 'True'
        skill.increasesDecresases = skillDict.get(
            'increasesDecresases').split(',')
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
        return position in ['Offense', 'Defense']

    @staticmethod
    def get_valid_team_postions():
        return ['Offense', 'Defense']
