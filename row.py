from card import Card


class Row:
    """Area in player inventory in which cards can interact."""
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def validate(self):
        sqlstr = '''SELECT EXISTS(SELECT 1 FROM Row WHERE id = :id);'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_current_length(self):
        sqlstr = '''SELECT count(*) FROM Card
                        JOIN Row ON Row.id=Card.row_id
                    WHERE Row.id = :id;'''
        self.conn.execute(sqlstr, {'id': self.id})
        return self.conn.fetchone()

    def get_name(self):
        sqlstr = '''SELECT name FROM Row
                    WHERE id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()

    def get_max_cards(self):
        sqlstr = '''SELECT max_cards FROM Row
                    WHERE id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()

    def get_card(self, index: int) -> Card:
        sqlstr = '''SELECT id FROM Card
                    WHERE Card.row_index=:r_index
                    AND Card.row_id=:rid;'''
        self.cursor.execute(sqlstr, {'r_index': index, 'rid': self.id})
        card_id = self.cursor.fetchone()[0]
        return Card(self.conn, card_id)

    # Add card to row. Throws RowFullError if row full.
    # Also sets up parameters and defaults.
    def add_card(self, type_name: str):
        curr_length = self.get_current_length()  # stored to save sql time
        if curr_length >= self.get_max_cards():
            raise RowFilledError()
        # Find card type id, and param type ids
        card_type_id = get_card_type_id(type_name, self.cursor)
        param_type_ids = get_param_types(card_type_id, self.cursor)
        # construct list of param insert data based on default values
        param_inserts = []
        for p_type in param_type_ids:
            param_inserts.append({'val':  get_param_type_default(p_type, self.cursor),
                                  'c_id': card_type_id,
                                  't_id': p_type})
        # sql strings
        card_sql = '''INSERT INTO Card (row_index, card_type, row_id)
                      VALUES (:r_index, :c_type, :rid);'''
        param_sql = '''INSERT INTO Param (value, card_id, type_id)
                       VALUES (:val, :c_id, :t_id);'''
        # insert new rows to database
        self.cursor.execute(card_sql, {'r_index': curr_length, 'c_type': card_type_id, 'rid': self.id})
        self.cursor.executemany(param_sql, param_inserts)
        self.conn.commit()

    # Plan:
    # 1 - throw err if card not found
    # 2 - remove all param rows
    # 3 - remove card row
    def remove_card(self, index):
        self.get_card(index).destroy()
        sqlstr = '''UPDATE Param
                            SET value=:newval
                            WHERE id IN 
                            (
                                SELECT id FROM Param
                                    JOIN Card ON Card.id=Param.card_id
                                    JOIN ParamType ON ParamType.id=Param.type_id
                                WHERE Card.id=:id
                                AND ParamType.name=:name
                            );'''
        # TODO


class RowFilledError(Exception):
    """Raised when a card is inserted into a filled row"""
    pass


def get_card_type_id(card_name: str, cursor):
    sqlstr = '''SELECT (id) 
                FROM CardType
                WHERE name=:name;'''
    cursor.execute(sqlstr, {'name': card_name})
    return cursor.fetchone()


def get_param_types(card_type_id: int, cursor):
    """Returns a list of ParamType PKs for given card type"""
    sqlstr = '''SELECT (id)
                FROM ParamType
                WHERE card_type=:cid;'''
    cursor.execute(sqlstr, {'cid': card_type_id})
    return cursor.fetchall()


def get_param_type_default(param_id, cursor):
    sqlstr = '''SELECT (default)
                FROM ParamType
                WHERE id=:pid;'''
    cursor.execute(sqlstr, {'pid': param_id})
    return cursor.fetchall()
