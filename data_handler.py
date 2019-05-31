import sqlite3
DEFAULT_NO_ROWS = 1
DEFAULT_NO_CARDS = 6

# NEW IDEA: Each class holds no state. instead, they continually poll the db
# then, we can treat player classes like normal players !


class Player:
    def __init__(self, sql_connection, discord_id):
        self.conn = sql_connection
        self.cursor = self.conn.cursor()
        self.d_id = discord_id

    # ensure a data entry exists. otherwise throw SqlNotFoundError
    def validate(self):
        sqlstr = '''SELECT EXISTS(SELECT 1 FROM Player WHERE discord_id = :did);'''
        self.cursor.execute(sqlstr, {'did': self.d_id})
        return self.cursor.fetchone()

    def get_name(self):
        sqlstr = '''SELECT name FROM Player
                    WHERE discord_id=:did;'''
        self.cursor.execute(sqlstr, {'did': self.d_id})
        return self.cursor.fetchone()

    def get_max_rows(self):
        sqlstr = '''SELECT max_rows FROM Player
                            WHERE discord_id=:did;'''
        self.cursor.execute(sqlstr, {'did': self.d_id})

    # returns list of rows in the correct order
    def get_row_id_list(self):
        sqlstr = '''SELECT (id, player_inventory_index) 
                    FROM Row
                        JOIN Player ON Player.id = Row.player_id
                    WHERE Player.discord_id = :did;'''
        self.cursor.execute(sqlstr, {'did': self.d_id})
        results = self.cursor.fetchall()
        ordered_ids = [a[0] for a in sorted(results, key=lambda tup: tup[1])]
        return ordered_ids


class Row:
    """Area in player inventory in which cards can interact."""
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def get_current_length(self):
        sqlstr = '''SELECT count(*) FROM Card
                        JOIN Row ON Row.id=Card.row_id
                    WHERE Row.id = :id;'''
        self.conn.execute(sqlstr, {'id': self.id})
        return self.conn.fetchone()

    def validate(self):
        sqlstr = '''SELECT EXISTS(SELECT 1 FROM Row WHERE id = :id);'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()

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

    # Add card to row. Throws RowFullError if row full.
    # Also sets up parameters and defaults.
    def add_card(self, type_name):
        if self.get_current_length() >= self.get_max_cards():
            raise RowFilledError()
        # Find card type id, and param type ids
        card_type_id = get_card_type_id(self.cursor, type_name)
        param_type_ids = get_param_types(card_type_id, self.cursor)
        # construct list of param insert data based on default values
        param_inserts = []
        for p_type in param_type_ids:
            param_inserts.append({'val':  get_param_type_default(p_type, self.cursor),
                                  'c_id': card_type_id,
                                  't_id': p_type})
        # sql strings
        card_sql = '''INSERT INTO Card (card_type, row_id)
                      VALUES (:c_type, :rid);'''
        param_sql = '''INSERT INTO Param (value, card_id, type_id)
                       VALUES (:val, :c_id, :t_id);'''
        # insert new rows to database
        self.cursor.execute(card_sql, {'c_type': card_type_id, 'rid': self.id})
        self.cursor.executemany(param_sql, param_inserts)
        self.conn.commit()

    # Plan:
    # 1 - throw err if card not found
    # 2 - remove all param rows
    # 3 - remove card row
    def remove_card(self):
        pass  # TODO


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


def create_card_from_type_id(type_id, row_id):
    pass  # TODO, might keep to Row


# Subclass me! Does nothing on its own.
# These methods should handle all the sql; subclasses can just use them
# Card classes should be used whenever cards are being worked with.
# Ca
class Card:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def get_name(self):
        sqlstr = '''SELECT name 
                    FROM CardType
                        JOIN Card ON Card.card_type=CardType.id
                    WHERE id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()

    # THANK GOD FOR BLOBS
    def get_param(self, name):
        sqlstr = '''SELECT value
                    FROM Param
                        JOIN Card ON Card.id = Param.card_id
                        JOIN ParamType ON ParamType.id = Param.type_id
                    WHERE ParamType.name=:name
                    AND Card.id = :id;'''
        self.cursor.execute(sqlstr, {'name': name, 'id': self.id})
        return self.cursor.fetchone()

    def set_param(self, name, new_value):
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
        self.cursor.execute(sqlstr, {'name': name, 'id': self.id, 'newval': new_value})

    def passive(self, dt):
        pass

    def use(self):
        pass


# example, TODO
class SimplePassiveGenerator(Card):
    """Example card functionality class that generates 1 money per hour.
       Holds 50 money."""
    def use(self):
        pass

    def passive(self, dt):
        pass
