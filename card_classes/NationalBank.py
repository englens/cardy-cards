import card

class NationalBank(Card):
    def use(self, message) -> str:
        raise NotImplementedError
    
    def passive(self, message, t) -> str:
        raise NotImplementedError
