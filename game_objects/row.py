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

    def has_room(self) -> bool:
        return self.remaining_slots() > 0

    def delete(self):
        for card in self.get_all_cards(0):
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

    def get_card(self, index: int, t):

        sqlstr = '''SELECT id FROM Card
                    WHERE Card.row_index=:r_index
                    AND Card.row_id=:rid;'''
        self.cursor.execute(sqlstr, {'r_index': index, 'rid': self.id})
        try:
            card_id: int = self.cursor.fetchone()[0]
            return cards.get_card(card_id, self.conn, t)
        except TypeError:
            return None

    def get_all_cards(self, t) -> List[card.Card]:
        """Return all cards in ascending order"""
        sqlstr = '''SELECT id FROM Card
                    WHERE Card.row_id=:rid
                    ORDER BY Card.row_index ASC;'''
        self.cursor.execute(sqlstr, {'rid': self.id})
        return [cards.get_card(i[0], self.conn, t) for i in self.cursor.fetchall()]

    def remaining_slots(self) -> int:
        """Returns number of open slots for cards"""
        return self.get_max_cards() - self.get_current_length()

    # Add card to row. Throws RowFullError if row full.
    # Also sets up parameters and defaults.
    def add_card(self, type_name: str, t=None):
        """Create new card and add it to row. Throws RowFullError if row full.
           Optionally Supply t to update the card and return it"""
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
                                  'max_val': defaults['max_val'],
                                  'c_id': card_id,
                                  't_id': p_type})
        # sql strings

        param_sql = '''INSERT INTO Param (value, visible, max, card_id, param_type_id)
                       VALUES (:val, :visible, :max_val, :c_id, :t_id);'''
        # insert new rows to database

        card_id = self.cursor.lastrowid
        self.cursor.executemany(param_sql, param_inserts)
        self.conn.commit()
        if t is not None:
            return cards.get_card(card_id, self.conn, t)

    # Plan:
    # 1 - throw err if card not found
    # 2 - remove all param rows
    # 3 - remove card row
    def remove_card(self, index):
        """Remove a card from the row, deleting it from the database."""
        self.get_card(index, 0).delete()

    def render(self, t) -> str:
        from utils import render_utils
        minimum_internal_width = 50
        """Returns a string representation of Row
                 Lines:
                    |------------------------------|  divline, # dashes equal to the max width -2
                    |       | Row N/Alias |        |  name_line, middle section centered
                    |---+--------------------------|  divline,
                    | 1 | card 1 summary           |  card_lines, left justified
                    | n | card n summary           |
                    |---+--------------------------|  divline
                """
        # setup row label -- alias if it exists, or row index otherwise
        alias = self.get_alias()
        if alias is None:
            label = f'Row {self.get_index()}'
        else:
            label = alias
        # First pass -- internal lines
        name_line_internal = f'  | {label} |  '
        divline_internal = '---+'
        card_lines_internal = []
        for i, c in enumerate(self.get_all_cards(t)):
            card_lines_internal.append(f' {i+1} | {c.one_line_summary()}   ')
        # Find length of longest line for spacing
        max_internal_len = max([len(c) for c in card_lines_internal])
        max_internal_len = max(len(name_line_internal),
                               minimum_internal_width,
                               max_internal_len)
        # Second pass -- full lines with proper spacing
        topline = '|' + '-'*max_internal_len + '|'
        divline = '|' + render_utils.space_text(divline_internal, 'right', max_internal_len, '-') + '|'
        nameline = '|' + render_utils.space_text(name_line_internal, 'both', max_internal_len) + '|'
        cardlines = []
        for l in card_lines_internal:
            cardlines.append('|' + render_utils.space_text(l, 'right', max_internal_len) + '|')
        # Put it all together
        output = topline + '\n' + nameline + '\n' + divline + '\n'
        for l in cardlines:
            output += l + '\n'
        output += divline
        return '```' + output + '```'


class RowFilledError(Exception):
    """Raised when a card is inserted into a filled row"""
    pass
