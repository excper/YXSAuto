import enum
import random
from functools import total_ordering
# from types import Union
from typing import Callable


class CardType(enum.Enum):
    BASIC = '基本'

    EQUIPMENT = '装备'
    WEAPON = '武器'
    ARMOR = '防具'
    OFFENSIVE_HORSE = '进攻马'
    DEFENSIVE_HORSE = '防御马'

    MAGIC = '锦囊'
    DELAYED_MAGIC = '延时锦囊'
    INSTANT_MAGIC = '非延时锦囊'
    INDIVIDUAL_MAGIC = '单体锦囊'
    GROUP_MAGIC = '群锦囊'
    BAD_MAGIC = '伤害性锦囊'
    GOOD_MAGIC = '增益性锦囊'


class CardSuit(enum.Enum):
    SPADE = '♠'
    HEART = '♡'
    CLUB = '♣'
    DIAMOND = '♢'


class CardName(enum.Enum):
    SHA = '杀'
    SHAN = '闪'
    YAO = '药'
    JIU = '酒'
    TANNANGQUWU = '探囊取物'
    FUDICHOUXIN = '釜底抽薪'
    FENGHUOLANGYAN = '烽火狼烟'
    WANJIANQIFA = '万箭齐发'
    WUGUFENGDENG = '五谷丰登'
    JUEDOU = '决斗'
    WUXIEKEJI = '无懈可击'
    HUADIWEILAO = '画地为牢'
    BINGLIANGCUNDUAN = '兵粮寸断'
    SHOUPENGLEI = '手捧雷'
    HUFU = '虎符'
    LONGLINDAO = '龙鳞刀'
    BOLANGCHUI = '博浪锤'
    LUYEQIANG = '芦叶枪'
    XUANHUAFU = '宣花斧'
    FANGYUMA = '防御马'
    JINGONGMA = '进攻马'
    YURUYI = '玉如意'
    QIANKUNDAI = '乾坤袋'
    WUZHONGSHENGYOU = '无中生有'
    JIEDAOSHAREN = '借刀杀人'


