import sqlite3
import discord
import bot_utils
import player
import player_state as p_state
import debug_utils
import debug_commands
from tutorial import tutorial

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


async def inventory_command(message: discord.Message, session_player: player.Player):
    """Shows inventory and switches state"""
    p_state.set_player_state(session_player.id, p_state.InventoryState())
    msg = session_player.render()
    await message.channel.send(msg)


async def row_command(message: discord.Message, session_player: player.Player, row_index: int):
    """Selects specific row, rendering it and switching state"""
    session_row = session_player.get_row(row_index)
    await message.channel.send(session_row.render())
    p_state.set_player_state(session_player.id, p_state.RowState(session_row))


async def card_command(message: discord.Message, session_player: player.Player,
                       row_index: int, card_index: int):
    """Selects specific card, rendering it and switching state."""
    session_row = session_player.get_row(row_index)
    session_card = session_row.get_card(card_index)

    msg = session_card.render()
    await message.channel.send(msg)
    p_state.set_player_state(session_player.id, p_state.CardState(session_row, session_card))


# Displays a shop, including all cards available for purchase
async def shop_command(message: discord.Message, session_player: player.Player, shop_index):
    """Selects specific shop, rendering it and switching state"""
    shop_index -= 1
    shops = session_player.get_unlocked_shops()
    if shop_index < 0 or shop_index >= len(shops):
        message.channel.send('Please enter a valid index.')
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


async def use_command(message: discord.Message, session_player: player.Player):
    state = p_state.get_player_state(session_player.id)
    if not isinstance(state, p_state.CardState):
        await message.channel.send('Nothing to use -- Please select a card first.')
    else:
        await state.session_card.use(message)
    # TODO: Edit the OG card message if the card changed. This way we dont have to reshow the new card


async def select_command(message: discord.Message, session_player: player.Player, param1: int, param2: int = None):
    """General command to 'select' something from a list by index.
       Can optionally take two parameters (ex, !inventory 2 1, for row 2 card 1)
       INDEXES START WITH 1!"""

    state = p_state.get_player_state(session_player.id)
    if isinstance(state, p_state.RowState):  # Browsing 1 row
        await card_command(message, session_player, state.session_row.get_index(), param1)
    elif isinstance(state, p_state.InventoryState):  # Looking at all rows
        await row_command(message, session_player, param1)
    elif isinstance(state, p_state.ShopMenuState):  # Looking at all shops
        await shop_command(message, session_player, param1)
    elif isinstance(state, p_state.ShopState):  # Browsing 1 shop
        await shop_card_command(message, session_player, param1)
    else:
        await message.channel.send('Nothing to select')


async def help_command(message: discord.Message, session_player: player.Player):
    """Displays a list of commands possible for the current state"""
    pass
    # TODO: Show general help menu, and state specific help if applicable


async def player_creation(message, players_in_session, client: discord.Client, conn: sqlite3.Connection):
    """Create a new player from the message's author"""
    channel = message.channel
    pinput = bot_utils.PInput(client, message)
    p_name = await pinput.player_input('What do you want to be named?')
    new_player = player.register_new_player(conn, message.author.id, p_name)
    row = new_player.add_row()
    row.add_card(DEFAULT_NEW_PLAYER_CARD)
    players_in_session.append(new_player)
    await channel.send('You are now registered to play. ' +
                       'I\'ve given you a card to start you off.')

    response = await pinput.yes_or_no('Do the (short) tutorial?')
    if response == 'yes':
        await tutorial(message, new_player, client)
    else:
        await channel.send('Alright. You have been given one card to start off. Type !help to see commands. Good Luck!')
    players_in_session.remove(new_player)


async def join_command(message: discord.Message, session_player: player.Player):
    """Notify the player when they've already joined"""
    await message.channel.send('You\ve already joined! Say !help if you don\'t know what to do.')