from game_objects import card


class ButtonBooster(card.Card):
    def use(self, message) -> str:
        raise NotImplementedError
    
    def passive(self, message, t, last_t) -> str:
        raise NotImplementedError