cards_data = [
    (CardSuit.SPADE, 1, CardName.JUEDOU, [CardType.INSTANT_MAGIC, CardType.INDIVIDUAL_MAGIC, CardType.BAD_MAGIC]),
    (CardSuit.SPADE, 2, CardName.YURUYI, [CardType.EQUIPMENT, CardType.ARMOR]),
    (CardSuit.SPADE, 3, CardName.SHA, [CardType.BASIC]),
    (CardSuit.SPADE, 4, CardName.FUDICHOUXIN, [CardType.INSTANT_MAGIC, CardType.INDIVIDUAL_MAGIC]),
    (CardSuit.SPADE, 5, CardName.FANGYUMA, [CardType.EQUIPMENT, CardType.DEFENSIVE_HORSE]),
    (CardSuit.SPADE, 6, CardName.SHA, [CardType.BASIC]),
    (CardSuit.SPADE, 7, CardName.SHA, [CardType.BASIC]),
    (CardSuit.SPADE, 8, CardName.SHA, [CardType.BASIC]),
    (CardSuit.SPADE, 9, CardName.JIU, [CardType.BASIC]),
    (CardSuit.SPADE, 10, CardName.SHA, [CardType.BASIC]),
    (CardSuit.SPADE, 11, CardName.SHA, [CardType.BASIC]),
    (CardSuit.SPADE, 12, CardName.WUXIEKEJI, [CardType.INSTANT_MAGIC]),
    (CardSuit.SPADE, 12, CardName.XUANHUAFU, [CardType.EQUIPMENT, CardType.WEAPON]),
    (CardSuit.SPADE, 13, CardName.JIEDAOSHAREN, [CardType.INSTANT_MAGIC, CardType.INDIVIDUAL_MAGIC]),
    (CardSuit.HEART, 1, CardName.HUFU, [CardType.EQUIPMENT, CardType.WEAPON]),
    (CardSuit.HEART, 2, CardName.SHAN, [CardType.BASIC]),
    (CardSuit.HEART, 3, CardName.YAO, [CardType.BASIC]),
    (CardSuit.HEART, 4, CardName.SHAN, [CardType.BASIC]),
    (CardSuit.HEART, 5, CardName.TANNANGQUWU, [CardType.INSTANT_MAGIC, CardType.INDIVIDUAL_MAGIC]),
    (CardSuit.HEART, 6, CardName.YAO, [CardType.BASIC]),
    (CardSuit.HEART, 7, CardName.JUEDOU, [CardType.INSTANT_MAGIC, CardType.INDIVIDUAL_MAGIC, CardType.BAD_MAGIC]),
    (CardSuit.HEART, 8, CardName.SHAN, [CardType.BASIC]),
    (CardSuit.HEART, 9, CardName.WUZHONGSHENGYOU, [CardType.INSTANT_MAGIC, CardType.INDIVIDUAL_MAGIC]),
    (CardSuit.HEART, 10, CardName.SHA, [CardType.BASIC]),
    (CardSuit.HEART, 11, CardName.SHA, [CardType.BASIC]),
    (CardSuit.HEART, 12, CardName.WUXIEKEJI, [CardType.INSTANT_MAGIC]),
    (CardSuit.HEART, 13, CardName.SHAN, [CardType.BASIC]),
    (CardSuit.CLUB, 1, CardName.SHOUPENGLEI, [CardType.DELAYED_MAGIC]),
    (CardSuit.CLUB, 2, CardName.LONGLINDAO, [CardType.EQUIPMENT, CardType.WEAPON]),
    (CardSuit.CLUB, 3, CardName.TANNANGQUWU, [CardType.INSTANT_MAGIC, CardType.INDIVIDUAL_MAGIC]),
    (CardSuit.CLUB, 4, CardName.FUDICHOUXIN, [CardType.INSTANT_MAGIC, CardType.INDIVIDUAL_MAGIC]),
    (CardSuit.CLUB, 5, CardName.FENGHUOLANGYAN, [CardType.INSTANT_MAGIC, CardType.GROUP_MAGIC, CardType.BAD_MAGIC]),
    (CardSuit.CLUB, 6, CardName.BINGLIANGCUNDUAN, [CardType.DELAYED_MAGIC, CardType.INDIVIDUAL_MAGIC]),
    (CardSuit.CLUB, 7, CardName.SHA, [CardType.BASIC]),
    (CardSuit.CLUB, 8, CardName.SHA, [CardType.BASIC]),
    (CardSuit.CLUB, 9, CardName.SHA, [CardType.BASIC]),
    (CardSuit.CLUB, 10, CardName.SHA, [CardType.BASIC]),
    (CardSuit.CLUB, 11, CardName.QIANKUNDAI, [CardType.EQUIPMENT, CardType.ARMOR]),
    (CardSuit.CLUB, 12, CardName.LUYEQIANG, [CardType.EQUIPMENT, CardType.WEAPON]),
    (CardSuit.CLUB, 13, CardName.FENGHUOLANGYAN, [CardType.INSTANT_MAGIC, CardType.GROUP_MAGIC, CardType.BAD_MAGIC]),
    (CardSuit.DIAMOND, 1, CardName.WANJIANQIFA, [CardType.INSTANT_MAGIC, CardType.GROUP_MAGIC, CardType.BAD_MAGIC]),
    (CardSuit.DIAMOND, 2, CardName.SHAN, [CardType.BASIC]),
    (CardSuit.DIAMOND, 3, CardName.WUGUFENGDENG, [CardType.INSTANT_MAGIC, CardType.GROUP_MAGIC, CardType.GOOD_MAGIC]),
    (CardSuit.DIAMOND, 4, CardName.FUDICHOUXIN, [CardType.INSTANT_MAGIC, CardType.INDIVIDUAL_MAGIC]),
    (CardSuit.DIAMOND, 5, CardName.BOLANGCHUI, [CardType.EQUIPMENT, CardType.WEAPON]),
    (CardSuit.DIAMOND, 6, CardName.HUADIWEILAO, [CardType.DELAYED_MAGIC, CardType.INDIVIDUAL_MAGIC]),
    (CardSuit.DIAMOND, 7, CardName.SHA, [CardType.BASIC]),
    (CardSuit.DIAMOND, 8, CardName.SHAN, [CardType.BASIC]),
    (CardSuit.DIAMOND, 9, CardName.JIU, [CardType.BASIC]),
    (CardSuit.DIAMOND, 10, CardName.SHAN, [CardType.BASIC]),
    (CardSuit.DIAMOND, 11, CardName.SHA, [CardType.BASIC]),
    (CardSuit.DIAMOND, 12, CardName.SHA, [CardType.BASIC]),
    (CardSuit.DIAMOND, 12, CardName.YAO, [CardType.BASIC]),
    (CardSuit.DIAMOND, 13, CardName.JINGONGMA, [CardType.EQUIPMENT, CardType.OFFENSIVE_HORSE])
]

