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
                    WHERE id=:sqlid;'''
        self.cursor.execute(sqlstr, {'sqlid': self.id})
        self.conn.commit()

    # THANK GOD FOR BLOBS
    def get_param(self, name):
        sqlstr = '''SELECT value
                    FROM Param
                        JOIN Card ON Card.id = Param.card_id
                        JOIN ParamType ON ParamType.id = Param.type_id
                    WHERE ParamType.name=:name
                    AND Card.id = :id;'''
        self.cursor.execute(sqlstr, {'name': name, 'id': self.id})
        return self.cursor.fetchone()

    def set_param(self, name, new_value):
        sqlstr = '''UPDATE Param
                    SET value=:newval
                    WHERE id IN 
                    (
                        SELECT id FROM Param
                            JOIN Card ON Card.id=Param.card_id
                            JOIN ParamType ON ParamType.id=Param.type_id
                        WHERE Card.id=:id
                        AND ParamType.name=:name
                    );'''
        self.cursor.execute(sqlstr, {'name': name, 'id': self.id, 'newval': new_value})

    def passive(self, **kwargs):
        pass

    def use(self):
        pass
