import card
import math
SHOP_WINDOW_WIDTH = 40


class Shop:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def get_length(self) -> int:
        sqlstr = """SELECT COUNT(*) FROM CardListing
                        JOIN Shop ON CardListing.shop_id=Shop.id
                    WHERE Shop.id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_name(self) -> str:
        sqlstr = """SELECT name FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_greeting_quip(self) -> str:
        sqlstr = """SELECT greeting_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_exit_quip(self) -> str:
        sqlstr = """SELECT exit_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_examine_quip(self) -> str:
        sqlstr = """SELECT examine_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_cancel_quip(self) -> str:
        sqlstr = """SELECT cancel_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_buy_quip(self) -> str:
        sqlstr = """SELECT buy_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_card_listings(self) -> list:
        sqlstr = '''SELECT CardListing.id FROM CardListing
                    WHERE CardListing.shop_id=:id
                    ORDER BY CardListing.shop_index ASC;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return [CardListing(self.conn, i[0]) for i in self.cursor.fetchall()]

    def get_card_listing(self, index):
        sqlstr = '''SELECT CardListing.id FROM CardListing
                    WHERE CardListing.shop_id=:id
                        AND CardListing.shop_index=:index;'''
        self.cursor.execute(sqlstr, {'id': self.id, 'index': index})
        try:
            return CardListing(self.conn, self.cursor.fetchone()[0])
        except TypeError:  # Indexing NoneType -- aka card not found
            raise IndexError('Card Not found at index ' + str(index))

    def render(self) -> str:
        title = 'Shop: ' + self.get_name()
        left_dashes = '-'*math.floor(SHOP_WINDOW_WIDTH-len(title)/2)
        right_dashes = '-'*math.ceil(SHOP_WINDOW_WIDTH-len(title)/2)
        render_str = left_dashes + title + right_dashes + '\n'
        for card_listing in self.get_card_listings():
            render_str += card_listing.get_shop_listing_text() + '\n'
        render_str += '-'*SHOP_WINDOW_WIDTH
        return render_str


class CardListing:
    """Card to be displayed in a shop. Represents the card type, and returns default values."""
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def get_shop_index(self) -> int:
        sqlstr = '''SELECT shop_index FROM CardListing
                            WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_price_type(self) -> str:
        sqlstr = '''SELECT price_type FROM CardListing
                    WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_price_value(self) -> int:
        sqlstr = '''SELECT price FROM CardListing
                    WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_stock(self) -> int:
        sqlstr = '''SELECT stock FROM CardListing
                    WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def set_stock(self, new_val):
        sqlstr = '''UPDATE CardListing
                    SET stock=:new_val
                    WHERE id=:id;'''
        self.cursor.execute(sqlstr, {'new_val': new_val, 'id': self.id})
        self.conn.commit()

    def get_fake_params(self) -> list:
        sqlstr = '''SELECT ParamType.id FROM ParamType
                        JOIN CardType ON ParamType.card_type=CardType.id
                        JOIN CardListing ON CardListing.card_type=CardType.id
                    WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return [FakeParam(i[0], self.conn) for i in self.cursor.fetchall()]

    def get_name(self) -> str:
        sqlstr = '''SELECT name 
                    FROM CardType
                        JOIN CardListing ON CardType.id = CardListing.id
                    WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_art(self) -> str:
        sqlstr = '''SELECT art 
                    FROM CardType
                        JOIN CardListing ON CardType.id = CardListing.id
                    WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_rarity(self) -> str:
        sqlstr = '''SELECT rarity 
                    FROM CardType
                        JOIN CardListing ON CardType.id = CardListing.id
                    WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_description(self) -> str:
        sqlstr = '''SELECT description
                    FROM CardType
                        JOIN CardListing ON CardType.id = CardListing.id
                    WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def render(self):
        return card.render_card(self.get_art(), self.get_name(),
                                self.get_rarity(), self.get_description(), self.get_fake_params())

    def get_shop_listing_text(self) -> str:
        """Returns the row of the shop representing this card. Example:
           1) MoneyButton                  100 money"""
        render_str_left = str(self.get_shop_index()) + ') ' + self.get_name()
        render_str_right = str(self.get_price_value()) + ' ' + str(self.get_price_value())
        spaces = ' '*(SHOP_WINDOW_WIDTH - (len(render_str_left) + len(render_str_right)))
        return render_str_left + spaces + render_str_right


class FakeParam:
    """Represents a Param of a card type, for displaying in shops.
       Not Stored in SQL -- gets info from Types."""
    def __init__(self, param_type_id: int, conn):
        self.id = param_type_id
        self.conn = conn
        self.cursor = conn.cursor()

    def __eq__(self, other):
        return self.id == other.id and type(self) == type(other)

    def get_val(self):
        sqlstr = '''SELECT value_default
                    FROM ParamType
                    WHERE ParamType.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    # name fixed
    def get_name(self):
        sqlstr = '''SELECT name
                    FROM ParamType
                        JOIN Param ON Param.type_id=ParamType.id
                    WHERE ParamType.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    # almost always same as default, but functionality is there to change it
    def is_visible(self):
        sqlstr = '''SELECT visible_default
                    FROM ParamType
                    WHERE ParamType.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    # almost always same as default, but functionality is there to change it
    def get_max(self):
        """For non-number params, max is null."""
        sqlstr = '''SELECT max_default
                    FROM ParamType
                    WHERE ParamType.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]


def get_player_shops(plr, conn):
    """Returns list of shops a player can access."""
    cursor = conn.cursor()
    sqlstr = """SELECT Shop.id FROM Shop
                    JOIN ShopUnlocked ON ShopUnlocked.shop_id=Shop.id
                WHERE ShopUnlocked.player_id=:id
                ORDER BY Shop.name ASC;"""
    cursor.execute(sqlstr, {'id': plr.id})
    return [Shop(i[0], conn) for i in cursor.fetchall()]
