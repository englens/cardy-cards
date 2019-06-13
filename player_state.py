from enum import Enum
import time

STATE_TIMEOUT = 120
player_states = {}  # did:state


class State(Enum):
    # Comments show state_param def
    DEFAULT = 1  # []
    INVENTORY = 2  # []
    ROW = 3  # [row_index]
    CARD = 4  # [row_index, card_index]
    SHOP_MENU = 5  # []
    SHOP = 6  # [shop_id]
    SHOP_CARD_EXAMINE = 7  # [shop_id, index]


# Base

class BaseState:
    def __init__(self, state):
        self.state = state


class DefaultState(BaseState):
    def __init__(self):
        super().__init__(state=State.DEFAULT)


class InventoryState(BaseState):
    def __init__(self):
        super().__init__(state=State.INVENTORY)


class RowState(BaseState):
    def __init__(self, row_index):
        super().__init__(state=State.ROW)
        self.row_index = row_index


class CardState(BaseState):
    def __init__(self, row_index, card_index):
        super().__init__(state=State.CARD)
        self.row_index = row_index
        self.card_index = card_index


class ShopMenuState(BaseState):
    def __init__(self):
        super().__init__(state=State.SHOP_MENU)


class ShopState(BaseState):
    def __init__(self, shop_id):
        super().__init__(state=State.SHOP)
        self.shop_id = shop_id


class ShopCardState(BaseState):
    def __init__(self, shop_id, card_index):
        super().__init__(state=State.SHOP_CARD_EXAMINE)
        self.shop_id = shop_id
        self.card_index = card_index


def get_player_state(discord_id: int):
    try:
        if time.time() - player_states[discord_id]['time'] > STATE_TIMEOUT:
            player_states[discord_id] = State.DEFAULT
            return State.DEFAULT
        return player_states[discord_id]['state']
    except KeyError:
        player_states[discord_id] = {'state': DefaultState(), 'time': time.time()}
        return player_states[discord_id]['state']


def set_player_state(discord_id: int, new_state: BaseState):
    player_states[discord_id] = {'state': new_state, 'time': time.time()}
