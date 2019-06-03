import sqlite3
from card import Card
DEFAULT_NO_ROWS = 1
DEFAULT_NO_CARDS = 6


# example, TODO
class SimplePassiveGenerator(Card):
    """Example card functionality class that generates 1 money per hour.
       Holds 50 money."""
    def use(self):
        pass

    def passive(self, dt):
        pass
