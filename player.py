from row import Row
DEFAULT_MAX_ROWS = 1


class Player:
    def __init__(self, sql_connection, sql_id):
        self.conn = sql_connection
        self.cursor = self.conn.cursor()
        self.id = sql_id

    # ensure a data entry exists. otherwise throw SqlNotFoundError
    def validate(self):
        sqlstr = '''SELECT EXISTS(SELECT 1 FROM Player WHERE Player.id=:sql_id);'''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        return self.cursor.fetchone()

    def get_name(self):
        sqlstr = '''SELECT name FROM Player
                    WHERE Player.id=:sql_id;'''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        return self.cursor.fetchone()

    def get_max_rows(self):
        sqlstr = '''SELECT max_rows FROM Player
                            WHERE Player.id=:sql_id;'''
        self.cursor.execute(sqlstr, {'sql_id': self.id})

    # returns list of rows in the correct order
    def get_all_rows_ordered(self):
        sqlstr = '''SELECT (id, inventory_index) 
                    FROM Row
                        JOIN Player ON Player.id = Row.player_id
                    WHERE Player.id=:sql_id;'''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        results = self.cursor.fetchall()
        ordered_rows = [Row(self.conn, a[0]) for a in sorted(results, key=lambda tup: tup[1])]
        return ordered_rows

    def get_row(self, index: int):
        sqlstr = '''SELECT id FROM Row
                    WHERE Row.inventory_index=:i_index
                    AND Row.player_id=:p_id;'''
        self.cursor.execute(sqlstr, {'i_index': index, 'p_id': self.id})
        row_id = self.cursor.fetchone()[0]
        return Row(self.conn, row_id)


def create_new_player(sql_conn, discord_id: str, server_id: str, nickname: str):
    sqlstr = '''INSERT INTO Player (discord_id, server_id, name, max_rows)
                VALUES (:did, :s_id, :name, :max_rows);'''
    # TODO
