from game_objects import card


class Bank(card.Card):
    def use(self, message) -> str:
        raise NotImplementedError
    
    def passive(self, message, t) -> str:
        raise NotImplementedError
