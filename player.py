import enum
import random
from typing import Callable

from Data import PlayerType, Stage, Flag, Mark
from cards import Card, CardName, CardStrainer, CardType, CardSuit
from damage import Damage, DamageType
from deck import DeckType, Deck
from hero import Hero
from judge import Judge
from skill_names import SkillName

from typing import TypeVar

TPlayer = TypeVar("TPlayer", bound="Player")

class PlayerStrategy(enum.Enum):
    KEEPCARD = '保持手牌'
    NORMAL = '正常'
    WASTECARD = '少留手牌'


class Player:
    def __init__(self, hero: Hero):
        self.hero = hero
        self.controller = None
        self.want_card = None
        self.team = 0
        self.enemies = []
        self.friends = []
        self.position = None

        self.hand_cards = Deck(DeckType.HAND_DECK)
        self.equipment_cards = Deck(DeckType.EQUIPMENT_DECK)
        self.judgement_cards = Deck(DeckType.JUDGEMENT_DECK)

        self.stages = Stage

        self.skill_ai = SkillAI()
        self.strategy = PlayerStrategy.NORMAL

        if self.hero.has_skill([SkillName.ZHUDING]):
            self.strategy = PlayerStrategy.KEEPCARD

    def use_skill(self, skill_id=0, target=None):
        for skill in self.hero.skills:
            if skill.type == 1:
                self.skill_ai.operate(skill, source=self, to=self.enemies[0])

    def react_skill(self, skill_name: SkillName, target: TPlayer):
        self.skill_ai.operate(self.get_skill(skill_name), self, target)

    def decide_hit_card(self, origin, asked_card, count=1, reason=None):
        if isinstance(reason, Card):
            if reason.name == CardName.JUEDOU:
                if origin.has_skill(SkillName.WUSHENG):
                    return False
        own_cards = self.get_cards(asked_card)
        return len(own_cards) >= count

    def hit_card(self, card, source_card=None):
        print(f'{self}  {card}')
        self.hands_in(card)
        self.controller.player_hit_card(self, card, source_card)

    def choose_player_a_card(self, target: TPlayer, deck_type=DeckType.PLAYER_ALL):
        if deck_type.HAND_DECK:
            if target.hand_cards.cards_count > 0:
                return target.hand_cards.random_pick_cards()
        elif deck_type.EQUIPMENT_DECK:
            if target.equipment_cards.cards_count > 0:
                return target.equipment_cards.random_pick_cards()
        else:
            if self.want_card is not None:
                copied_card = self.want_card
                self.want_card = None
                return copied_card
            else:
                for zb_card in target.get_cards([CardName.FANGYUMA, CardName.YURUYI],
                                               deck_type=DeckType.EQUIPMENT_DECK):
                    return zb_card
                if target.hand_cards.cards_count > 0:
                    return target.hand_cards.random_pick_cards()
                elif target.equipment_cards.cards_count > 0:
                    return target.equipment_cards.random_pick_cards()

    @staticmethod
    def get_strainer(card_filter):
        return card_filter if isinstance(card_filter, CardStrainer) else CardStrainer(card_filter)

    def get_all_cards(self, deck_type=DeckType.HAND_DECK):
        match deck_type:
            case DeckType.HAND_DECK:
                return self.hand_cards
            case DeckType.EQUIPMENT_DECK:
                return self.equipment_cards
            case DeckType.JUDGEMENT_DECK:
                return self.judgement_cards
            case DeckType.PLAYER_OWN:
                return self.hand_cards + self.equipment_cards
            case DeckType.PLAYER_ALL:
                return self.hand_cards + self.equipment_cards + self.judgement_cards
            case _:
                raise ValueError(f'Cannot identify deck type: {deck_type}')

    def has_card(self, card_filter, deck_type=DeckType.HAND_DECK):
        strainer = self.get_strainer(card_filter)
        all_cards = self.get_all_cards(deck_type)
        for card in all_cards:
            if strainer.has(card):
                return True
        return False

    def get_a_card(self, card_filter=None, deck_type=DeckType.HAND_DECK):
        strainer = self.get_strainer(card_filter)
        all_cards = self.get_all_cards(deck_type)
        for card in all_cards:
            if strainer.has(card):
                return card

    def get_cards(self, card_filter, deck_type=DeckType.HAND_DECK) -> list:
        """
        Get all cards with certain pattern.
        :param card_filter: None, CardType, CardName, [CardTypes], [CardNames], function filter
        :param deck_type:
        :return: a list of all matched cards, will not remove original
        """
        strainer = self.get_strainer(card_filter)
        all_cards = self.get_all_cards(deck_type)
        found = []
        for card in all_cards:
            if strainer.has(card):
                if card not in found:
                    found.append(card)
        found.sort(key=lambda card: card.value)
        return found

    def get_random_cards(self, count=1):
        return self.hand_cards.random_pick_cards(count=count)

    def is_friend(self, target):
        return self.team == target.team

    def is_enemy(self, target):
        return target in self.enemies

    def operate(self):
        pass

    def is_equipped(self, card):
        if isinstance(card, Card):
            equipped_names = [card.name for card in self.equipment_cards]
            return card.name in equipped_names
        elif isinstance(card, CardName):
            return card in [card.name for card in self.equipment_cards]

    def use_card(self, card, target, *args):
        print(self, card, target)
        return self.controller.player_use_card(self, card, target, *args)

    def equip_card(self, card, reverse=False):
        second_type = card.type[1]
        if not reverse:
            for a_card in self.equipment_cards:
                if second_type in a_card.type:
                    self.equip_card(a_card, reverse=True)
            print(f'{self}装备了{card}')
            self.hand_cards.remove(card)
            self.equipment_cards.add_cards(card)
        else:
            self.equipment_cards.remove(card)
            print(f'{self}失去了{card}')
            print(f'{self}当前装备区{self.equipment_cards}')
        factor = -1 if reverse else 1
        match card.name:
            case CardName.FANGYUMA:
                self.hero.range_from_others += factor * 1
            case CardName.JINGONGMA:
                self.hero.range_to_others += factor * 1
            case CardName.BOLANGCHUI | CardName.LUYEQIANG:
                self.hero.attack_range_to_others += factor * 2
            case CardName.LONGLINDAO:
                self.hero.attack_range_to_others += factor * 1
            case CardName.QIANKUNDAI:
                self.hero.max_hand_cards_patch += factor * 1
                if reverse:
                    self.controller.deal_cards(self, count=1)
            case CardName.HUFU:
                self.hero.sha_limit += factor * 99

    def hands_in(self, pattern):
        if isinstance(pattern, Card):
            if pattern in self.hand_cards:
                self.hand_cards.remove_card(pattern)
            elif pattern in self.equipment_cards:
                self.equip_card(pattern, reverse=True)
            return pattern
        elif isinstance(pattern, Callable):
            matched_cards = self.hand_cards.get_cards(count=self.hand_cards.cards_count, pattern=pattern)
            return matched_cards
        elif hasattr(pattern, '__iter__'):
            matched_cards = []
            for card in pattern:
                if card in self.hand_cards:
                    matched_cards.append(self.hand_cards.remove_card(card))
                elif card in self.equipment_cards:
                    self.equip_card(card, reverse=True)
                    matched_cards.append(card)
            return matched_cards
        elif pattern is None:
            return None

    def play_card(self):
        self.controller.play_card_start(self)
        self.use_skill()
        if self.controller.player_has_mark(self, Mark.ZHUDING) >= 3:
            self.strategy = PlayerStrategy.NORMAL
        reset = True
        while reset:
            reset = False
            for card in self.get_cards([CardName.TANNANGQUWU, CardName.TANNANGQUWU]):
                valid_targets = self.get_valid_targets(card)
                if self.use_fdtn(valid_targets, card):
                    # raise NotImplemented
                    reset = True
                    break

            if reset:
                continue

            if self.strategy == PlayerStrategy.KEEPCARD:
                if self.hero.hp >= self.hand_cards.cards_count:
                    break
            reset = False
            # print(self.hand_cards)
            for card in self.get_cards(CardName.YAO):
                if self.hero.hp < self.hero.max_hp:
                    self.use_card(card, self)
                    reset = True
            if reset:
                continue

            for card in self.get_cards([CardName.FANGYUMA, CardName.QIANKUNDAI, CardName.YURUYI, CardName.JINGONGMA]):
                if not self.is_equipped(card):
                    self.equip_card(card)
                    reset = True
                    break
            if reset:
                continue

            # for card in self.get_cards(CardType.WEAPON):

            for card in self.get_cards([CardName.FUDICHOUXIN]):
                valid_targets = self.get_valid_targets(card)
                if self.use_fdtn(valid_targets, card):
                    # raise NotImplemented
                    reset = True
                    break

            if reset:
                continue

            for card in self.get_cards(CardName.WUZHONGSHENGYOU):
                self.use_card(card, self)
                reset = True

            if reset:
                continue

            for card in self.get_cards([CardName.FENGHUOLANGYAN, CardName.WANJIANQIFA]):
                self.use_card(card, self.controller.get_players(self, PlayerType.OTHERS))
                reset = True

            if reset:
                continue

            weapon_cards = self.get_cards(CardType.WEAPON)
            distance = self.controller.attack_distance(self, self.enemies[0])
            current_weapon = self.get_weapon()
            if current_weapon is None:
                if len(weapon_cards) == 1:
                    self.equip_card(weapon_cards[0])
                else:
                    if distance > 1:
                        for card in weapon_cards:
                            if distance - card.distance <= 1:
                                self.equip_card(weapon_cards[0])
                                break
            else:
                if len(weapon_cards) > 0:
                    if distance > 1:
                        for card in weapon_cards:
                            if distance - card.distance <= 1:
                                self.equip_card(card)
                                break

            for card in self.get_cards(CardName.SHA):
                if self.hero.sha_limit > 0:
                    targets = self.get_valid_targets(card)
                    targets.sort(key=lambda target: target.hero.hp)
                    for target in targets:
                        if self.is_enemy(target):
                            self.use_card(card, target)
                            self.hero.sha_limit -= 1
                            reset = True
                            break
                else:
                    break

            if reset:
                continue

            for card in self.get_cards([CardName.HUADIWEILAO, CardName.BINGLIANGCUNDUAN]):
                targets = self.get_valid_targets(card)
                for target in targets:
                    if self.is_enemy(target):
                        self.use_card(card, target)
                        reset = True
                        break
            if reset:
                continue

            for card in self.get_cards(CardName.JUEDOU):
                targets = self.get_valid_targets(card)
                if not self.use_duel(targets, card):
                    break
                else:
                    reset = True

            if reset:
                continue

        # time.sleep(5)

    def get_weapon(self):
        for card in self.equipment_cards:
            if CardType.WEAPON in card.type:
                return card

    def use_duel(self, targets, card):
        enemies = [target for target in targets if self.is_enemy(target)]
        enemies.sort(key=lambda target: target.hero.hp)
        for enemy in enemies:
            if len(enemy.hand_cards) == 0 or self.has_skill(SkillName.WUSHENG):
                self.use_card(card, enemy)
                return True
            elif len(self.get_cards(CardName.SHA)) / len(enemy.hand_cards) >= 0.5:
                self.use_card(card, enemy)
                return True
        return False

    def use_fdtn(self, targets, card):
        friends = [target for target in targets if self.is_friend(target)]
        for friend in friends:  # type: Player
            for yc_card in friend.get_cards([CardName.HUADIWEILAO, CardName.BINGLIANGCUNDUAN]):
                self.want_card = yc_card
                if self.use_card(card, friend):
                    # if self.controller.player_use_card(self, card, friend):
                    return True
                else:
                    self.want_card = None
                    return False

        enemies = [target for target in targets if self.is_enemy(target)]
        enemies.sort(key=lambda player: player.hero.hp)
        for enemy in enemies:
            # print(f'enemy is {enemy}')
            for zb_card in enemy.get_cards([CardName.FANGYUMA, CardName.YURUYI],
                                           deck_type=DeckType.EQUIPMENT_DECK):
                # print(zb_card)
                self.want_card = zb_card
                # print(f'want card is {self.want_card}')
                if self.use_card(card, enemy):
                    # if self.controller.player_use_card(self, card, enemy):
                    return True
                else:
                    self.want_card = None
                    return False
            if enemy.has_some_card():
                enemy_weapon = enemy.get_weapon()
                if enemy_weapon is not None:
                    if self.controller.attack_distance(enemy, self) + enemy_weapon.distance > 1:
                        self.want_card = enemy_weapon
                        return self.use_card(card, enemy)
                if self.use_card(card, enemy):
                    return True
            else:
                print('enemy has no card')
        return False

    def pick_enemy(self):
        return self.enemies[0]

    def discard_cards(self, count, stage=Stage.PLAY_CARD):
        self.set_cards_value(stage)
        self.hand_cards.sort()
        removed_cards = self.hand_cards[:count]
        print(f'{self.hero.name}弃置{removed_cards}')
        self.hand_cards.remove_cards(removed_cards)
        return removed_cards

    def discard_card(self, card):
        self.hand_cards.remove(card)
        return card

    def add_card(self, card):
        self.hand_cards += [card]

    def add_cards(self, cards_to_add, deck_type: DeckType = DeckType.HAND_DECK):

        add_to = self.get_all_cards(deck_type)

        if hasattr(cards_to_add, '__iter__'):
            while None in cards_to_add:
                cards_to_add.remove(None)
            add_to += cards_to_add
        else:
            if cards_to_add is not None:
                add_to.append(cards_to_add)

    def give_a_card(self, reason, card_name):
        cards = self.get_cards(card_name)
        for card in cards:
            return card

    def get_valid_targets(self, card):
        return self.controller.get_valid_targets(self, card)

    def stealable(self):
        result = len(self.hand_cards) + len(self.judgement_cards) + len(self.equipment_cards) != 0
        # print(result)
        return result

    def has_some_card(self):
        return len(self.equipment_cards) + len(self.hand_cards) > 0

    def has_range_attack(self, target):
        return self.controller.attack_distance(self, target) <= 1

    def attack_distance_to(self, target):
        pass

    def set_cards_value(self, stage: Stage = Stage.PLAY_CARD):
        increment = 0
        for card in self.get_cards(CardName.SHA):
            if not (self.has_card(CardName.HUFU, deck_type=DeckType.HAND_DECK) or (self.hero.sha_limit >= 2) or
                    SkillName.TIANLANG in self.hero.skills):
                card.value = 7 + increment
                increment -= 2
            else:
                card.value = 7
        increment = 0
        for card in self.get_cards(CardName.SHAN):
            card.value = 8 + increment
            increment -= 3

        increment = 0
        for card in self.get_cards(CardName.WUXIEKEJI):
            card.value = 8 + increment
            increment -= 2

        if stage == Stage.PLAY_CARD:
            self.enemies.sort(key=lambda enemy: enemy.hero.hp)
            weakest_enemy = self.enemies[0]
            for card in self.get_cards(CardType.WEAPON):
                if not self.has_card(CardType.WEAPON, deck_type=DeckType.EQUIPMENT_DECK):
                    card.value = 6
                else:
                    card.value = 2
                if self.has_range_attack(weakest_enemy):
                    if card.name == CardName.HUFU:
                        card.value = len(self.get_cards(CardName.SHA)) * 6
                    elif card.name == CardName.XUANHUAFU:
                        card.value += self.hand_cards.cards_count / 2 - 1
                    else:
                        card.value += 0
                else:
                    card.value += 3

            enemy_skills = []
            for enemy in self.enemies:
                enemy_skills.extend(enemy.hero.skills)
            enemy_has_dh = SkillName.DIEHUN in enemy_skills or SkillName.YUEFA in enemy_skills
            for card in self.get_cards(CardType.GROUP_MAGIC):
                if enemy_has_dh:
                    card.value = 0
                else:
                    card.value = 7
            for card in self.get_cards([CardName.FANGYUMA, CardName.YURUYI, CardName.TANNANGQUWU,
                                        CardName.BINGLIANGCUNDUAN, CardName.QIANKUNDAI]):
                card.value = 8

            for card in self.get_cards([CardName.JUEDOU]):
                card.value = 7

            for card in self.get_cards(CardName.FUDICHOUXIN):
                card.value = 6

            for card in self.get_cards([CardName.HUADIWEILAO, CardName.WUZHONGSHENGYOU]):
                card.value = 9

            for card in self.get_cards([CardName.WUGUFENGDENG, CardName.JIEDAOSHAREN]):
                card.value = 5

        else:
            for card in self.get_cards(CardType.EQUIPMENT):
                card.value = 0
        for card in self.get_cards([CardName.JIU, CardName.YAO]):
            if self.hero.hp == 1:
                card.value += 5
        if self.has_skill([SkillName.ZHUDING, SkillName.SHENTAN]):
            for card in self.hand_cards:
                if card.suit == CardSuit.CLUB or card.suit == CardSuit.SPADE:
                    card.value += 3


    def __str__(self):
        return self.hero.name

    def __repr__(self):
        return self.hero.name

    def has_skill(self, skill_name):
        return self.hero.has_skill(skill_name)

    def get_skill(self, skill_name):
        return self.hero.get_skill(skill_name)

    def get_skill_names(self, skill_name):
        return self.hero.get_skill_names(skill_name)

    def is_alive(self):
        return self.hero.is_alive


