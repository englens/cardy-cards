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
    
class BaseCard:
    def __init__(self, card_type):
        self.type = card_type
        
    def use(self):
        pass
        
    def passive(self, dt):
        pass
    
    def 
    
class RowFilledError(Exception):
    """Raised when a card is inserted into a filled row"""
    pass