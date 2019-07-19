import card


class Shop:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def get_name(self):
        sqlstr = """SELECT name FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_greeting_quip(self):
        sqlstr = """SELECT greeting_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_exit_quip(self):
        sqlstr = """SELECT exit_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_examine_quip(self):
        sqlstr = """SELECT examine_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_cancel_quip(self):
        sqlstr = """SELECT cancel_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_buy_quip(self):
        sqlstr = """SELECT buy_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_card_listings(self):
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


class CardListing:
    """Card to be displayed in a shop. Represents the card type, and returns default values."""
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def get_shop_index(self):
        sqlstr = '''SELECT shop_index FROM CardListing
                            WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_price_type(self):
        sqlstr = '''SELECT price_type FROM CardListing
                    WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_price_value(self):
        sqlstr = '''SELECT price FROM CardListing
                    WHERE CardListing.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_stock(self):
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

    def get_fake_params(self):
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


class FakeParam:
    """Represents a Param of a card type, for displaying in shops."""
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
        """For non-number params, max is null"""
        sqlstr = '''SELECT max_default
                    FROM ParamType
                    WHERE ParamType.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]
