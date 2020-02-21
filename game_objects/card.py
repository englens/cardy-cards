from typing import List


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

    def __eq__(self, other):
        return self.id == other.id and type(self) == type(other)

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


# Subclass me! Does nothing on its own.
# These methods should handle all the sql; subclasses can just use them
# Card classes should be used whenever cards are being worked with.
# BIG NOTE: IF YOU STORE A CARD, UPDATE IT BEFORE USE. UPDATE IS ONLY CALLED ON GET CARD
class Card:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def __eq__(self, other):
        return self.id == other.id and type(self) == type(other)

    # --- INTERFACE --- #
    def passive(self, t: int, last_t: int):
        """Called every time the card is used or displayed. Returns a string along
           the lines of 'Made 5 money since last checked'"""
        return ''

    # Called when
    def use(self, message):
        """Does something when activated with !use."""
        return ''

    def one_line_summary(self):
        """A summary of the card when displayed in the row. By default, shows the value and name of each param.
           May be overwritten if a different summary is more useful"""

        """MoneyButton -- money:5"""
        p_lines = []
        for p in self.get_all_params():
            if p.is_visible():
                p_lines.append(p.get_name() + ':' + p.get_val())
        return self.get_name() + ' -- ' + ', '.join(p_lines)
    # ------------------ #

    def update(self, t: int):
        """Runs passive, but only if t new.
        This fixes unnecessary double updates when cards depend on the values of others.
        """
        last_t = self.get_last_t()
        if t != last_t:
            self.set_last_t(t)
            return self.passive(t, last_t)
        return None

    # ---- Last_t interface ----
    def get_last_t(self) -> int:
        """Returns timestamp of last use."""
        sqlstr = '''SELECT last_t
                    FROM Card
                    WHERE id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        try:
            return self.cursor.fetchone()[0]
        except IndexError:
            return 0

    def set_last_t(self, new_t: int):
        sqlstr = '''UPDATE Card
                    SET last_t=:newval
                    WHERE Card.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id, 'newval': new_t})
        self.conn.commit()

    # ---- Basic Getters ----
    def get_name(self) -> str:
        sqlstr = '''SELECT name 
                    FROM CardType
                        JOIN Card ON Card.card_type_id=CardType.id
                    WHERE Card.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_class_name(self) -> str:
        sqlstr = '''SELECT class_name
                    FROM CardType
                        JOIN Card ON Card.card_type_id=CardType.id
                    WHERE Card.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_art(self) -> str:
        sqlstr = '''SELECT art 
                    FROM CardType
                        JOIN Card ON Card.card_type_id=CardType.id
                    WHERE Card.id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_rarity(self) -> str:
        sqlstr = '''SELECT rarity 
                    FROM CardType
                        JOIN Card ON Card.card_type_id=CardType.id
                    WHERE Card.id=:id;
                 '''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_description(self) -> str:
        sqlstr = '''SELECT description
                    FROM CardType
                        JOIN Card on Card.card_type_id=CardType.id
                    WHERE Card.id=:id;
                 '''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def delete(self):
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

    # ---- Param Handling ----
    # THANK GOD FOR BLOBS
    def get_param(self, param_name) -> Param:
        # Only compute passives right before grabbing them
        sqlstr = '''SELECT Param.id 
                    FROM Param
                        JOIN Card ON Card.id = Param.card_id
                        JOIN ParamType ON ParamType.id = Param.type_id
                    WHERE ParamType.name=:name
                    AND Card.id = :id;'''
        self.cursor.execute(sqlstr, {'name': param_name, 'id': self.id})
        return Param(self.cursor.fetchone()[0], self.conn)

    def get_param_value(self, param_name):
        return self.get_param(param_name).get_val()

    def get_card_type_id(self):
        sqlstr = '''SELECT card_type_id
                    FROM Card
                    WHERE id=:id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_all_params(self) -> List[Param]:
        sqlstr = '''SELECT Param.id
                    FROM Param
                    WHERE Param.card_id = :id;'''
        self.cursor.execute(sqlstr, {'id': self.id})
        params = [Param(a[0], self.conn) for a in self.cursor.fetchall()]
        return params

    def has_param(self, param_name: str) -> bool:
        """Returns true if card has given param, the param is visible, and the param is > 0"""
        params = self.get_all_params()
        for p in params:
            if p.is_visible() and p.get_name() == param_name and p.get_val() > 0:
                return True
        return False

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

    # --------------------
    def render(self) -> str:
        return render_card(self.get_art(), self.get_name(), self.get_rarity(),
                           self.get_description(), self.get_all_params())


def render_card(art: str, name: str, rarity: str, desc: str, params: list) -> str:
    """Returns a string representing the ascii image of this card."""
    # TODO: Card art saving with extra character on all but last line. Need to fix in CCD
    # Temp fix is in tho-- the overwriting art lines thing
    render_lines = []
    pic_width = 38
    pic_height = 25
    art_lines = art.split('\n')
    art_lines = [l[:-1] for l in art_lines[:-1]] + [art_lines[-1]]
    desc = desc.split('\n')
    # Header
    render_lines.append('+' + '-'*(pic_width-2) + '+')
    render_lines.append(r'| {}{}{} |'.format(name,
                                             ' '*(pic_width-4 - len(name) - len(rarity)),
                                             rarity))
    # Empty between header and art
    render_lines.append('|' + ' '*(pic_width-2) + '|')
    # Art
    for line in art_lines:
        render_lines.append(f'|{line}|')
    # Description
    desc_h_space = pic_width-2
    description_lines = []
    for line in desc:
        line_split = [line[i:i + desc_h_space] for i in range(0, len(line), desc_h_space)]
        description_lines += line_split
    for line in description_lines:
        if len(line) < desc_h_space:
            render_lines.append('|' + line + ' ' * (desc_h_space - len(line)) + '|')
        else:
            render_lines.append(f'|{line}|')
    # Empty between desc and params
        render_lines.append('|' + ' '*(pic_width-2) + '|')
    # Footer - Params
    paramlines = []
    for param in params:
        if param.is_visible():
            val = param.get_val()
            param_max = param.get_max()
            if param_max is None:
                paramtext = f'{param.get_name()}: {val}'
            else:
                paramtext = f'{param.get_name()}: {val}/{param_max}'
            paramlines.append('|' + ' '*(pic_width-3-len(paramtext)) + paramtext + ' |')
    for i in range(max(0, pic_height-len(paramlines)-len(render_lines))):
        render_lines.append('|' + ' ' * (pic_width - 2) + '|')
    for p in paramlines:
        render_lines.append(p)
    render_lines.append('+' + '-'*(pic_width - 2) + '+\n')
    render_str = ''
    for r in render_lines:
        render_str += r + '\n'
    return '```' + render_str + '```'
