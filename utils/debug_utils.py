from player import Player
from shop import Shop
import sqlite3


def can_player_debug(player: Player):
    return True  # TODO: implement actual checking before vslice


def register_player_with_shop(player: Player, shop: Shop, sql_conn: sqlite3.Connection):
    if shop.has_player_unlocked(player):
        raise sqlite3.IntegrityError()

    sqlstr = '''INSERT INTO ShopUnlocked (player_id, shop_id)
                VALUES (:p_id, :s_id);'''
    sql_conn.execute(sqlstr, {'p_id': player.id, 's_id': shop.id})
    sql_conn.commit()

