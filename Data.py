import enum
from typing import TypeVar

TPlayer = TypeVar("TPlayer", bound="Player")

class Stage(enum.Enum):
    PREPARE = '开始阶段'
    TRIAL = '判定阶段'
    DRAW_CARD = '摸牌阶段'
    PLAY_CARD = '出牌阶段'
    DISCARD_CARD = '弃牌阶段'
    OVER = '结束阶段'


class PlayerType(enum.Enum):
    ALL = 0
    TEAMMATE = 1
    ENEMY = 2
    TEAMMATE_NO_SELF = 3
    OTHERS = 4


class Mark(enum.Enum):
    JIANDAO = '剑道标记'
    SHOUJIAN = '授剑标记'
    DIHUI = '诋毁标记'
    XIWEN = '檄文标记'
    PODI = '破敌标记'
    JIANMIE = '歼灭标记'
    ZHENLIE = '贞烈标记'
    ZHUDING = '铸鼎标记'
    ZUIJIU = '醉酒标记'
    JIU = '酒标记'


class Flag(enum.Enum):
    CANTREACT = '无法响应'


