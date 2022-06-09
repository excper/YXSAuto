from cards import Card


class DamageType:
    SHA = '杀'
    MAGIC = '锦囊'
    SKILL = '技能'


class Damage:
    def __init__(self, count=1, source=None, target=None, damage_type=None, card=None):
        self.count = count
        self.source = source
        self.target = target
        self.damage_type = damage_type
        self.card = card


damage = Damage(count=1, source=None, card=Card())
