from Data import Mark, Flag
from cards import CardName, Card, CardType, CardSuit
from deck import Deck, DeckType
from hero import Hero
from judge import Judge
from player import Player, PlayerType, Stage
from skill_names import SkillName
from damage import Damage, DamageType


class Controller:
    def __init__(self):
        self.discard_cards = Deck(DeckType.DISCARDED_DECK)
        self.remain_cards = Deck(DeckType.REMAINING_DECK)
        self.remain_cards.reset_use(self.discard_cards)

        self.player_count = 0
        self.players = []
        self.agents = []

        self.game_over = False
        self.game_started = False
        self.winner = None

        self.current_player = None

    def add_player(self, hero: Hero, team, position):
        player = Player(hero)
        player.team = team
        player.position = position
        player.controller = self
        self.players.append(player)
        self.set_player_state(player)
        return player

    def set_player_state(self, player):
        if player.has_skill(SkillName.DANQI):
            player.hero.range_to_others += 1
        elif player.has_skill(SkillName.SHICAI):
            player.hero.range_from_others += 1

    def deal_cards(self, player: Player, count=2, certain_cards=None):
        if certain_cards is None:
            # print('remain_card: ', self.remain_cards)
            got_cards = self.remain_cards.get_cards(count=count)
        else:
            got_cards = self.remain_cards.get_cards(count=count, pattern=certain_cards)
        player.add_cards(got_cards)
        print(f'{player.hero} 获得手牌 {got_cards}\n当前手牌 {player.hand_cards}')
        if self.game_started:
            if player.has_skill(SkillName.BINGXIAN):
                if len(got_cards) >= 2:
                    self.deal_cards(player, count=1)

    def start(self):
        self.set_enemies()
        for hero in self.players:
            if hero.position % 2 == 0:
                self.deal_cards(hero, count=3, certain_cards=[])
            else:
                self.deal_cards(hero,
                                count=4, certain_cards=[])
        self.game_started = True

    def set_enemies(self):
        for player in self.players:
            for another_player in self.players:
                if player is another_player:
                    continue
                else:
                    if player.team != another_player.team:
                        player.enemies.append(another_player)
                    else:
                        player.friends.append(another_player)

    def loop_round(self):
        for player in self.players:
            self.current_player = player
            player.stages = list(Stage)
            if player.hero.is_alive and self.game_over is False:
                for stage in player.stages:
                    self.process_stage(stage, player)

    @staticmethod
    def remove_player_stage(player: Player, stage: Stage):
        player.stages.remove(stage)

    def judge(self, player, card=None, success_pattern=None, success_function=None,
              fail_function=None):
        judge_card = self.remain_cards.get_card()
        print(f'{card}判定：{judge_card}')
        if success_pattern(judge_card):
            success_function(self, player, card)
        else:
            if fail_function:
                fail_function(self, player)
        self.discard_cards.add_cards(judge_card)

    def process_stage(self, stage, player: Player):
        match stage:
            case Stage.PREPARE:
                self.prepare_start(player)
                self.prepare_process(player)
                self.prepare_over(player)
            case Stage.TRIAL:
                self.trial_start(player)
                self.trial_process(player)
                self.trial_before_apply(player)
                self.trial_apply(player)
            case Stage.DRAW_CARD:
                self.draw_card_start(player)
                self.draw_card_process(player)
                self.draw_card_over(player)
            case Stage.PLAY_CARD:
                self.play_card_start(player)
                self.play_card_process(player)
                self.play_card_over(player)
            case Stage.DISCARD_CARD:
                self.discard_card_start(player)
                self.discard_card_process(player)
                self.discard_card_over(player)
            case Stage.OVER:
                self.over_start(player)
                self.over_process(player)
                self.over_over(player)

    def ask_players_to_use_card(self, asked_target: PlayerType, origin: Player, target: Player, attack_card: Card,
                                asked_card_name) -> bool:
        match asked_target:
            case PlayerType.ALL:
                asked_targets = self.players
            case PlayerType.TEAMMATE:
                asked_targets = origin.friends + [origin]
            case PlayerType.ENEMY:
                asked_targets = origin.enemies
            case PlayerType.TEAMMATE_NO_SELF:
                asked_targets = origin.friends
            case _:
                asked_targets = [asked_target]
        for player in asked_targets:
            if asked_card_name == CardName.WUXIEKEJI:
                for card in player.get_cards(CardName.WUXIEKEJI):
                    if origin.is_enemy(player) and target.is_friend(player):
                        # player.hit_card(card)
                        return player.use_card(card, origin)

            elif asked_card_name == CardName.YAO:
                for card in player.get_cards(CardName.YAO):
                    player.hit_card(card)
                    self.change_player_hp(1, origin, player, card)
                    return True
        return False

    @staticmethod
    def ask_player_to_hit_card(target, origin, asked_card, count, reason):
        if target.decide_hit_card(origin, asked_card, count, reason):
            for _ in range(count):
                target.hit_card(target.get_cards(asked_card))
            return True
        return False

    def player_use_card(self, player: Player, card: Card, target: Player = None, *args):
        if CardType.EQUIPMENT in card.type:
            self.player_equip(player, card)
        elif CardType.INSTANT_MAGIC in card.type:
            # if self.player_try_to_use_instant_magic(player, card, target):
            return self.player_use_instant_magic(player, card, target)
        elif CardType.DELAYED_MAGIC in card.type:
            self.player_use_delayed_magic(player, card, target)
        elif CardType.BASIC in card.type:
            # self.player_try_to_use_basic_card(player, card, target)
            self.player_use_basic_card(player, card, target, *args)
        else:
            print('some other card types')

    @staticmethod
    def player_equip(player: Player, card: Card):
        player.equip_card(card)
        # player.equipment_cards.add_cards(card)
        # if card.name == CardName.FANGYUMA:
        #     player.hero.range_from_others += 1
        # if card.name == CardName.JINGONGMA:
        #     player.hero.range_to_others += 1
        # if card.name == CardName.BOLANGCHUI or card.name == CardName.LUYEQIANG:
        #     player.hero.attack_range_to_others += 2
        # if card.name == CardName.LONGLINDAO:
        #     player.hero.attack_range_to_others += 1
        # player.discard_card(card)

    def player_unequip(self, player: Player, card: Card):
        player.equipment_cards.remove(card)
        match card.name:
            case CardName.FANGYUMA:
                player.hero.range_from_others -= 1
            case CardName.JINGONGMA:
                player.hero.range_to_others -= 1
            case CardName.BOLANGCHUI | CardName.LUYEQIANG:
                player.hero.attack_range_to_others -= 2
            case CardName.LONGLINDAO:
                player.hero.attack_range_to_others -= 1

        # self.discard_cards.add_card(card)

    def player_use_instant_magic(self, player: Player, card: Card, target):
        self.discard_cards.add_cards(player.hands_in(card))
        if player.has_skill(SkillName.MIAOJI) and self.current_player == player:
            self.deal_cards(player, count=1)
        if isinstance(target, Player):
            target = [target]

        for a_target in target:
            if self.player_use_instant_magic_set_a_target(player, card, a_target):
                if card.name == CardName.FUDICHOUXIN:
                    choose_card = self.ask_player_to_choose_a_card(player, a_target, DeckType.PLAYER_ALL)
                    print(f'{card}弃置: {choose_card}')
                    self.discard_cards.add_cards(a_target.hands_in(choose_card))
                elif card.name == CardName.TANNANGQUWU:
                    choose_card = self.ask_player_to_choose_a_card(player, a_target, DeckType.PLAYER_ALL)
                    print(f'{card}获得: {choose_card}')
                    player.hand_cards.add_cards(a_target.hands_in(choose_card))
                elif card.name == CardName.JUEDOU:
                    while True:
                        if not a_target.decide_hit_card(player, CardName.SHA, count=1, reason=card):
                            # self.change_player_hp(-1, a_target, source=player, card=card)

                            self.player_get_damage(
                                Damage(source=player, target=a_target, damage_type=DamageType.MAGIC, card=card)
                            )
                            break
                        else:
                            a_target.hit_card(a_target.get_a_card(CardName.SHA))

                        if not player.decide_hit_card(a_target, CardName.SHA, count=1, reason=card):
                            self.player_get_damage(
                                Damage(source=a_target, target=player, damage_type=DamageType.MAGIC, card=card)
                            )
                            break
                        else:
                            player.hit_card(player.get_a_card(CardName.SHA))
                elif card.name == CardName.WUZHONGSHENGYOU:
                    self.deal_cards(player, 2)

                elif card.name == CardName.FENGHUOLANGYAN:
                    if got := self.ask_player_for_card(a_target, CardName.FENGHUOLANGYAN, CardName.SHA):
                        a_target.hit_card(got)
                    else:
                        damage = Damage(target=a_target, source=player, damage_type=DamageType.MAGIC, card=card)
                        self.player_get_damage(damage)
                elif card.name == CardName.WANJIANQIFA:
                    if got := self.ask_player_for_card(a_target, CardName.FENGHUOLANGYAN, CardName.SHAN):
                        a_target.hit_card(got)
                    else:
                        damage = Damage(target=a_target, source=player, damage_type=DamageType.MAGIC, card=card)
                        self.player_get_damage(damage)
            else:
                return False
        return True

    @staticmethod
    def player_use_delayed_magic(player: Player, card: Card, target: Player):
        target.judgement_cards.add_cards(card)
        player.discard_card(card)
        # print(target in self.players)
        pass

    def player_use_basic_card(self, player: Player, card: Card, target: Player, *args):
        self.discard_cards.add_cards(player.hands_in(card))
        if card.name == CardName.SHA:
            # print('args', args)
            target = self.set_sha_target(player, card, target)
            if player.has_skill(SkillName.JIANDAO):
                self.add_mark_to_player(target, Mark.JIANDAO)
                if self.player_has_mark(target, Mark.JIANDAO) >= 4:
                    print(target.hero, 'Dead')
                    target.hero.is_alive = False
                    self.game_over = True
                    self.winner = player
            if Flag.CANTREACT not in args:
                got_card = self.ask_player_for_card(target, card, CardName.SHAN)
                if got_card:
                    target.hit_card(got_card, card)
                else:
                    damage = Damage(target=target, source=player, damage_type=DamageType.SHA, card=card)
                    self.player_get_damage(damage)
            else:
                self.player_get_damage(Damage(target=target, source=player, damage_type=DamageType.SHA, card=card))
        elif card.name == CardName.YAO:
            count = 1
            self.change_player_hp(count, player, player, card)
        elif card.name == CardName.JIU:
            if player.hero.hp <= 0:
                count = 1
                self.change_player_hp(count, player, target)
            else:
                self.add_mark_to_player(player, Mark.JIU)

    @staticmethod
    def ask_player_to_choose_a_card(player, target, deck_type=DeckType.HAND_DECK):
        return player.choose_player_a_card(target, deck_type)

    @staticmethod
    def ask_player_for_card(player, reason, card_name):
        return player.get_a_card(card_name)

    @staticmethod
    def get_card(target: Player):
        return target.get_random_cards(count=1)

    def response_by(self, target, card_name):
        target_card_names = [card.name for card in target.hand_cards]
        if card_name in target_card_names:
            index = target_card_names.index(card_name)
            self.discard_cards.append(target.hand_cards.pop(index))
            return True
        else:
            return False

    def ask_for_discard_cards(self, player, count):
        if count > 0:
            discard_cards = player.discard_cards(count, stage=Stage.DISCARD_CARD)
            self.discard_cards.add_cards(discard_cards)

    def recover_player(self, source, target, card):
        if target is None:
            target = source
        self.change_player_hp(value=1, target=target, source=source, card=None)
        source.discard_card(card)
        self.discard_cards += [card]

    def change_player_hp(self, value, target: Player, source: Player, card: Card = None):
        if value > 0 and target.hero.hp == target.hero.max_hp:
            print('Need not change')
            return
        target.hero.change_hp(value)
        print(f'{target} hp 改变: {value}, 来源 {source}, 卡 {card}, 当前 hp {target.hero.hp}')
        while target.hero.hp <= 0:
            if not (card_jiu := self.ask_player_for_card(target, None, CardName.JIU)):
                if not self.ask_players_to_use_card(PlayerType.TEAMMATE, target, target, None, CardName.YAO):
                    target.hero.is_alive = False
                    self.winner = source
                    self.game_over = True
                    break
            else:
                self.player_use_card(target, card_jiu, target)

    def get_valid_targets(self, source, card):
        if card.name == CardName.SHA:
            players = self.get_players(source, PlayerType.OTHERS)
            return [player for player in players if self.attack_distance(source, player) <= 1]
        elif card.name == CardName.FUDICHOUXIN:
            return [player for player in self.get_players(source, PlayerType.OTHERS) if player.stealable()]
        elif card.name == CardName.TANNANGQUWU:
            return [player for player in self.get_players(source, PlayerType.OTHERS) if player.stealable() and
                    self.distance(source, player) <= 1]
        elif card.name == CardName.BINGLIANGCUNDUAN:
            players = self.get_players(source, PlayerType.OTHERS)
            return [player for player in players if self.distance(source, player) <= 1]
        elif card.name == CardName.HUADIWEILAO:
            players = self.get_players(source, PlayerType.OTHERS)
            return players
        else:
            players = self.get_players(source, PlayerType.OTHERS)
            return players

    @staticmethod
    def attack_distance(source: Player, to: Player):
        source_player, to_player = source.hero, to.hero
        position_distance = abs(source.position - to.position)
        source_range = source_player.range_to_others + source_player.attack_range_to_others
        to_range = to_player.range_from_others + to_player.attack_range_from_others
        ret = to_range - source_range + position_distance
        # print(ret)
        return ret

    @staticmethod
    def distance(source: Player, to: Player):
        return to.hero.range_from_others - source.hero.range_to_others + abs(source.position - to.position)

    def get_players(self, source: Player, player_type: PlayerType):
        match player_type:
            case PlayerType.ALL:
                return self.players
            case PlayerType.ENEMY:
                return [player for player in self.players if player in source.enemies]
            case PlayerType.TEAMMATE:
                return [player for player in self.players if player in source.friends]
            case PlayerType.TEAMMATE_NO_SELF:
                return [player for player in self.players if player in source.friends and player is not source]
            case PlayerType.OTHERS:
                return [player for player in self.players if player is not source]
            case _:
                raise NotImplemented

    def get_cards_from_player(self, got_cards, player: Hero):
        if hasattr(got_cards, '__iter__'):
            self.discard_cards += got_cards
        else:
            self.discard_cards.append(got_cards)

    def player_hit_card(self, player, card, source_card):
        for p in self.players:
            if p is player:
                continue
            else:
                if p.has_skill(SkillName.WUSHENG):
                    if card.name == CardName.SHA:
                        print(p, '获得', card)
                        p.add_cards(card)
                        return
        self.discard_cards.add_cards(card)

    def play_card_start(self, player: Player):
        pass

    @staticmethod
    def prepare_start(player):

        pass

    def prepare_process(self, player):
        player.hero.sha_limit = 1 + self.player_has_mark(player, Mark.SHOUJIAN)
        if player.has_card(CardName.HUFU, deck_type=DeckType.EQUIPMENT_DECK):
            player.hero.sha_limit = 999
        if player.has_skill(SkillName.ZHUDING):
            for p in self.players:
                if p.is_friend(player) and p.controller.player_has_mark(p, Mark.ZHUDING) <= 3:
                    player.react_skill(SkillName.ZHUDING, p)
                    break
        if player.has_skill(SkillName.LIANCE):
            player.react_skill(SkillName.LIANCE, player.enemies[0])


    def prepare_over(self, player):
        pass

    def trial_start(self, player):
        pass

    def trial_process(self, player):
        player.judgement_cards.reverse()
        will_remove = []
        for card in player.judgement_cards:
            match card.name:
                case CardName.HUADIWEILAO:
                    if not self.ask_players_to_use_card(PlayerType.ALL, player.enemies[0], player, card,
                                                        CardName.WUXIEKEJI):
                        self.judge(player, card, *Judge.get_pattern(name=CardName.HUADIWEILAO))
                case CardName.BINGLIANGCUNDUAN:
                    self.judge(player, card, *Judge.get_pattern(name=CardName.BINGLIANGCUNDUAN))

            will_remove.append(card)
        for card in will_remove:
            if card in player.judgement_cards:
                player.judgement_cards.remove(card)
                self.discard_cards.add_cards(card)

    def trial_before_apply(self, player):
        pass

    def trial_apply(self, player):
        pass

    def draw_card_start(self, player):
        pass

    def draw_card_process(self, player):
        if player.has_skill(SkillName.BUDAO):
            self.deal_cards(player, count=3)
        elif player.has_skill(SkillName.SHISHENG):
            if 2 + self.player_has_mark(
                    player, Mark.ZHUDING) - self.player_has_mark(player, Mark.JIANMIE) >= 2:
                player.react_skill(SkillName.SHISHENG, player)
        elif player.has_skill(SkillName.TIANDU):
            self.deal_cards(player, count=4)
            player.set_cards_value()
            self.discard_cards.add_cards(player.discard_cards(count=1))
        else:
            self.deal_cards(player, count=2 + self.player_has_mark(
                player, Mark.ZHUDING) - self.player_has_mark(player, Mark.JIANMIE)
                            )
        pass

    def draw_card_over(self, player):
        pass

    def play_card_process(self, player):
        for p in self.players:
            if p.has_skill(SkillName.ZHISHUI):
                if p.is_enemy(player) and player.hand_cards.cards_count >= 4:
                    p.react_skill(SkillName.ZHISHUI, player)
                    break
        player.play_card()

    def play_card_over(self, player):
        pass

    def discard_card_start(self, player):
        pass

    def discard_card_process(self, player):
        self.ask_for_discard_cards(player, len(player.hand_cards) - player.hero.max_hand_cards_patch -
                                   player.hero.hp)

    def discard_card_over(self, player):
        pass

    def over_start(self, player):
        pass

    def over_process(self, player):
        pass

    def over_over(self, player: Player):
        for p in self.players:
            if p.has_skill(SkillName.JIANLIE):
                p.react_skill(SkillName.JIANLIE, p)
        if player.has_skill(SkillName.BEIMIN):
            player.react_skill(SkillName.BEIMIN, player)

    def player_try_to_use_basic_card(self, player, card, target):
        pass

    def player_try_to_use_instant_magic(self, player, card, target):
        """
        Ask all players use wuxiekeji
        :param player:
        :param card:
        :param target:
        :return: True indicates successful use, False indicates invalid
        """
        pass

    def player_use_instant_magic_set_a_target(self, player, card, a_target):
        if not self.ask_players_to_use_card(PlayerType.ALL, player, a_target, card, CardName.WUXIEKEJI):
            return True
        else:
            return False
        pass

    def set_sha_target(self, player, card, target):
        return target
        pass

    @staticmethod
    def add_mark_to_player(target, mark):
        target.hero.marks[mark] += 1
        pass

    def get_player_mark(self):
        pass

    @staticmethod
    def player_has_mark(target, mark: Mark):
        return target.hero.marks[mark]
        pass

    @staticmethod
    def remove_player_mark(player: Player, mark: Mark):
        player.hero.marks[mark] = 0

    def player_get_damage(self, damage: Damage):
        count = damage.count
        victim = damage.target
        attacker = damage.source
        card = damage.card
        if self.player_has_mark(victim, Mark.DIHUI):
            damage += 1
            self.remove_player_mark(victim, Mark.DIHUI)
        if self.player_has_mark(attacker, Mark.ZUIJIU):
            if CardName.SHA == card.name or CardName.JUEDOU == card.name:
                damage += 1
        self.change_player_hp(-count, victim, attacker, card)
        skills = victim.get_skill_names([SkillName.FANJI, SkillName.FAJIA, SkillName.RENDE, SkillName.SHESHEN, SkillName.FUCHOU, SkillName.YAOYI, SkillName.LUOYAN, SkillName.JIASHA])
        if len(skills) > 0 and victim.is_alive():
            if SkillName.FAJIA in skills:
                victim.react_skill(SkillName.FAJIA, attacker)
            if SkillName.SHESHEN in skills:
                victim.react_skill(SkillName.SHESHEN, victim)
            if SkillName.RENDE in skills:
                victim.react_skill(SkillName.RENDE, victim)
            if SkillName.FUCHOU in skills:
                victim.react_skill(SkillName.FUCHOU, attacker)
            if SkillName.JIASHA in skills:
                victim.react_skill(SkillName.JIASHA, attacker)
            if SkillName.LUOYAN in skills:
                victim.react_skill(SkillName.LUOYAN, attacker)
            if SkillName.FANJI in skills:
                if card.name == CardName.SHA or card.name == CardName.JUEDOU:
                    victim.react_skill(SkillName.FANJI, attacker)

        pass

    def discard_some_cards(self, cards):
        self.discard_cards.add_cards(cards)
