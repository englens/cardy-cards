# Subclass me! Does nothing on its own.
# These methods should handle all the sql; subclasses can just use them
# Card classes should be used whenever cards are being worked with.


class Card:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def validate(self):
        sqlstr = '''SELECT EXISTS(SELECT 1 FROM Card WHERE id = :id);'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_name(self):
        sqlstr = '''SELECT name 
                    FROM CardType
                        JOIN Card ON Card.card_type=CardType.id
                    WHERE id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()

    def destroy(self):
        sqlstr = '''DELETE FROM Card
                    WHERE id=:sql_id;'''
        # TODO: Set this to drop cascade the params
        self.cursor.execute(sqlstr, {'sql_id': self.id})
        self.conn.commit()

    # THANK GOD FOR BLOBS
    def get_param(self, name):
        sqlstr = '''SELECT Param.id
                    FROM Param
                        JOIN Card ON Card.id = Param.card_id
                        JOIN ParamType ON ParamType.id = Param.type_id
                    WHERE ParamType.name=:name
                    AND Card.id = :id;'''
        self.cursor.execute(sqlstr, {'name': name, 'id': self.id})
        return Param(self.cursor.fetchone(), self.conn)

    # Can be also done from the param class, but this is faster if we don't need any info about it
    def set_param(self, name, new_value):
        sqlstr = """UPDATE Param
                    SET value=:newval
                    WHERE id IN 
                    (
                        SELECT id FROM Param
                            JOIN Card ON Card.id=Param.card_id
                            JOIN ParamType ON ParamType.id=Param.type_id
                        WHERE Card.id=:id
                        AND ParamType.name=:name
                    );"""
        self.cursor.execute(sqlstr, {'name': name, 'id': self.id, 'newval': new_value})
        self.conn.commit()

    def passive(self, *args, **kwargs):
        pass

    def use(self, *args, **kwargs):
        pass


class Param:
    """Represents one card parameter. Can access parameter:
            Name
            Value (any type)
            Max Value
        Can also change the card value, but cards can also do this themselves to take advantage
        of sql speed.
    """
    def __init__(self, sql_id: int, conn):
        self.id = sql_id
        self.conn = conn
        self.cursor = conn.cursor()

    def get_val(self):
        sqlstr = '''SELECT value
                    FROM Param
                    WHERE Param.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def set_val(self, new_value):
        sqlstr = '''UPDATE Param
                    SET value=:newval
                    WHERE Param.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id, 'newval': new_value})
        self.conn.commit()

    # name fixed
    def get_name(self):
        sqlstr = '''SELECT name
                    FROM ParamType
                        JOIN Param ON Param.type_id=ParamType.id
                    WHERE Param.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    # almost always same as default, but functionality is there to change it
    def is_visible(self):
        sqlstr = '''SELECT visible
                    FROM Param
                    WHERE Param.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    # almost always same as default, but functionality is there to change it
    def get_max(self):
        """For non-number params, max is null"""
        sqlstr = '''SELECT max
                    FROM Param
                    WHERE Param.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]
