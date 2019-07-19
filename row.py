from card import Card
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

    def get_card(self, index: int) -> Card:
        sqlstr = '''SELECT id FROM Card
                    WHERE Card.row_index=:r_index
                    AND Card.row_id=:rid;'''
        self.cursor.execute(sqlstr, {'r_index': index, 'rid': self.id})
        card_id = self.cursor.fetchone()[0]
        return Card(self.conn, card_id)

    def get_all_cards(self) -> list:
        """Return all cards in ascending order"""
        sqlstr = '''SELECT id FROM Card
                    WHERE Card.row_id=:rid
                    ORDER BY Card.row_index ASC;'''
        self.cursor.execute(sqlstr, {'rid': self.id})
        return [Card(self.conn, i[0]) for i in self.cursor.fetchall()]

    # Add card to row. Throws RowFullError if row full.
    # Also sets up parameters and defaults.
    def add_card(self, type_name: str) -> Card:
        curr_length = self.get_current_length()  # stored to save sql time
        if curr_length >= self.get_max_cards():
            raise RowFilledError()
        # Find card type id, and param type ids
        card_type_id = get_card_type_id(type_name, self.cursor)
        param_type_ids = get_param_types(card_type_id, self.cursor)
        # construct list of param insert data based on default values
        param_inserts = []
        for p_type in param_type_ids:
            param_inserts.append({'val':  get_param_type_default_value(p_type, self.cursor),
                                  'c_id': card_type_id,
                                  't_id': p_type})
        # sql strings
        card_sql = '''INSERT INTO Card (row_index, card_type_id, row_id)
                      VALUES (:r_index, :c_type, :rid);'''
        param_sql = '''INSERT INTO Param (value, card_id, type_id)
                       VALUES (:val, :c_id, :t_id);'''
        # insert new rows to database
        self.cursor.execute(card_sql, {'r_index': curr_length, 'c_type': card_type_id, 'rid': self.id})
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
        if alias is None:
            alias = str(self.get_index())
        no_dashes = ROW_WINDOW_WIDTH - len(alias) - 8

        render = '-'*(no_dashes//2) + 'Row ' + str(self.get_index()) + '-'*(no_dashes//2) + '\n'
        if alias is not None:
            render += '('+alias+')'
        render += '--------------------------\n'
        for i, card in enumerate(self.get_all_cards()):
            render += str(i) + ') ' + card.get_name() + '\n'
        render += '-'*no_dashes
        return '```' + render + '```'


class RowFilledError(Exception):
    """Raised when a card is inserted into a filled row"""
    pass


def get_card_type_id(card_name: str, cursor) -> int:
    sqlstr = '''SELECT id 
                FROM CardType
                WHERE name=:name;'''
    cursor.execute(sqlstr, {'name': card_name})
    return cursor.fetchone()[0]


def get_param_types(card_type_id: int, cursor) -> list:
    """Returns a list of ParamType PKs for given card type"""
    sqlstr = '''SELECT id
                FROM ParamType
                WHERE card_type=:cid;'''
    cursor.execute(sqlstr, {'cid': card_type_id})
    return [i[0] for i in cursor.fetchall()]


def get_param_type_default_value(param_id, cursor):
    sqlstr = '''SELECT value_default
                FROM ParamType
                WHERE id=:pid;'''
    cursor.execute(sqlstr, {'pid': param_id})
    return cursor.fetchone()[0]
