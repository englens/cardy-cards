from collections import namedtuple
import time
ParamType = namedtuple('ParamType', ['name', 'val_default', 'max_default', 'visible_default', 'card_type'])


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
class Card:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def __eq__(self, other):
        return self.id == other.id and type(self) == type(other)

    ## INTERFACE ##


    def passive(self, message, t):
        """Called every time the card is used or displayed. Returns a string along
           the lines of 'Made 5 money since last checked'"""
        return ''

    # Called when
    def use(self, message):
        """Does something when activated with !use."""
        return ''

    @staticmethod
    def get_param_types() -> list:
        """returns list of ParamDefinitions for each param.
           Subclasses should invoke and add to super."""
        return []

    ################

    def validate(self) -> bool:
        sqlstr = '''SELECT EXISTS(SELECT 1 FROM Card WHERE id = :id);'''
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_name(self) -> str:
        sqlstr = '''SELECT name 
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
                    WHERE Card.id=:id
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

    # THANK GOD FOR BLOBS
    def get_param(self, param_name) -> Param:
        sqlstr = '''SELECT Param.id
                    FROM Param
                        JOIN Card ON Card.id = Param.card_id
                        JOIN ParamType ON ParamType.id = Param.type_id
                    WHERE ParamType.name=:name
                    AND Card.id = :id;'''
        self.cursor.execute(sqlstr, {'name': param_name, 'id': self.id})
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

    def render(self) -> str:
        return render(self.get_art(), self.get_name(), self.get_rarity(), self.get_description(), self.get_all_params())


class ParamDefinition:
    """Defines a Param (ParamType) for use in Card.get_param_types()."""
    def __init__(self, name: str, base_val, base_visible: bool, max_default=None):
        self.name = name
        self.base_val = base_val
        self.base_visible = base_visible
        self.max_default = max_default


class MoneyButton(Card):
    """Gives the player 5 money every 1 hour."""
    DELAY_BETWEEN_USES = 60*60  # 1 hour
    MONEY_ON_USE = 5

    def use(self, message) -> str:
        time_since_last = time.time() - self.get_param('last_use').get_val()
        if time_since_last < MoneyButton.DELAY_BETWEEN_USES:
            # Too soon
            return f'Please Wait {time_since_last - MoneyButton.DELAY_BETWEEN_USES} seconds before use.'
        money = self.get_param('money')
        if money.get_val() + MoneyButton.MONEY_ON_USE > money.get_max():
            money.set_val(money.get_max())
        else:
            money.set_val(money.get_val() + MoneyButton.MONEY_ON_USE)

    @staticmethod
    def get_param_types() -> list:
        params = super().get_param_types()
        params.append(ParamDefinition('money', base_val=0, base_visible=True, max_default=100))
        params.append(ParamDefinition('last_use', base_val=0, base_visible=False, max_default=None))
        return params


    # def render(self) -> str:
    #     """Returns a string representing the ascii image of this card."""
    #     art_lines = self.get_art().split('\n')
    #     name = self.get_name()
    #     rarity = self.get_rarity()
    #     desc = self.get_description().split('\n')
    #     top_art_line = art_lines[0]
    #     mid_art_lines = art_lines[1:-1]
    #     bot_art_line = art_lines[-1]
    #     # Header
    #     render_str = '+' + '-' * 38 + '+\n'
    #     render_str += r'| {}{}{} |'.format(name,
    #                                        ' ' * (36 - (len(name) + len(rarity))),
    #                                        rarity) + '\n'
    #     render_str += '|' + ' ' * 38 + ' \n'
    #     # Art
    #     render_str += '|  /' + '-' * 32 + r'\  |' + '\n'
    #     render_str += '| /' + top_art_line + r'\ |' + '\n'
    #     for line in mid_art_lines:
    #         render_str += '| |' + line + '| |\n'
    #     render_str += '| \\' + bot_art_line + '/ |\n'
    #     render_str += '|  \\' + '-' * 32 + '/  |' + '\n'
    #     # Description
    #     desc_h_space = 38
    #     description_lines = []
    #     for line in desc:
    #         line_split = [line[i:i + desc_h_space] for i in range(0, len(line), desc_h_space)]
    #         description_lines += line_split
    #     for line in description_lines:
    #         if len(line) < desc_h_space:
    #             render_str += '|' + line + ' ' * (desc_h_space - len(line)) + '|\n'
    #         else:
    #             render_str += '|' + line + '|\n'
    #     render_str += '|' + ' ' * 38 + ' \n'
    #     # Footer
    #     for param in self.get_all_params():
    #         if param.is_visible():
    #             val = param.get_val()
    #             if type(val) in [int, float]:
    #                 paramtext = param.get_name() + ': ' + val + '/' + param.get_max()
    #             else:
    #                 paramtext = val
    #             render_str += '|' + ' ' * (37 - len(paramtext)) + paramtext + ' |'
    #     render_str = '+' + '-' * 38 + '+\n'
    #     return '```' + render_str + '```'


def render(art: str, name: str, rarity: str, desc: str, params: list) -> str:
    """Returns a string representing the ascii image of this card."""
    art_lines = art.split('\n')
    desc = desc.split('\n')
    top_art_line = art_lines[0]
    mid_art_lines = art_lines[1:-1]
    bot_art_line = art_lines[-1]
    # Header
    render_str = '+' + '-' * 38 + '+\n'
    render_str += r'| {}{}{} |'.format(name,
                                       ' ' * (36 - (len(name) + len(rarity))),
                                       rarity) + '\n'
    render_str += '|' + ' ' * 38 + ' \n'
    # Art
    render_str += '|  /' + '-' * 32 + r'\  |' + '\n'
    render_str += '| /' + top_art_line + r'\ |' + '\n'
    for line in mid_art_lines:
        render_str += '| |' + line + '| |\n'
    render_str += '| \\' + bot_art_line + '/ |\n'
    render_str += '|  \\' + '-' * 32 + '/  |' + '\n'
    # Description
    desc_h_space = 38
    description_lines = []
    for line in desc:
        line_split = [line[i:i + desc_h_space] for i in range(0, len(line), desc_h_space)]
        description_lines += line_split
    for line in description_lines:
        if len(line) < desc_h_space:
            render_str += '|' + line + ' ' * (desc_h_space - len(line)) + '|\n'
        else:
            render_str += '|' + line + '|\n'
    render_str += '|' + ' ' * 38 + ' \n'
    # Footer
    for param in params:
        if param.is_visible():
            val = param.get_val()
            if type(val) in [int, float]:
                paramtext = param.get_name() + ': ' + val + '/' + param.get_max()
            else:
                paramtext = val
            render_str += '|' + ' ' * (37 - len(paramtext)) + paramtext + ' |'
    render_str = '+' + '-' * 38 + '+\n'
    return '```' + render_str + '```'

