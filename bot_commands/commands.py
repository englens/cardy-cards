import sqlite3
import discord
import asyncio

from . import debug_commands
from game_objects import player
from .tutorial import tutorial
from utils import debug_utils, bot_utils
from . import select_command_cases
import player_state as p_state

"""
Module Description:
    Bot commands, able to be run by player. These commands are called by the on_message function in main.
"""

ERRMSG_INVALID_PERMS = 'You do not have permission to use that command.'
DEFAULT_NEW_PLAYER_CARD = 'money button'


async def debug_command(message: discord.Message, session_player: player.Player, terms: list, conn: sqlite3.Connection):
    if not debug_utils.can_player_debug(session_player):
        await message.channel.send(ERRMSG_INVALID_PERMS)
        return

    if len(terms) == 0:
        await message.channel.send('Please supply debug terms!')
        return
    try:
        if terms[0] == 'unlock_shop':
            await debug_commands.unlock_shop(message, session_player, terms, conn)
        elif terms[0] == 'dbclear':
            await debug_commands.dbclear(message, session_player)
    except IndexError:
        await message.channel.send('Improper Command Format.')


async def inventory_command(message: discord.Message, session_player: player.Player, t: int):
    """Shows inventory and switches state"""
    p_state.set_player_state(session_player.id, p_state.InventoryState())
    msg = session_player.render(t)
    await message.channel.send(msg)


async def row_command(message: discord.Message, session_player: player.Player, t: int, row_index: int):
    """Selects specific row, rendering it and switching state"""
    session_row = session_player.get_row(row_index)
    if session_row is None:
        await message.channel.send('Error: No Row with that index.')
        return
    await message.channel.send(session_row.render(t))
    p_state.set_player_state(session_player.id, p_state.RowState(session_row))


async def card_command(message: discord.Message, session_player: player.Player,
                       t: int, row_index: int, card_index: int):
    """Selects specific card, rendering it and switching state."""
    session_row = session_player.get_row(row_index)
    if session_row is None:
        await message.channel.send('Error: No Row with that index.')
        return
    session_card = session_row.get_card(card_index, t)
    if session_card is None:
        await message.channel.send('Error: No Card with that index.')
    await message.channel.send(session_card.render())
    p_state.set_player_state(session_player.id, p_state.CardState(session_row, session_card))


# Displays a shop, including all cards available for purchase
async def shop_command(message: discord.Message, session_player: player.Player, shop_index):
    """Selects specific shop, rendering it and switching state"""
    shop_index -= 1
    shops = session_player.get_unlocked_shops()
    if shop_index < 0 or shop_index >= len(shops):
        await message.channel.send('Please enter a valid index.')
        return
    p_state.set_player_state(session_player.id, p_state.ShopState(shops[shop_index]))
    await message.channel.send(shops[shop_index].render())


# brings up list of shops a player can access, with numbers for each
# changes the state to shop menu, displays shop menu
async def shop_menu_command(message: discord.Message, session_player: player.Player):
    """Shows shop menu and switches state"""
    p_state.set_player_state(session_player.id, p_state.ShopMenuState())
    await message.channel.send(session_player.get_shop_menu_render())


async def shop_card_command(message: discord.Message, session_player: player.Player, card_index):
    """Selects card, showing the full art render and switches state
       Currently only triggered with !select from stop state"""
    state = p_state.get_player_state(session_player.id)
    if not isinstance(state, p_state.ShopState):
        await message.channel.send('Something went wrong. shop_card_command triggered outside of shop state.')
        return
    session_shop = state.shop
    session_card = session_shop.get_listing_from_index(card_index)
    p_state.set_player_state(session_player.id, p_state.ShopCardState(session_shop, session_card))
    await message.channel.send(session_card.get_card_render())


async def buy_command(message: discord.Message, session_player: player.Player, card_index: int = None):
    state = p_state.get_player_state(session_player.id)
    # Verify valid state and syntax, fetch session card
    if isinstance(state, p_state.ShopCardState):
        if card_index is not None:
            await message.channel.send('Improper format: buy index not needed when examining a Card listing.')
            return
        session_card = state.listing
    elif isinstance(state, p_state.ShopState):
        if card_index is None:
            await message.channel.send('Improper format: Please supply an index or !examine a Card listing first.')
            return
        session_card = state.shop.get_listing_from_index(card_index)
    else:
        # state has no valid buy command
        await message.channel.send('Nothing to buy from this game state.')
        return
    # ---------------

    response = session_player.try_pay(session_card.get_price_name(), session_card.get_price())
    if response is None:
        await message.channel.send(f'Not enough {session_card.get_price_name()} to pay cost.')
        return

    await message.channel.send(f'Bought [{session_card.get_card_type_name()}]!')
    await asyncio.sleep(1)
    msg = '''Please !select an option:
             1 - Place card into a Row
             2 - Place card into your Card Vault'''

    await message.channel.send(msg)
    p_state.set_player_state(session_player.id, p_state.BuySelectRowState(state.shop, session_card))


async def use_command(message: discord.Message, session_player: player.Player):
    state = p_state.get_player_state(session_player.id)
    if not isinstance(state, p_state.CardState):
        await message.channel.send('Nothing to use -- Please select a card first.')
    else:
        await state.session_card.use(message)
    # TODO: Edit the OG card message if the card changed. This way we dont have to reshow the new card
    # OR have card produce "summary" messages


async def select_command(message: discord.Message, session_player: player.Player, t: int, param1: int, param2: int = None):
    """General command to 'select' something from a list by index.
       Can optionally take two parameters (ex, !inventory 2 1, for row 2 card 1)
       INDEXES START WITH 1!"""
    state = p_state.get_player_state(session_player.id)
    if isinstance(state, p_state.RowState):  # Browsing 1 row
        await card_command(message, session_player, state.session_row.get_index(), param1, t)
    elif isinstance(state, p_state.InventoryState):  # Looking at all rows
        await row_command(message, session_player, t, param1)
    elif isinstance(state, p_state.ShopMenuState):  # Looking at all shops
        await shop_command(message, session_player, param1)
    elif isinstance(state, p_state.ShopState):  # Browsing 1 shop
        await shop_card_command(message, session_player, param1)
    elif isinstance(state, p_state.BuySelectRowState):
        await select_command_cases.buy_select_row(message, session_player, param1)
    elif isinstance(state, p_state.BuyPlaceCardVaultOrRow):
        await select_command_cases.buy_select_vault_or_row(message, session_player, t, param1, state)
    else:
        await message.channel.send('Nothing to select')


async def help_command(message: discord.Message, session_player: player.Player, show_all: bool = False):
    """Displays a list of commands possible for the current state"""
    pass
    # TODO: Show general help menu, and state specific help if applicable


async def player_creation(message, players_in_session, client: discord.Client, conn: sqlite3.Connection, t):
    """Create a new player from the message's author"""
    pinput = bot_utils.PInput(client, message)
    p_name = await pinput.player_input('What do you want to be named?')
    new_player = player.register_new_player(conn, message.author.id, p_name)
    print('done')
    new_row = new_player.add_row()
    new_row.add_card(DEFAULT_NEW_PLAYER_CARD)
    players_in_session.append(new_player)
    await message.channel.send('You are now registered to play. ' +
                               'I\'ve given you a card to start you off.')

    response = await pinput.yes_or_no('Do the (short) tutorial?')
    if response == 'yes':
        await tutorial(message, new_player, client, t)
    else:
        await message.channel.send('Alright. You have been given one card to start off. Type !help to see commands. Good Luck!')
    players_in_session.remove(new_player)
