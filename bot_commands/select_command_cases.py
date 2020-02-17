import discord
import player_state as p_state
import asyncio
from game_objects import player


async def buy_select_row(message: discord.Message, session_player: player.Player, row_index: int):
    """Player has bought a card and chosen to place it in a row, and selected a row"""

    state = p_state.get_player_state(session_player.id)
    assert isinstance(state, p_state.BuySelectRowState)
    try:
        session_row = session_player.get_row(row_index)
    except Exception:
        await message.channel.send('Invalid Row Index.')
        return
    if session_row.remaining_slots() <= 0:
        await message.channel.send('Selected Row full; please select another Row or make room.')
    # ----------
    card_name = state.listing.get_card_type_name()
    session_row.add_card(card_name)
    await message.channel.send(f'[{card_name}] added to Row {session_row.get_index()}')
    await asyncio.sleep(2)
    await message.channel.send('Returning to shop...')
    await asyncio.sleep(1)
    await message.channel.send(state.session_shop.render())
    p_state.set_player_state(session_player.id, p_state.ShopState(state.session_shop))


async def buy_select_vault_or_row(message: discord.Message, session_player: player.Player, choice: int,  state: p_state.BaseState):
    """Player has bought a card and has room in at least 1 row, and are now
       choosing to place it in the vault or in a row"""
    '''Before: Please !select an option:
             1 - Place card into a Row
             2 - Place card into your Card Vault'''
    assert isinstance(state, p_state.BuyPlaceCardVaultOrRow)
    if choice == 1:  # row
        await message.channel.send('Please !select a row:\n' + session_player.render())
        p_state.set_player_state(session_player.id, p_state.BuySelectRowState(state.session_shop, state.listing))
    elif choice == 2:  # vault
        session_player.add_card_to_vault(state.listing.get_card_type_id())
        await message.channel.send('Added to vault.')
        await asyncio.sleep(2)
        await message.channel.send(f'Returning to shop...')
        await asyncio.sleep(1)
        p_state.set_player_state(session_player.id, p_state.ShopState(state.session_shop))
    else:  # improper input
        await message.channel.send(f'Improper Choice index.')

