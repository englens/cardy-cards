from game_objects import player
from game_objects import shop
import sqlite3


def can_player_debug(session_player: player.Player):
    return True  # TODO: implement actual checking before vslice


def register_player_with_shop(session_player: player.Player, session_shop: shop.Shop, sql_conn: sqlite3.Connection):
    if session_shop.has_player_unlocked(session_player):
        raise sqlite3.IntegrityError()

    sqlstr = '''INSERT INTO ShopUnlocked (player_id, shop_id)
                VALUES (:p_id, :s_id);'''
    sql_conn.execute(sqlstr, {'p_id': session_player.id, 's_id': session_shop.id})
    sql_conn.commit()

