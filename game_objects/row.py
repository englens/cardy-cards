from . import card
import cards
from utils import card_type_utils as ctu
from typing import List

ROW_WINDOW_WIDTH = 40
DEFAULT_MAX_CARDS = 8


class Row:
    """Area in player inventory in which cards can interact."""
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def __eq__(self, other):
        return self.id == other.id and type(self) == type(other)

    def validate(self) -> bool:
        sqlstr = '''SELECT EXISTS(SELECT 1 FROM Row WHERE id = :id);'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def delete(self):
        for card in self.get_all_cards():
            card.delete()
        sqlstr = '''DELETE FROM Row
                    WHERE Row.id = :id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        self.conn.commit()

    def get_current_length(self) -> int:
        sqlstr = '''SELECT count(*) FROM Card
                        JOIN Row ON Row.id=Card.row_id
                    WHERE Row.id = :id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_alias(self) -> str:
        sqlstr = '''SELECT alias FROM Row
                    WHERE id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_index(self) -> int:
        sqlstr = '''SELECT player_index FROM Row
                    WHERE id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_max_cards(self) -> int:
        # sqlstr = '''SELECT max_cards FROM Row
        #             WHERE id=:id;'''
        # self.cursor.execute(sqlstr, {'id': self.id})
        # return self.cursor.fetchone()[0]
        return DEFAULT_MAX_CARDS

    def get_card(self, index: int) -> card.Card:
        sqlstr = '''SELECT id FROM Card
                    WHERE Card.row_index=:r_index
                    AND Card.row_id=:rid;'''
        self.cursor.execute(sqlstr, {'r_index': index, 'rid': self.id})
        card_id: int = self.cursor.fetchone()[0]
        return cards.get_card(card_id, self.conn)

    def get_all_cards(self) -> List[card.Card]:
        """Return all cards in ascending order"""
        sqlstr = '''SELECT id FROM Card
                    WHERE Card.row_id=:rid
                    ORDER BY Card.row_index ASC;'''
        self.cursor.execute(sqlstr, {'rid': self.id})
        return [cards.get_card(i[0], self.conn) for i in self.cursor.fetchall()]

    def remaining_slots(self) -> int:
        """Returns number of open slots for cards"""
        return self.get_max_cards() - self.get_current_length()

    # Add card to row. Throws RowFullError if row full.
    # Also sets up parameters and defaults.
    def add_card(self, type_name: str) -> card.Card:
        # Find curr length of row, so we can insert after it
        curr_length = self.get_current_length()
        if curr_length >= self.get_max_cards():
            raise RowFilledError()
        # Card
        card_type_id = ctu.get_card_type_id_from_name(type_name, self.cursor)
        card_sql = '''INSERT INTO Card (row_index, card_type_id, row_id)
                              VALUES (:r_index, :c_type, :rid);'''
        self.cursor.execute(card_sql, {'r_index': curr_length, 'c_type': card_type_id, 'rid': self.id})
        # Params
        card_id = self.cursor.lastrowid
        param_type_ids = ctu.get_param_types(card_type_id, self.cursor)
        param_inserts = []
        for p_type in param_type_ids:
            defaults = ctu.get_param_type_defaults(p_type, self.cursor)
            param_inserts.append({'val':  defaults['val'],
                                  'visible': defaults['visible'],
                                  'max': defaults['max'],
                                  'max_val': defaults['max_val'],
                                  'c_id': card_id,
                                  't_id': p_type})
        # sql strings

        param_sql = '''INSERT INTO Param (value, visible, max, card_id, type_id)
                       VALUES (:val, :visible, :max_val :c_id, :t_id);'''
        # insert new rows to database

        card_id = self.cursor.lastrowid
        self.cursor.executemany(param_sql, param_inserts)
        self.conn.commit()
        return self.get_card(curr_length)

    # Plan:
    # 1 - throw err if card not found
    # 2 - remove all param rows
    # 3 - remove card row
    def remove_card(self, index):
        """Remove a card from the row, deleting it from the database."""
        self.get_card(index).delete()

    def render(self):
        alias = self.get_alias()
        # Done this way in case theres no alias
        if alias is None:
            a_len = 0
        else:
            a_len = len(alias)
        no_dashes = ROW_WINDOW_WIDTH - a_len - 8

        render = '-'*(no_dashes//2) + 'Row ' + str(self.get_index()) + '-'*(no_dashes//2) + '\n'
        if alias is not None:
            render += '('+alias+')'
        render += '--------------------------\n'
        for i, card in enumerate(self.get_all_cards()):
            render += f'{i}) {card.get_name()}\n'
        render += '-'*no_dashes
        return '```' + render + '```'


class RowFilledError(Exception):
    """Raised when a card is inserted into a filled row"""
    pass
