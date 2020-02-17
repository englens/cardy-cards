from game_objects.card import render_card

"""
Module Description:
    Classes representing cards as listed in a shop.
"""


class ShopListing:
    """A Card as listed in a shop, not attached to a player.
        Mimics a card, but takes all values from card type defaults."""
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def get_card_type_name(self) -> str:
        sqlstr = '''SELECT CardType.name FROM CardType
                    JOIN ShopListing ON ShopListing.card_type_id=CardType.id
                    WHERE ShopListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_card_type_id(self) -> int:
        sqlstr = '''SELECT CardType.id FROM CardType
                    JOIN ShopListing ON ShopListing.card_type_id=CardType.id
                    WHERE ShopListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_card_render(self) -> str:
        sqlstr = '''SELECT CardType.art, CardType.name, CardType.rarity, CardType.description
                    FROM CardType
                    JOIN ShopListing ON ShopListing.card_type_id = CardType.id
                    WHERE ShopListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        data = self.cursor.fetchone()[0]
        return render_card(data[0], data[1], data[2], data[3], self.get_all_params())

    def get_all_params(self) -> list:
        sqlstr = '''SELECT * FROM ParamType
                    JOIN CardType ON ParamType.card_type = CardType.id
                    JOIN ShopListing ON ShopListing.card_type_id = CardType.id
                    WHERE ShopListing.id = :id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        params = [ParamListing(a[0], self.conn) for a in self.cursor.fetchall()]
        return params

    def get_price(self) -> int:
        sqlstr = '''SELECT price FROM ShopListing
                    WHERE ShopListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_price_name(self) -> str:
        sqlstr = '''SELECT price_type FROM ShopListing
                    WHERE ShopListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]


class ParamListing:
    """Similar to a CardListing, a virtual param for shop display. Thanks, duck typing!"""
    def __init__(self, sql_id: int, conn):
        self.id = sql_id
        self.conn = conn
        self.cursor = conn.cursor()

    def get_val(self):
        sqlstr = '''SELECT value_default
                    FROM ParamType
                    WHERE ParamType.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})

        # name fixed
    def get_name(self):
        sqlstr = '''SELECT name
                    FROM ParamType
                    WHERE ParamType.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

        # almost always same as default, but functionality is there to change it
    def get_max(self):
        """For non-number params, max is null"""
        sqlstr = '''SELECT max
                    FROM ParamType
                    WHERE ParamType.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def is_visible(self):
        sqlstr = '''SELECT visible_default
                    FROM ParamType
                    WHERE ParamType.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]
