# Subclass me! Does nothing on its own.
# These methods should handle all the sql; subclasses can just use them
# Card classes should be used whenever cards are being worked with.

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


class Card:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def validate(self) -> bool:
        sqlstr = '''SELECT EXISTS(SELECT 1 FROM Card WHERE id = :id);'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_name(self) -> str:
        sqlstr = '''SELECT name 
                    FROM CardType
                        JOIN Card ON Card.card_type=CardType.id
                    WHERE Card.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_art(self) -> str:
        sqlstr = '''SELECT art 
                    FROM CardType
                        JOIN Card ON Card.card_type=CardType.id
                    WHERE Card.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_rarity(self) -> str:
        sqlstr = '''SELECT rarity 
                    FROM CardType
                        JOIN Card ON Card.card_type=CardType.id
                    WHERE Card.id=:id;
                 '''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_description(self) -> str:
        sqlstr = '''SELECT description
                    FROM CardType
                        JOIN Card on Card.card_type=CardType.id
                    WHERE Card.id=:id
                 '''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def destroy(self):
        sqlstr = '''DELETE FROM Card
                    WHERE Card.id=:id;
                 '''
        # This isn't "telling the other guy", but its faster this way
        self.cursor.execute(sqlstr, {'id': self.id})
        sqlstr = '''DELETE FROM Param
                    WHERE Param.card_id=:id;
                 '''
        self.cursor.execute(sqlstr, {'id': self.id})
        self.conn.commit()

    # THANK GOD FOR BLOBS
    def get_param(self, name) -> Param:
        sqlstr = '''SELECT Param.id
                    FROM Param
                        JOIN Card ON Card.id = Param.card_id
                        JOIN ParamType ON ParamType.id = Param.type_id
                    WHERE ParamType.name=:name
                    AND Card.id = :id;'''
        self.cursor.execute(sqlstr, {'name': name, 'id': self.id})
        return Param(self.cursor.fetchone()[0], self.conn)

    def get_all_params(self) -> list:
        sqlstr = '''SELECT Param.id
                    FROM Param
                    WHERE Param.card_id = :id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return [Param(a[0], self.conn) for a in self.cursor.fetchall()]

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

    def render(self) -> str:
        """Returns a string representing the ascii image of this card."""
        art_lines = self.get_art().split('\n')
        name = self.get_name()
        rarity = self.get_rarity()
        desc = self.get_description().split('\n')
        top_art_line = art_lines[0]
        mid_art_lines = art_lines[1:-1]
        bot_art_line = art_lines[-1]
        # Header
        render = '+' + '-'*38 + '+\n'
        render += r'| {}{}{} |'.format(name,
                                       ' '*(36-(len(name) + len(rarity))),
                                       rarity) + '\n'
        render += '|' + ' '*38 + ' \n'
        # Art
        render += '|  /' + '-'*32 + r'\  |' + '\n'
        render += '| /' + top_art_line + r'\ |' + '\n'
        for line in mid_art_lines:
            render += '| |' + line + '| |\n'
        render += '| \\' + bot_art_line + '/ |\n'
        render += '|  \\' + '-'*32 + '/  |' + '\n'
        # Description
        desc_h_space = 38
        description_lines = []
        for line in desc:
            line_split = [line[i:i+desc_h_space] for i in range(0, len(line), desc_h_space)]
            description_lines += line_split
        for line in description_lines:
            if len(line) < desc_h_space:
                render += '|' + line + ' '*(desc_h_space-len(line)) + '|\n'
            else:
                render += '|' + line + '|\n'
        render += '|' + ' '*38 + ' \n'
        # Footer
        for param in self.get_all_params():
            if param.is_visible():
                val = param.get_val()
                if type(val) in [int, float]:
                    paramtext = param.get_name() + ': ' + val + '/' + param.get_max()
                else:
                    paramtext = val
                render += '|' + ' '*(37-len(paramtext)) + paramtext + ' |'
        render = '+' + '-'*38 + '+\n'
        return render
