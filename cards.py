import importlib
from typing import List
from game_objects.card import Card
from utils import card_type_utils
from sqlite3 import Connection

"""
Module Description:
    Acts a single source for finding card sub-classes. Imports all card classes on startup for optimisation.
    Usage: run import_cards on program startup. Then, use get_card when creating card objects.
"""

card_classes = {}


# Imports a list of card type class names from the Cards folder.
def import_cards(c_types: List[str]):
    global card_classes
    for c_type in c_types:
        try:
            mod = importlib.import_module('card_classes.'+c_type)
            card_classes[c_type] = getattr(mod, c_type)
            print(f'Card Module {c_type} imported.')
        except Exception as e:
            print(f'Card Module {c_type} not imported correctly.')
            raise e


def get_card(card_id: int, sql_conn: Connection) -> Card:
    global card_classes
    print(card_classes)
    class_name = card_type_utils.get_card_type_class_from_card_id(card_id, sql_conn.cursor())
    return card_classes[class_name](sql_conn, card_id)
