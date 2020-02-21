from . import row
from . import shop
from . import card
from sqlite3 import DatabaseError

DEFAULT_NO_ROWS = 1
PLAYER_WINDOW_WIDTH = 40


class Player:
    """Object oriented representation of a player."""
    def __init__(self, sql_connection, sql_id):
        self.conn = sql_connection
        self.cursor = self.conn.cursor()
        self.id = sql_id

    def __eq__(self, other):
        return self.id == other.id and type(self) == type(other)

    def get_name(self) -> str:
        """Returns the player's in-game name."""
        sqlstr = '''SELECT name FROM Player
                    WHERE Player.id=:sql_id;
                 '''
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        return self.cursor.fetchone()[0]

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
        ordered_rows = [row.Row(self.conn, a[0]) for a in sorted(results, key=lambda tup: tup[1])]
        return ordered_rows

    def get_row(self, index: int):
        sqlstr = '''SELECT id FROM Row
                    WHERE Row.player_index=:p_index
                    AND Row.player_id=:p_id;
                 '''
        self.cursor.execute(sqlstr, {'p_index': index, 'p_id': self.id})
        try:
            row_id = self.cursor.fetchone()[0]
        except TypeError:
            return None
        return row.Row(self.conn, row_id)

    def add_row(self, alias=None) -> row.Row:
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

    def get_unlocked_shops(self):
        sqlstr = '''SELECT shop_id from ShopUnlocked
                    WHERE player_id=:p_id
                    ORDER BY shop_id;'''
        self.cursor.execute(sqlstr, {'p_id': self.id})
        return[shop.Shop(self.conn, a[0]) for a in self.cursor.fetchall()]

    def render(self, t) -> str:
        name = self.get_name()
        no_dashes = PLAYER_WINDOW_WIDTH - len(name) - 8
        render = '-' * (no_dashes // 2) + ' ' + name + ' ' + '-' * (no_dashes // 2) + '\n'
        for i, r in enumerate(self.get_all_rows_ordered()):
            render += str(i) + ' | '
            for c in r.get_all_cards(t):
                render += c.get_name() + ' , '
            render = render[:-2]  # remove the last comma
            render += '\n'
        render += '-' * (no_dashes + 5)
        return '```' + render + '```'

    def delete(self):
        for r in self.get_all_rows_ordered():
            r.delete()
        sqlstr = '''DELETE FROM Player
                    WHERE Player.id=:id'''
        self.cursor.execute(sqlstr, {'id': self.id})
        self.conn.commit()

    def get_shop_menu_render(self):
        return shop.render_shop_menu(self)

    def get_cards_holding_resource(self, resource: str):
        matches = []
        for r in self.get_all_rows_ordered():
            for c in r.get_all_cards():
                if c.has_param(resource):
                    matches.append((c, c.get_param(resource).get_val()))
        # sort cards from most to least filled, so bank-like cards are used first
        # TODO: option to draw from smallest first
        matches.sort(key=lambda tup: tup[1], reverse=True)
        return matches

    def try_pay(self, resource_name: str, cost: int):
        """Loops through cards containing given resource, attempting to pay cost.
        If successful, returns a list of cards updated and their new values.
        Otherwise, returns None
        """
        valid_cards = self.get_cards_holding_resource(resource_name)
        if valid_cards is None:
            return None
        total_left = cost
        cards_used = []
        for c, amt in valid_cards:
            cards_used.append(c)
            if total_left <= amt:
                c.get_param(resource_name).set_val(amt-total_left)
                break
            else:
                total_left -= amt
                c.get_param(resource_name).set_val(0)
        else:
            # Never break, so not enough to pay
            return None
        return cards_used

    def get_cards_in_vault(self) -> dict:
        """Returns a dict of names of cards in vault, and count for each."""
        sqlstr = '''SELECT CardType.name, CardVault.amount FROM CardType
                    JOIN CardVault ON CardVault.card_type_id=CardType.id
                    WHERE CardVault.player_id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        hits = {}
        for a in self.cursor.fetchall():
            if a[0] in hits:
                hits[a[0]] += 1
            else:
                hits[a[0]] = 1
        return hits

    def get_card_type_amount_in_vault(self, card_type_id):
        sqlstr = '''SELECT amount 
                    FROM Row
                    WHERE card_type_id = :c_id
                    AND player_id = :p_id;'''
        self.cursor.execute(sqlstr, {'c_id': card_type_id, 'p_id': self.id})
        data = self.cursor.fetchone()
        if len(data) == 0:
            return 0
        return data[0]

    def move_card_from_vault_to_row(self, row_index: int, card_type_id: int) -> str:
        """Checks card vault for instance of card_type, and decrements it if exists.
            If this works, adds a new Card instance to row specified.
            :return - One of vault_empty, no_space, success, describing the result of the action"""
        session_row = self.get_row(row_index)
        if self.get_card_type_amount_in_vault(card_type_id) <= 0:
            return 'vault_empty'
        if not session_row.has_room():
            return 'no_space'
        return 'success'

    def add_card_to_vault(self, card_type_id: int):
        """Searches the database either adding a new entry for that card type or incrementing the amount column"""
        old_amount = self.get_card_type_amount_in_vault(card_type_id)
        if old_amount == 0:
            sqlstr = '''INSERT INTO CardVault (card_type_id, player_id, amount)
                        VAULES (:c_id, :p_id, :amt);'''

        else:
            sqlstr = '''UPDATE CardVault
                        SET amount = :amt
                        WHERE card_type_id = :c_id
                        AND player_id = :p_id;'''
        self.cursor.execute(sqlstr, {'c_id': card_type_id, 'p_id': self.id, 'amt': old_amount+1})
        self.conn.commit()

    def delete_card_from_vault(self, session_card: card.Card):
        """Completely deletes card from vault, such that the player must re-earn it (buy, etc) to get it back."""
        sqlstr = """DELETE FROM CardVault
                    WHERE card_type_id=:t_id
                    AND player_id=:p_id
                    LIMIT 1;"""
        self.cursor.execute(sqlstr, {'t_id': session_card.get_card_type_id(), 'p_id': self.id})
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


def get_player(sql_conn, discord_id: int) -> Player:
    """Creates a player class based off of discord id."""
    curr = sql_conn.cursor()
    sqlstr = '''SELECT id FROM Player
                WHERE Player.discord_id = :did;
             '''
    curr.execute(sqlstr, {'did': discord_id})
    try:
        return Player(sql_conn, curr.fetchone()[0])
    except TypeError:
        raise DatabaseError()
