from enum import Enum
from game_objects.shop import Shop
from game_objects.row import Row
from game_objects.card import Card
from game_objects.shop_listings import ShopListing
import time

"""
Module Description:
    Provides easy interface for remembering the current "state" they player is in.
    This module may be interfaced with using get_player_state and set_player_state.
"""

STATE_TIMEOUT = 120
player_states = {}  # did:{state, time}


class BaseState:
    """Used for inheritance purposes (for type hints)"""
    pass


class DefaultState(BaseState):
    """State when player is in no special screen."""
    pass


class InventoryState(BaseState):
    """State when player is looking at their list of rows, but haven't selected a row."""
    pass


class RowState(BaseState):
    """State when player is looking at a specific row. Stores current Row."""
    def __init__(self, session_row: Row):
        self.session_row: Row = session_row


class CardState(BaseState):
    """State when player is looking at a card they own. Stores current row and card."""
    def __init__(self, session_row: Row, session_card: Card):
        # Technically we can get the row from the card object, but this makes things easier
        # If slowdown is noticeable may remove this, but i doubt it
        self.session_row: Row = session_row
        self.session_card: Card = session_card


class ShopMenuState(BaseState):
    """State when player is looking at the list of Shops, but has not selected one yet."""
    pass


class ShopState(BaseState):
    """State when player is looking at a specific shop. Stores the shop they are looking at."""
    def __init__(self, shop: Shop):
        self.shop: Shop = shop


class ShopCardState(BaseState):
    """State when the player is looking at a specific card in a shop.
       Stores the Shop and the ShopListing (that contains card information)"""
    def __init__(self, session_shop: Shop, session_card: ShopListing):
        self.shop: Shop = session_shop
        self.card: ShopListing = session_card


class ShopCardSelectRowState(BaseState):
    """State when player has bought a card and needs to place it in """
    def __init__(self, session_shop: Shop, session_card: ShopListing):
        self.shop: Shop = session_shop
        self.card: ShopListing = session_card


def get_player_state(player_id: int):
    """Returns the current player state. Accounts for state timeouts and reverts the player to default if timed out."""
    try:
        if time.time() - player_states[player_id]['time'] > STATE_TIMEOUT:
            player_states[player_id] = {'state': DefaultState(), 'time': time.time()}
        return player_states[player_id]['state']
    except KeyError:
        player_states[player_id] = {'state': DefaultState(), 'time': time.time()}
        return player_states[player_id]['state']


def set_player_state(player_id: int, new_state: BaseState):
    player_states[player_id] = {'state': new_state, 'time': time.time()}
    print(f'Set {player_id} to state {player_states[player_id]["state"]}')
