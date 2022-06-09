import collections.abc
import enum
import random
from typing import Callable

import cards
from cards import CardName, Card


class DeckType(enum.Enum):
    REMAINING_DECK = '摸牌堆'
    DISCARDED_DECK = '弃牌堆'
    HAND_DECK = '手牌区'
    JUDGEMENT_DECK = '判定区'
    EQUIPMENT_DECK = '装备区'
    PLAYER_OWN = '拥有区'
    PLAYER_ALL = '全部区'


class Deck(collections.abc.MutableSequence):
    def __init__(self, deck_type: DeckType = DeckType.HAND_DECK):
        super(Deck, self).__init__()
        self.deck_type = deck_type
        self._cards = []
        self._reset_source = None
        if deck_type is DeckType.REMAINING_DECK:
            self._cards = cards.get_all_cards()

    def __setitem__(self, i: int, card) -> None:
        self._cards[i] = card

    def __delitem__(self, index):
        del self._cards[index]

    def __len__(self):
        return len(self._cards)

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, value):
        self._cards = value

    @property
    def cards_count(self):
        return len(self.cards)

    def insert(self, index: int, card) -> None:
        self._cards.insert(index, card)

    def __add__(self, other):
        if isinstance(other, Deck):
            cards = self.cards + other.cards
            deck = Deck()
            deck._cards = cards
            return deck
        else:
            raise NotImplemented

    def show_cards(self, count=1, reverse=False):
        remaining_cards_count = len(self)
        if remaining_cards_count == 0:
            if self.deck_type == DeckType.REMAINING_DECK:
                self._reset()
        if reverse:
            self.cards.reverse()
            result = self.cards[:count]
            self.cards.reverse()
            return result
        else:
            if count > remaining_cards_count:
                remaining_cards = self.cards.copy()
                if self.deck_type == DeckType.REMAINING_DECK:
                    self._reset()
                    self.cards = remaining_cards + self.cards
            result = self.cards[:count]
            return result

    def get_card(self, pattern=None, reverse=False):
        if len(self.cards) <= 0:
            # print('empty!')
            self._reset()
            # print(self.cards)
        if pattern:
            if isinstance(pattern, cards.CardName):
                for card in self.cards:
                    if card.name == pattern:
                        self.cards.remove(card)
                        return card
                print(f'No such cards {pattern}')
            elif isinstance(pattern, Card):
                self.cards.remove(pattern)
                return pattern
            else:
                for card in self.cards:
                    if pattern(card):
                        self.cards.remove(card)
                        return card
        else:
            return self.cards.pop(0)

    def get_cards(self, count=1, pattern=None, reverse=False):
        result = []
        # pattern = [CardName.SHA, CardName.SHAN, ...]
        if hasattr(pattern, '__iter__'):
            for card_name in pattern:
                got_card = self.get_card(pattern=card_name, reverse=reverse)
                if got_card is None:
                    pass
                else:
                    result.append(got_card)
            if count > len(result):
                for _ in range(count - len(result)):
                    result.append(self.get_card(pattern=None))
            return result
        else:
            for _ in range(count - len(result)):
                result.append(self.get_card(pattern=pattern))
            return result

    def random_pick_cards(self, count=1, pattern=None):
        # ret = self.cards[random.randint(0, len(self._cards) - 1)]
        # return ret
        if pattern:
            matched_cards = []
            for card in self.cards:
                if pattern(card):
                    matched_cards.append(card)
            if matched_cards:
                matched_count = len(matched_cards)
                if matched_count > count:
                    for _ in range(matched_count - count):
                        matched_cards.remove(random.choice(matched_cards))
                return matched_cards
        else:
            return random.choices(self.cards, k=count)

    def copy(self):
        return self.cards.copy()

    def _reset(self):
        # print('reset!')
        if self._reset_source is not None:
            # print(self._reset_source)
            self.cards = self._reset_source.copy()
            self._reset_source.clear()

            random.shuffle(self.cards)

    def sort(self, key=None, reverse=False):
        self.cards.sort(key=key, reverse=reverse)

    def add_card(self, card):
        self.cards.append(card)
        if self.deck_type == DeckType.DISCARDED_DECK:
            # print(self.cards)
            pass

    def add_cards(self, added_cards):
        if hasattr(added_cards, '__iter__'):
            for card in added_cards:
                if card is not None:
                    self.add_card(card)
        else:
            if added_cards is not None:
                self.add_card(added_cards)

    def reset_use(self, source: DeckType.DISCARDED_DECK):
        if type(source) is Deck:
            self._reset_source = source

    def remove_card(self, card: Card):
        if card in self.cards:
            self.cards.remove(card)
        else:
            print(f'Does not have card {card}')
        return card

    def remove_cards(self, pattern):
        # self.get_cards(count=self.cards_count, pattern=pattern)
        if hasattr(pattern, '__iter__'):
            for card in pattern:
                self.remove_card(card)
        elif isinstance(pattern, Card):
            self.remove_card(pattern)
        elif isinstance(pattern, Callable):
            matched_cards = []
            for card in self.cards:
                if pattern(card):
                    matched_cards.append(card)
            for card in matched_cards:
                self.cards.remove(card)

    def __str__(self):
        return self.cards.__str__()

    def __repr__(self):
        return self.cards.__repr__()

    def __next__(self):
        return self.cards.__next__()

    def __getitem__(self, item):
        return self.cards.__getitem__(item)


if __name__ == '__main__':
    deck = Deck(DeckType.REMAINING_DECK)
    discard = Deck(DeckType.DISCARDED_DECK)
    deck.reset_use(discard)
    discard.add_cards(deck.get_cards(30))
    print(deck)
    # print(deck.show_cards(count=6, reverse=False))
    deck.remove_cards(lambda card: card.name == CardName.SHA)
    print(deck)
    print(discard)
    print(deck)
    # print(deck._items)