# attack_value, defense_value, total_value
cards_value_data = {
    CardName.SHA: (5, 5, 5),
    CardName.SHAN: (0, 8, 6),
    CardName.YAO: (0, 10, 8),
    CardName.JIU: (5, 9, 7),

    CardName.FUDICHOUXIN: (6, 0, 6),
    CardName.TANNANGQUWU: (6, 0, 7),
    CardName.WUZHONGSHENGYOU: (6, 6, 8),

}


def get_all_cards():
    cards = [Card(*card) for card in cards_data]
    random.shuffle(cards)
    return cards


@total_ordering
class Card:
    def __init__(self, suit=None, figure=None, name=None, card_type=None):
        self.type = card_type
        self.name = name
        self.distance = 0
        self.figure = figure
        self.suit = suit
        self.value = None
        self.attack_value = 0
        self.defense_value = 0
        self.set_value()
        self.set_distance()
        self.deck_type = None

    def set_value(self, value=None):
        if value is None:
            match self.name:
                case CardName.SHA:
                    self.value = 5
                    self.attack_value = 5
                    self.defense_value = 5
                case CardName.SHAN:
                    self.value = 6
                    self.attack_value = 0
                    self.defense_value = 8
                case CardName.YAO:
                    self.value = 8
                    self.attack_value = 0
                    self.defense_value = 10
                case CardName.JIU:
                    self.value = 7
                case CardName.WUGUFENGDENG:
                    self.value = 5
                case CardName.YAO:
                    self.value = 8
                case CardName.SHOUPENGLEI:
                    self.value = 3
                case _:
                    self.value = 5
        else:
            self.value = int(value)

    def set_distance(self, value=None):
        if value is None:
            match self.name:
                case CardName.BOLANGCHUI | CardName.LUYEQIANG:
                    self.distance = 2
                case CardName.LONGLINDAO:
                    self.distance = 1

    def __str__(self):
        return f'{self.suit.value}{self.figure}{self.name.value}'

    def __repr__(self):
        return f'{self.suit.value}{self.figure}{self.name.value}'

    def __eq__(self, other):
        if type(other) == type(self):
            return self.name == other.name and self.suit == other.suit and self.figure == other.figure
        else:
            return False

    def __ne__(self, other):
        return not (self.value == other.value)

    def __lt__(self, other):
        return self.value < other.value


class CardStrainer(object):
    def __init__(self, pattern):
        super().__init__()
        self.pattern = pattern

    def has(self, card: Card):
        if isinstance(self.pattern, CardType):
            return self.pattern in card.type
        elif isinstance(self.pattern, CardName):
            return card.name == self.pattern
        elif isinstance(self.pattern, Callable):
            return self.pattern(card)
        elif hasattr(self.pattern, '__iter__'):
            if len(self.pattern) > 0:
                for pattern in self.pattern:
                    strainer = CardStrainer(pattern)
                    if strainer.has(card):
                        return True
                return False
        elif self.pattern is None:
            return True
        else:
            raise NotImplemented


if __name__ == '__main__':
    test_card = [Card(*cards_data[0]), Card(*cards_data[1])]
    strainer = CardStrainer([CardName.JUEDOU, CardName.YURUYI])
    for card in test_card:
        print(strainer.has(card))


