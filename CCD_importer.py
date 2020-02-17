import sqlite3


def read_db(conn):
    curr = conn.cursor()
    sqlstr = '''SELECT id, name, rarity, description, art, class_name
                FROM CardType;'''
    curr.execute(sqlstr)
    data = curr.fetchall()
    out = {}
    for d in data:
        sqlstr = '''SELECT name, value_default, max_default, visible_default
                    FROM ParamType 
                    WHERE card_type_id=:id;'''
        curr.execute(sqlstr, {'id': d[0]})
        out[d[1]] = {'c_type': d[1:], 'params': curr.fetchall()}
    return out


def insert_card(card_data, conn):
    curr = conn.cursor()
    data = {'name': card_data[0],
            'rarity': card_data[1],
            'desc': card_data[2],
            'art': card_data[3],
            'class_name': card_data[4]}
    sqlstr = '''INSERT INTO CardType (name, rarity, description, art, class_name)
                VALUES (:name, :rarity, :desc, :art, :class_name);'''
    curr.execute(sqlstr, data)
    conn.commit()
    return curr.lastrowid


def insert_param(param_data, conn, c_type_id):
    curr = conn.cursor()
    sqlstr = '''INSERT INTO ParamType (name, value_default, max_default, visible_default, card_type_id)
                    VALUES (:name, :val_d, :max_d, :vis_d, :c_type);'''
    data = {'name': param_data[0],
            'val_d': param_data[1],
            'max_d': param_data[2],
            'vis_d': param_data[3],
            'c_type': c_type_id}  # use the new one
    curr.execute(sqlstr, data)
    conn.commit()


def merge_data(data_in, data_master, conn_master):
    classes = []
    for c_name in data_in:
        if c_name in data_master:
            print(f'{c_name} NOT IMPORTED --  already present in master database.')
        else:
            c_id = insert_card(data_in[c_name]['c_type'], conn_master)
            for p in data_in[c_name]['params']:
                insert_param(p, conn_master, c_id)
            print(f'{c_name} IMPORTED -- {len(data_in[c_name]["params"])} params.')
            classes.append(data_in[c_name]['c_type'][4])
    if len(classes) > 0:
        print(f'Done\n------------\nNOTE: Card Classes {str(classes)} need to be merged manually. Place these in the card_classes directory.')


def main():
    db_file_input = input('Name of sqlite database to import from: ')
    db_file_output = input('Name of sqlite database to write to: ')
    conn_in = sqlite3.connect(db_file_input)
    conn_master = sqlite3.connect(db_file_output)
    data_in = read_db(conn_in)
    data_master = read_db(conn_master)
    merge_data(data_in, data_master, conn_master)


if __name__ == '__main__':
    main()
