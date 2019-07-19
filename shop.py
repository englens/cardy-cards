
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

class CardListing:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

