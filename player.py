from row import Row
DEFAULT_NO_ROWS = 1


class Player:
    """Object oriented representation of a player."""
    def __init__(self, sql_connection, sql_id):
        self.conn = sql_connection
        self.cursor = self.conn.cursor()
        self.id = sql_id

    def validate(self):
        """Ensures a data entry exists. otherwise throw SqlNotFoundError"""
        sqlstr = '''SELECT EXISTS
                    (
                        SELECT 1 FROM Player 
                        WHERE Player.id=:sql_id
                    );
                 '''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        return self.cursor.fetchone()

    def get_name(self):
        """Returns the player's in-game name."""
        sqlstr = '''SELECT name FROM Player
                    WHERE Player.id=:sql_id;
                 '''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        return self.cursor.fetchone()

    def get_discord_id(self):
        """Returns the unique discord id."""
        sqlstr = '''SELECT discord_id FROM Player
                    WHERE Player.id=:sql_id;
                 '''
        self.cursor.execute(sqlstr, {'sql_id': self.id})

    def get_next_row_index(self):
        """Return next row index to use when adding a new row"""
        sqlstr = '''SELECT MAX(player_index)
                    FROM Row
                    WHERE Row.player_id=:id;
                 '''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone() + 1

    def get_all_rows_ordered(self):
        """returns list of rows in the correct order"""
        sqlstr = '''SELECT (id, inventory_index) 
                    FROM Row
                        JOIN Player ON Player.id = Row.player_id
                    WHERE Player.id=:sql_id;
                 '''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        results = self.cursor.fetchall()
        ordered_rows = [Row(self.conn, a[0]) for a in sorted(results, key=lambda tup: tup[1])]
        return ordered_rows

    def get_row(self, index: int):
        sqlstr = '''SELECT id FROM Row
                    WHERE Row.inventory_index=:i_index
                    AND Row.player_id=:p_id;
                 '''
        self.cursor.execute(sqlstr, {'i_index': index, 'p_id': self.id})
        row_id = self.cursor.fetchone()[0]
        return Row(self.conn, row_id)

    def add_row(self):
        index = self.get_next_row_index()
        sqlstr = '''INSERT INTO Row (name, inventory_index, alias, player_id)
                        VALUES (:name, :i_index, :alias, :p_id);
                     '''
        vals = {'name': self.get_name(),
                'i_index': index,
                'alias': None,
                'p_id': self.get_discord_id()}
        self.cursor.execute(sqlstr, vals)
        self.conn.commit()
        return self.get_row(index)


def register_new_player(sql_conn, discord_id: int, nickname: str):
    """Adds a new player, giving them 1 row and 1 default card."""
    sqlstr = '''INSERT INTO Player (discord_id, name)
                VALUES (:did, :name);
             '''
    vals = {'did': discord_id,
            'name': nickname}
    sql_conn.execute(sqlstr, vals)
    sql_conn.commit()
    return get_player(sql_conn, discord_id)


def get_player(sql_conn, discord_id: int):
    """Creates a player class based off of discord id."""
    sqlstr = '''SELECT id FROM Player
                WHERE Player.discord_id = :did;
             '''
    sql_conn.execute(sqlstr, {'did': discord_id})
    return Player(sql_conn, sql_conn.fetchone()[0])
