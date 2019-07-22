from row import Row, RowFilledError

DEFAULT_NO_ROWS = 1
PLAYER_WINDOW_WIDTH = 40


class Player:
    """Object oriented representation of a player."""
    def __init__(self, sql_connection, sql_id):
        self.conn = sql_connection
        self.cursor = self.conn.cursor()
        self.id = sql_id
        # State Param: list of information to fully describe the state.
        # Dependant on state
        self.state_param = [0]

    def __eq__(self, other):
        return self.id == other.id and type(self) == type(other)

    def validate(self) -> bool:
        """Ensures a data entry exists. otherwise throw SqlNotFoundError"""
        sqlstr = '''SELECT EXISTS
                    (
                        SELECT 1 FROM Player 
                        WHERE Player.id=:sql_id
                    );
                 '''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        return self.cursor.fetchone()[0]

    def get_name(self) -> str:
        """Returns the player's in-game name."""
        sqlstr = '''SELECT name FROM Player
                    WHERE Player.id=:sql_id;
                 '''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        return self.cursor.fetchone()[0]

    def add_card(self, type_name) -> bool:
        """Adds card to the first available row, and returns True if successful."""
        row_index = 0
        max_index = self.get_next_row_index() - 1
        while True:
            try:
                self.get_row(0).add_card(type_name)
                return True
            except RowFilledError:
                if row_index == max_index:
                    raise RowFilledError('Players inventory filled.')
                row_index += 1

    def get_discord_id(self) -> int:
        """Returns the unique discord id."""
        sqlstr = '''SELECT discord_id FROM Player
                    WHERE Player.id=:sql_id;
                 '''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        return self.cursor.fetchone()[0]

    def get_next_row_index(self) -> int:
        """Return next row index to use when adding a new row"""
        sqlstr = '''SELECT MAX(player_index)
                    FROM Row
                    WHERE Row.player_id=:id;
                 '''
        self.cursor.execute(sqlstr, {'id': self.id})
        response = self.cursor.fetchone()
        if response[0] is None:
            return 0

        return response[0] + 1

    def get_all_rows_ordered(self) -> list:
        """returns list of rows in the correct order"""
        sqlstr = '''SELECT Row.id, Row.player_index
                    FROM Row
                        JOIN Player ON Player.id = Row.player_id
                    WHERE Player.id=:sql_id
                    ORDER BY Row.player_index;
                 '''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        results = self.cursor.fetchall()
        rows = [Row(self.conn, a[0]) for a in results]
        return rows

    def get_row(self, index: int) -> Row:
        sqlstr = '''SELECT id FROM Row
                    WHERE Row.player_index=:p_index
                    AND Row.player_id=:p_id;
                 '''
        self.cursor.execute(sqlstr, {'p_index': index, 'p_id': self.id})
        row_id = self.cursor.fetchone()[0]
        return Row(self.conn, row_id)

    def add_row(self, alias=None) -> Row:
        index = self.get_next_row_index()
        sqlstr = '''INSERT INTO Row (alias, player_index, player_id)
                        VALUES (:alias, :player_index, :player_id);
                 '''
        vals = {'alias': alias,
                'player_index': index,
                'player_id': self.id}
        self.cursor.execute(sqlstr, vals)
        self.conn.commit()
        return self.get_row(index)

    def render(self) -> str:
        name = self.get_name()
        no_dashes = PLAYER_WINDOW_WIDTH - len(name) - 8
        render = '-' * (no_dashes // 2) + ' ' + name + ' ' + '-' * (no_dashes // 2) + '\n'
        for i, row in enumerate(self.get_all_rows_ordered()):

            render += str(i) + ' | '
            for card in row.get_all_cards():
                render += card.get_name() + ' | '
            render = render[:-2]  # remove the last comma
            render += '\n'
        render += '-' * (no_dashes + 4)
        return '```' + render + '```'

    def delete(self):
        for row in self.get_all_rows_ordered():
            row.delete()
        sqlstr = '''DELETE FROM Player
                    WHERE Player.id=:id'''
        self.cursor.execute(sqlstr, {'id':self.id})
        self.conn.commit()


def register_new_player(sql_conn, discord_id: int, nickname: str) -> Player:
    """Adds a new player, giving them 1 row and 1 default card."""
    sqlstr = '''INSERT INTO Player (discord_id, name)
                VALUES (:did, :name);
             '''
    print(f'Adding New Player: Name: {nickname}, ID: {discord_id}')
    vals = {'did': discord_id,
            'name': nickname}
    sql_conn.execute(sqlstr, vals)
    sql_conn.commit()
    return get_player(sql_conn, discord_id)


def get_player(sql_conn, discord_id: int):
    """Creates a player class based off of discord id."""
    curr = sql_conn.cursor()
    sqlstr = '''SELECT id FROM Player
                WHERE Player.discord_id = :did;
             '''
    curr.execute(sqlstr, {'did': discord_id})
    try:
        return Player(sql_conn, curr.fetchone()[0])
    except TypeError:
        return None
