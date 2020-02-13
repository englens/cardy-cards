import sqlite3
"""Utility functions relating to card types and param types"""


def get_card_type_class_from_card_id(card_id: int, cursor: sqlite3.Cursor) -> str:
    sqlstr = '''SELECT CardType.class_name
                FROM CardType
                    JOIN Card ON Card.card_type_id = CardType.id
                WHERE Card.id = :id;'''
    cursor.execute(sqlstr, {'id': card_id})
    return cursor.fetchone()[0]


def get_card_type_id_from_name(card_name: str, cursor: sqlite3.Cursor) -> int:
    sqlstr = '''SELECT id 
                FROM CardType
                WHERE name=:name;'''
    cursor.execute(sqlstr, {'name': card_name})
    return cursor.fetchone()[0]


def get_param_types(card_type_id: int, cursor: sqlite3.Cursor) -> list:
    """Returns a list of ParamType PKs for given card type"""
    sqlstr = '''SELECT id
                FROM ParamType
                WHERE card_type=:cid;'''
    cursor.execute(sqlstr, {'cid': card_type_id})
    return [i[0] for i in cursor.fetchall()]


def get_param_type_defaults(param_id: int, cursor: sqlite3.Cursor) -> dict:
    """Return a list of default values for given param type
    :param param_id: id of given param type
    :param cursor: sqlite cursor to game database
    :return: dict consisting of 'val', 'visible' and 'max_val'
    """
    sqlstr = '''SELECT value_default, visible_default, max_default
                FROM ParamType
                WHERE id=:pid;'''
    cursor.execute(sqlstr, {'pid': param_id})
    data = cursor.fetchone()
    return {'val': data[0], 'visible': data[1], 'max_val': data[2]}


def get_all_card_classes(cursor: sqlite3.Cursor) -> list:
    """Returns a list of every card class string; used to import all the card types"""
    sqlstr = '''SELECT class_name FROM CardType;'''
    cursor.execute(sqlstr)
    return [a[0] for a in cursor.fetchall()]
