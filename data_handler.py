import sqlite3
from dataclasses import dataclass
DEFAULT_NO_ROWS = 1
DEFAULT_NO_CARDS = 6


class SqlHandler:
    def __init__(self, db_filename: str):
        self.conn = sqlite3.connect(db_filename)
        self.cursor = self.conn.cursor()

    def create_player(self, name: str, discord_id: str):
        sqlstring = '''INSERT INTO Player (discord_id, name, max_rows)
                       VALUES (:did, :name, :rows);'''

        self.cursor.execute(sqlstring, {'did': discord_id, 'name': name, 'rows': DEFAULT_NO_ROWS})

    def create_player_snapshot(self, discord_id: str):
        sqlstr = '''SELECT * FROM Player
                 WHERE discord_id = :did;'''
        self.cursor.execute(sqlstr, {'did': discord_id})
        data = self.cursor.fetchone()  # id, did, name, max_rows
        return PlayerSnapshot(data[0], data[2], data[1], data[3])

    def create_card(self, card_type: str, player_discord_id: str, row_index: int, params):
        card_sqlstr = '''INSERT INTO Card (card_type, location_id, param1, param2, param3, param4, param5) VALUES
                    (:ctype, :loc_id, :p1, :p2, :p3, :p4, :p5);'''
        self.cursor.exectute('''SELECT param1_default, param2_default, param3_default, param4_default, param5_default 
                                FROM CardType WHERE CardType.name = :name''', {'name': card_type})
        defaults = self.cursor.fetchone()
        self.cursor.execute(card_sqlstr)

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
                    WHERE Player.discord_id = :did'''
        self.cursor.execute(sqlstr, {'did': self.d_id})
        results = self.cursor.fetchall()
        ordered_ids = [a[0] for a in sorted(results, key=lambda tup: tup[1])]
        return ordered_ids


class Row:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def get_current_length(self):
        sqlstr = '''SELECT count(*) FROM Card
                        JOIN Row ON Row.id=Card.row_id
                    WHERE Row.id = :id'''
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
                    WHERE id=:id'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()

    # Add card to row. Throws RowFullError if row full.
    # Also sets up parameters and defaults.
    def add_card(self, type_name):
        if self.get_current_length() >= self.get_max_cards():
            raise RowFilledError()
        sqlstr = '''INSERT INTO Card (card_type, row_id)
                    VALUES''' # TODO

    def remove_card(self):
        pass # TODO


class RowFilledError(Exception):
    """Raised when a card is inserted into a filled row"""
    pass


# Subclass me! Does nothing on its own.
# These methods should handle all the sql; subclasses can just use them
class Card:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def get_name(self):
        sqlstr = '''SELECT name 
                    FROM CardType
                        JOIN Card ON Card.card_type=CardType.id
                    WHERE id=:id'''
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
    def use(self):
        pass

    def passive(self, dt):
        pass