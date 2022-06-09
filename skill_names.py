import enum


class SkillName(enum.Enum):
    LUOYAN = '落雁', 0
    HEQIN = '和亲', 1
    BUDAO = '布道', 1
    TAIJI = '太极', 2
    JUJIAN = '举荐', 1
    SHENTAN = '神探', 1
    WUSHENG = '武圣', 0
    DANQI = '单骑', 0
    BUDAO2 = '补刀', 2
    MENSHEN = '门神', 2
    FANJI = '反击', 2
    TIANLANG = '天狼', 0
    DIEHUN = '蝶魂', 2
    YUEFA = '约法', 2
    TIANDU = '天妒', 0
    WANGSHEN = '忘身', 1

    SHOUJIAN = '授剑', 1
    JIANJI = '剑技', 2
    JIANDAO = '剑道', 0

    BAWANG = '霸王', 0
    POFU = '破釜', 1

    XIANGMA = '相马', 0
    SHICAI = '试才', 1

    QIUHUANG = '求凰', 1
    JIANLIE = '谏猎', 2

    QINXIN = '琴心', 1
    XIANGSHOU = '相守', 2

    FAJIA = '法家', 2
    BIANFA = '变法', 2

    SHISHENG = '诗圣', 2
    BEIMIN = '悲悯', 2

    BINGXIAN = '兵仙', 0
    GONGXIN = '攻心', 1

    ZHUDING = '铸鼎', 2
    ZHISHUI = '治水', 2

    LIANPO = '连破', 2
    FUJING = '负荆', 1

    RENDE = '仁德', 2
    JIEYI = '结义', 2

    SHESHEN = '舍身', 2
    JUEBIE = '诀别', 2

    SHUCAI = '疏财', 1

    YUREN = '驭人', 1
    JIANXIONG = '奸雄', 1

    FUCHOU = '复仇', 2
    GANGYI = '刚毅', 0

    YAOYI = '徭役', 2
    JUJIAN2 = '拒谏', 1

    JIASHA = '袈裟', 2
    PUDU = '普渡', 1

    MIAOJI = '妙计', 0
    DONGCHA = '洞察', 0

    LIANCE = '连策', 2
    NISHI = '逆势', 2

    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return self.value[0]