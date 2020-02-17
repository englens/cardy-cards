import discord
import sqlite3
import traceback

import game_objects.player as player
import bot_commands.commands as commands
import cards
from utils import card_type_utils
"""
Module Description:
    Main module containing code entrypoint and general program administration. Also handles bot setup and events.
"""


# CONSTANTS
BOT_ID = ''
KEY_PATH = 'key.txt'

# GLOBALS
conn = sqlite3.connect('test_db.sqlite')
sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
players_in_session = []

client = discord.Client()


@client.event
async def on_ready():
    print('Ready.')
    

@client.event
async def on_message(message: discord.Message):

    # Checking for bots, non-commands or unregistered players
    if not message.content.startswith('!'):
        return
    if message.author.bot:
        return
    try:
        session_player = player.get_player(conn, message.author.id)
    except sqlite3.DatabaseError:
        if message.content == '!join':
            await commands.player_creation(message, players_in_session, client, conn)
        else:
            await message.channel.send('Please create an account with !join')
        return

    # Whole loop is wrapped in try block that logs errors before sending them up
    try:
        if session_player in players_in_session:
            return
        # Block player from being handled twice at once
        players_in_session.append(session_player)
        terms = message.content[1:].split(' ')
        command = terms[0]
        terms = terms[1:]
        if command == 'shop':
            if len(terms) == 1:
                pass  # TODO: quick nav to shop
            else:
                await commands.shop_menu_command(message, session_player)
        if command == 'inventory':
            await commands.inventory_command(message, session_player)
        elif command == 'row':
            await commands.row_command(message, session_player, int(terms[0]))
        elif command == 'use':
            await commands.use_command(message, session_player)
        elif command == 'select':
            if len(terms) == 2:
                try:
                    t1 = int(terms[0])
                    t2 = int(terms[1])
                except ValueError:
                    message.channel.send('!select parameters must be integers.')
                    return
                await commands.select_command(message, session_player, t1, t2)
            else:
                try:
                    t1 = int(terms[0])
                except ValueError:
                    message.channel.send('!select parameters must be integers.')
                    return
                await commands.select_command(message, session_player, t1)
        elif command == 'card':
            await commands.card_command(message, session_player, terms[0], terms[1])
        elif command == 'help':
            pass
        elif command == 'debug':
            await commands.debug_command(message, session_player, terms, conn)
        else:
            pass
        players_in_session.remove(session_player)

    except Exception as e:
        # Send exceptions to the discord, for testing
        # TODO: Remove before going live, or implement a "last error" feature only i can see
        # or logging
        tb = traceback.format_exc()
        await message.channel.send(tb)
        players_in_session.remove(session_player)
        raise e


if __name__ == '__main__':
    cards.import_cards(card_type_utils.get_all_card_classes(conn.cursor()))
    with open(KEY_PATH, 'r') as f:
        key = f.read()
    client.run(key)
