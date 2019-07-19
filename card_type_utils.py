import card
def make_card_type(conn, name, rarity, description, art, class_name):
    sqlstr = """INSERT INTO CardType (name, rarity, description, art, class_name)
                VALUES (:name, :rarity, :description, :art, :class_name);"""
    data = {'name': name,
            'rarity': rarity,
            'description': description,
            'art': art,
            'class_name': class_name}
    conn.execute(sqlstr, data)
    conn.execute()


# takes FULL CARD and returns only art area
def card_art_extractor(full_art):
    art = ''
    full_art_lines = full_art.split('\n')
    for line in full_art_lines[4:15]:
        art += line[3:37] + '\n'
    art += full_art_lines[15][3:37]
    return art


def register_new_card_type(type_class):
    params: list = type_class.get_param_types()
    for param in params:
        pass  # TODO

def register_new_param_type(param_def: card.ParamDefinition):
    sqlstr = """INSERT INTO ParamType (name, value_default, max_default, visible_default, card_type)"""