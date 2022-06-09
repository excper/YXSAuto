import controller
from hero import HeroFactory

player_a = '诸葛亮'
player_b = '周瑜'
count = 100

result = []
for i in range(count):
    game = controller.Controller()

    player1 = game.add_player(HeroFactory.get_hero(player_a), 0, 0)
    player2 = game.add_player(HeroFactory.get_hero(player_b), 1, 1)

    # print(player1)
    game.start()
    while not game.game_over:
        game.loop_round()
    result.append(game.winner.hero.name)

result2 = []
for i in range(count):
    game = controller.Controller()

    player1 = game.add_player(HeroFactory.get_hero(player_b), 0, 0)
    player2 = game.add_player(HeroFactory.get_hero(player_a), 1, 1)

    # print(player1)
    game.start()
    while not game.game_over:
        game.loop_round()
    result2.append(game.winner.hero.name)

dct = {}
for re in result:
    if re in dct:
        dct[re] += 1
    else:
        dct[re] = 1

dct2 = {}
for re in result2:
    if re in dct2:
        dct2[re] += 1
    else:
        dct2[re] = 1

dct3 = {}
for re in result + result2:
    if re in dct3:
        dct3[re] += 1
    else:
        dct3[re] = 1


print(dct)
print(dct2)
print(dct3)