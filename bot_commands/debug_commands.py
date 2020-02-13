import discord
import shop
import sqlite3
import debug_utils
from player import Player
"""
Module Description:
    Debug bot commands used for testing. Only used by admin users.
"""


async def unlock_shop(message: discord.Message, session_player: Player, terms: list, conn: sqlite3.Connection):
    # Rest of command is shop name
    try:
        session_shop = shop.get_shop_by_name(' '.join(terms[1:]), conn.cursor())
    except sqlite3.DatabaseError:
        await message.channel.send('Shop not found.')
        return
    try:
        debug_utils.register_player_with_shop(session_player, session_shop, conn)
        await message.channel.send('Unlocked.')
    except sqlite3.IntegrityError:
        await message.channel.send('Shop Already Unlocked.')


async def dbclear(message: discord.Message, session_player: Player):
    """Deletes session player from database"""
    session_player.delete()
    await message.channel.send('Player Profile Deleted.')
