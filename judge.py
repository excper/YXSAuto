from Data import PlayerType, Stage
from cards import CardSuit, CardName, Card
from skill_names import SkillName


class Judge:
    @staticmethod
    def get_pattern(name):
        match name:
            case CardName.HUADIWEILAO:
                return (lambda card: card.suit is not CardSuit.HEART,
                        lambda controller, player, card: controller.remove_player_stage(player, Stage.PLAY_CARD))
            case CardName.BINGLIANGCUNDUAN:
                return (lambda card: card.suit is not CardSuit.CLUB,
                        lambda controller, player, card: controller.remove_player_stage(player, Stage.DRAW_CARD))
            case CardName.SHOUPENGLEI:
                return (lambda card: card.suit is CardSuit.SPADE and 2 <= card.figure <= 9,
                        lambda controller, player, card: controller.change_player_hp(-3, player, None, card))
            case SkillName.QIUHUANG:
                def fail_function(controller, player):
                    players = controller.get_players(player, player_type=PlayerType.OTHERS)
                    females = [p for p in players if p.hero.gender == 0]
                    if females:
                        controller.deal_cards(females[0], count=1)
                        player.add_cards(females[0].hands_in(females[0].get_a_card(None)))

                return (lambda card: card.figure < 7,
                        lambda controller, player, card: player.use_card(Card(name=CardName.YAO), target=player),
                        fail_function
                        )
            case SkillName.BEIMIN:
                return (lambda card: card.figure < 7,
                        lambda controller, player, card:
                        controller.deal_cards(player, count=2, certain_cards=lambda card: card.figure >= 7))
