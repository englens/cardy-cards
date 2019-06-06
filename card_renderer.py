class Card:
    def __init__(self, name, art, desc, params):
        self.name = name
        self.art = art
        self.desc = desc
        self.params = params

    def add_param(self, param):
        self.params.append(param)

    def render_card(self):
        art_lines = self.art.split('\n')

        # topstring = '| ' + <name> + <spaces> + <rarity> + ' |'
        # art = '| /' + <art, with \n replaced by '| |\n| |'> + '/ |'


class Param:
    def __init__(self, name, max, current=0):
        self.name = name
        self.max = max
        self.current = current
