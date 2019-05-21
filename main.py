from data_handler import SqlHandler, PlayerSnapshot


class Row:
    def __init__(self, max_size, cards=[]):
        self.cards = cards
        self.size = max_size
        
    def get_card(self, index):
        return self.cards[index]
        
    def insert_card(self, card):
        if len(self) >= self.size:
            raise RowFilledError
        self.cards.append(card)
        
    def expand(self):
        self.size += 1

    def __len__(self):
        return len(self.cards)








class PlayerHandler(SqlHandler):
    def create_player(self, name, discord_id):
        sqlstring = 'INSERT INTO Player VALUES'


class BaseCard:
    # For when card has an "action"
    def use(self):
        pass
    
    # called as needed, use dt to update card state
    def passive(self, dt):
        pass

    # calls constructor, returns instance
    @staticmethod
    def from_sql(**kwargs):
        pass


# makes 1 resource over time.
# will make 10 money a hour up to 100 -- subclass to change
class SimplePassiveGenerator(BaseCard):
    def __init__(self, resource='money', rate_per_hour=10, inventory_size=100, inventory_fill=0):
        self.resource = resource
        self.rate_per_hour = rate_per_hour
        self.inventory_size = inventory_size
        self.inventory_fill = inventory_fill
        super().__init__()


class RowFilledError(Exception):
    """Raised when a card is inserted into a filled row"""
    pass
