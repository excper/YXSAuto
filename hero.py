from collections import defaultdict

import heroes_data
from skill import Skill
from skill_names import SkillName


class HeroFactory:
    @staticmethod
    def get_hero(name):
        for hero in heroes_data.heroes:
            if name in hero:
                return Hero(*hero)


class Hero:
    def __init__(self, name='步兵', max_hp=99, gender=1, skills=None):
        self._name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.gender = gender
        self._skills = []
        self.max_hand_cards_patch = 0

        self.is_alive = True
        self.range_to_others = 1
        self.range_from_others = 1
        self.attack_range_to_others = 1
        self.attack_range_from_others = 1

        self.sha_limit = 1

        self.player = None
        self.want_card = None
        self.marks = defaultdict(lambda: 0)

        for skill_name in skills:
            self._skills.append(Skill(skill_name))

    @property
    def name(self):
        return self._name

    @property
    def skills(self):
        return self._skills

    @skills.setter
    def skills(self, value):
        self._skills = value

    def change_hp(self, value, card=None):
        self.hp += value

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def has_skill(self, skill_name):
        if isinstance(skill_name, SkillName):
            skill_name = [skill_name]
        own_skills = [own_skill.name for own_skill in self.skills]
        for sn in skill_name:
            if sn in own_skills:
                return True
        return False

    def get_skill_names(self, skill_name: SkillName):
        if isinstance(skill_name, SkillName):
            skill_name = [skill_name]
        own_skills_names = [own_skill.name for own_skill in self.skills]
        found = []
        for sn in own_skills_names:
            if sn in skill_name:
                found.append(sn)
        return found

    def get_skill(self, skill_name):
        for skill in self.skills:
            if skill.name == skill_name:
                return skill


if __name__ == '__main__':
    pass