class SkillAI:
    def __init__(self):
        pass

    @staticmethod
    def operate(skill, source: Player, to: Player):
        if hasattr(skill, '__iter__'):
            skill = skill[0]
        print(skill)
        match skill.name:
            case SkillName.JUJIAN:
                if source.hand_cards.cards_count == 0 or to.hand_cards.cards_count == 0:
                    print('>>>', source.hand_cards.cards_count, to.hand_cards.cards_count)
                    return
                else:
                    source.set_cards_value()
                    source.hand_cards.sort(key=lambda card: card.value)
                    bad_card = source.hand_cards[0]

                    if bad_card.value <= 7:
                        source.controller.discard_cards.add_cards(source.hands_in(bad_card))
                        got_card = source.controller.get_card(to)
                        to.hands_in(got_card)

                        source.add_cards(got_card)
                        print(f'举荐卡：{bad_card} 获得卡：{got_card}')

            case SkillName.WANGSHEN:
                if (source.hero.hp >= 3 and (source.has_card(
                        CardName.YAO) and source.hand_cards.cards_count >= 2)) and source.has_some_card():
                    source.set_cards_value()
                    source.hand_cards.sort(key=lambda card: card.value)
                    if source.hand_cards.cards_count > 0:
                        bad_card = source.hand_cards[0]
                    else:
                        bad_card = source.equipment_cards[0]

                    if bad_card.value <= 7:
                        print(f'{skill}: {bad_card}')
                        source.hands_in(bad_card)
                        source.controller.change_player_hp(-1, source, source)
                        source.controller.deal_cards(source, count=3)

            case SkillName.SHOUJIAN:
                if card := source.get_a_card(CardType.EQUIPMENT, deck_type=DeckType.PLAYER_OWN):
                    print(f'{skill} {card}')
                    source.controller.discard_cards.add_cards(source.hands_in(card))
                    source.controller.deal_cards(source, count=1, certain_cards=CardName.SHA)
                    source.hero.marks[Mark.SHOUJIAN] += 1
                    source.hero.sha_limit += 1

            case SkillName.FANJI:
                card_sha = source.get_cards(CardName.SHA)
                if len(card_sha) > 0:
                    for card in card_sha:
                        if card.suit == CardSuit.HEART or card.suit == CardSuit.DIAMOND:
                            return source.use_card(card, to, Flag.CANTREACT)
                    return source.use_card(card_sha[0], to)

            case SkillName.QINXIN:
                if to.hand_cards.cards_count >= 1:
                    random.shuffle(to.hand_cards)
                    card = to.hand_cards.show_cards(1)[0]
                    if card.suit is CardSuit.HEART or card.suit is CardSuit.DIAMOND:
                        source.add_cards(to.hands_in(card))
                    else:
                        to.controller.player_get_damage(count=1, victim=to, attacker=source, card=None)

            case SkillName.JIANLIE:
                if source.hand_cards.cards_count <= 1:
                    source.controller.deal_cards(source, count=1)

            case SkillName.QIUHUANG:
                source.controller.judge(source, SkillName.QIUHUANG, *Judge.get_pattern(SkillName.QIUHUANG))

            case SkillName.FAJIA:
                if to.get_all_cards(DeckType.PLAYER_OWN).cards_count > 0:
                    # print(f'{to} hand_cards {to.hand_cards}')
                    random.shuffle(to.hand_cards)
                    card = to.get_a_card(None)
                    to.hands_in(card)
                    source.add_cards(card)
                    print(f'{SkillName.FAJIA} 获得 {card}')

            case SkillName.SHISHENG:
                cards = source.controller.remain_cards.show_cards(4)
                print(cards)
                source.add_cards(cards)
                source.set_cards_value()
                source.hand_cards.remove_cards(cards)
                leave_card = None
                has_bigger_6 = False
                acquire_cards = []

                for card in cards:
                    if card.figure >= 7:
                        if card.suit not in [got_card.suit for got_card in acquire_cards]:
                            acquire_cards.append(card)
                        else:
                            has_bigger_6 = True
                            if leave_card is None:
                                leave_card = card
                                # has_bigger_6 = True
                                for got_card in acquire_cards:
                                    if leave_card.suit == got_card.suit:
                                        if leave_card.value > got_card.value:
                                            acquire_cards.remove(got_card)
                                            acquire_cards.append(leave_card)
                                            leave_card = got_card
                                            break

                    #             switch card
                    else:
                        if leave_card is None:
                            leave_card = card
                            if leave_card.suit in [got_card.suit for got_card in acquire_cards]:
                                pass
                            else:
                                pass
                        else:
                            if card.suit not in [got_card.suit for got_card in acquire_cards]:
                                if not has_bigger_6:
                                    if card.suit == leave_card.suit and card.value < leave_card.value:
                                        acquire_cards.append(leave_card)
                                        leave_card = card
                                        continue
                                acquire_cards.append(card)
                            else:
                                for got_card in acquire_cards:
                                    if got_card.suit == card.suit and leave_card.figure < 7:
                                        if not has_bigger_6 and got_card.figure < 7:
                                            if got_card.value < card.value:
                                                acquire_cards.remove(got_card)
                                                acquire_cards.append(card)

                print(acquire_cards)
                source.controller.deal_cards(player=source, certain_cards=acquire_cards)

            case SkillName.BEIMIN:
                source.controller.judge(source, SkillName.BEIMIN, *Judge.get_pattern(SkillName.BEIMIN))

            case SkillName.GONGXIN:
                if to.hand_cards.cards_count > 0:
                    random.shuffle(to.hand_cards)
                    showed_card = to.hand_cards.show_cards(count=1)
                    source.set_cards_value()
                    if cards := source.get_cards(lambda card: showed_card[0].suit == card.suit):
                        cards.sort()
                        source.controller.discard_cards.add_cards(source.hands_in(cards[0]))
                        damage = Damage(count=1, source=source, target=to, damage_type=DamageType.SKILL)
                        source.controller.player_get_damage(damage)
                        print(f'展示{showed_card}, 弃置{cards[0]}')

            case SkillName.ZHUDING:
                useful_cards = source.get_cards(lambda card: card.suit == CardSuit.SPADE or card.suit == CardSuit.CLUB)
                source.set_cards_value()
                if useful_cards:
                    source.controller.discard_some_cards(source.hands_in(useful_cards[0]))
                    source.controller.add_mark_to_player(source, Mark.ZHUDING)
                    print(f'{SkillName.ZHUDING} {useful_cards[0]}')

            case SkillName.ZHISHUI:
                if to.hand_cards.cards_count >= 4:
                    card = source.choose_player_a_card(target=to)
                    to.controller.discard_some_cards(to.hands_in(card))
                    print(f'{skill} {card}')

            case SkillName.RENDE:
                source.controller.deal_cards(player=source, count=1)

            case SkillName.SHESHEN:
                source.controller.deal_cards(player=source, count=2)

            case SkillName.JIASHA:
                card = source.choose_player_a_card(to)
                if card is not None:
                    to.controller.discard_some_cards(to.hands_in(card))
                source.controller.deal_cards(source, count=1)

            case SkillName.LIANCE:
                success_time = 0
                while (card := source.choose_player_a_card(to, DeckType.HAND_DECK)) and success_time < 3:
                    choice = random.choice(['红色', '黑色'])
                    card = card[0]
                    print(choice, card)
                    if choice == '红色':
                        if card.suit == CardSuit.HEART or card.suit == CardSuit.DIAMOND:
                            source.add_cards(to.hands_in(card))
                            success_time += 1
                        else:
                            last_card = source.controller.remain_cards.show_cards(reverse=True)
                            print(last_card)
                            last_card = last_card[0]
                            source.hand_cards.add_cards(last_card)
                            source.set_cards_value()
                            source.hand_cards.remove_cards(last_card)
                            if last_card.value >= 8:
                                source.controller.remain_cards.get_card(last_card)
                                source.controller.remain_cards.insert(0, last_card)
                            break

                    else:
                        if card.suit == CardSuit.SPADE or card.suit == CardSuit.CLUB:
                            source.add_cards(to.hands_in(card))
                            success_time += 1
                        else:
                            last_card = source.controller.remain_cards.show_cards(reverse=True)
                            print(last_card)
                            last_card = last_card[0]
                            source.hand_cards.add_cards(last_card)
                            source.set_cards_value()
                            source.hand_cards.remove_cards(last_card)
                            if last_card.value >= 8:
                                source.controller.remain_cards.get_card(last_card)
                                source.controller.remain_cards.insert(0, last_card)
                            break




