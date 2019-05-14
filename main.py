from abc import ABC


# contains multiple rows, stored in a dict for speed.
class Inventory:
    def __init__(self, rows={}):
        self.rows = rows
        
        
    def add_row(self, row):
        self.rows[row.id] = row
        
    def get_row(self, row_name):
        
        
class Row:
    def __init__(self, cards=[]):
        self.cards = cards
        self.size = size
        
    def get_card(self, index):
        return self.cards[index]
        
    def insert_card(self, card):
        if len(self) >= self.size:
            raise RowFilledError
            return
        self.cards.append(card)
        
    def expand(self):
        self.size += 1
        
    def to_dict()
    
class SqlHandler:
    def __init__(self, db_filename):
        self.conn = sqlite3.connect(db_filename)
        self.cursor = conn.cursor()
        
    def create_card(self, type, player):
        pass
    
    def create_player(self, name, discord_id):
        pass
    
    
    
class BaseCard:
    # should be able to recreate a card at any state
    def __init__(self, card_type):
        self.type = card_type
    
    # For when card has an "action"
    def use(self):
        pass
    
    # called as needed, use dt to update card state
    def passive(self, dt):
        pass
    
    # lossless
    def to_dict(self):
        pass
    
    # calls constructor, returns instance
    def from_sql(**kwargs):
        pass


# makes 1 resource over time.
# if instanciated, will make 10 money a hour up to 100.
class SimplePassiveGenerator(BaseCard):
    def __init__(self, resource='money', rate_per_hour=10, inventory_size=100, inventory_fill=0):
        self.resource = resource
        self.rate_per_hour = rate_per_hour
        self.inventory_size = inventory_size
        self.inventory_fill = inventory_fill
    
class RowFilledError(Exception):
    """Raised when a card is inserted into a filled row"""
    pass