import discord
import player_state as p_state
import asyncio


async def buy_select_row(message: discord.Message, session_player: player.Player, row_index: int):
    state = p_state.get_player_state(session_player.id)
    assert isinstance(state, p_state.ShopCardSelectRowState)
    try:
        session_row = session_player.get_row(row_index)
    except Exception:
        await message.channel.send('Invalid Row Index.')
        return
    if session_row.remaining_slots() <= 0:
        await message.channel.send('Selected Row full; please select another Row or make room.')
    # ----------
    card_name = state.card.get_card_type_name()
    session_row.add_card(card_name)
    await message.channel.send(f'[{card_name}] added to Row {session_row.get_index()}')
    await asyncio.sleep(2)
    await message.channel.send('Returning to shop...')
    await asyncio.sleep(1)
    await message.channel.send(state.shop.render())
    p_state.set_player_state(session_player.id, p_state.ShopState(state.shop))

async def buy_select_vault_or_row(message: discord.Message, session_player: discord.Player, choice: str):
    if choice == '1':

