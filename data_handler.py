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


@dataclass
class PlayerSnapshot:
    """Shows simple player information"""
    sql_id: int
    name: str
    discord_id: str
    max_rows: int
