import discord
import asyncio
import bot_utils
import player
DEFAULT_MESSAGE_DELAY = 2

"""
Module Description:
    Tutorial sequence offered to new players. This is called in the "player_creation" command.
"""


async def tutorial(message, session_player: player.Player, client: discord.Client):
    channel = message.channel
    pinput = bot_utils.PInput(client, message)
    try:
        await channel.send('In this game, you collect Cards that work together in unique ways to create resources.')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await pinput.ask_loop('Lets look at that card I gave you.\n' +
                              'Pull up your inventory with !inventory.', ['!inventory'],
                              restated_question='Pull up your inventory with !inventory.')
        await channel.send(session_player.render())
        await channel.send('Your inventory is organised into rows, and each as several slots for storing cards. ' +
                           'As a new player, you only have 1 row.')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await pinput.ask_loop('Pull it up with !select 1.', ['!select 1'])
        # Send row render
        session_row = session_player.get_row(0)
        await channel.send(session_row.render())
        await channel.send('As you can see, you only have 1 card in this row. Each row can have a maximum of 12 cards. ' +
                           'In the future, you can quickly pull up a row at any time with !row <index>.')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await pinput.ask_loop('Now, pull up your first card with !select 1.', ['!select 1'])
        # Send card render
        session_card = session_row.get_card(0)
        await channel.send(session_card.render())
        await channel.send('As you can see, Each card has a Name, a Rarity(Top right), a description, ' +
                           'and resources(on the bottom).')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await channel.send('This card can store money, of which it has 0 out of a maximum of 50.')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await channel.send('Cards do a wide variety of things: produce all sorts of resources, boost the production ' +
                           'of other cards, convert between resources, and even form complex card-machines.\n' +
                           'This card, however, just produces money when you use it.')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await channel.send('Each card either does these things passively, when activated with !use, or both.')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await pinput.ask_loop('To "use" a card, Type !use. Try it now.', ['!use'], 'Type !use to use this card.')
        # Use card, re-render
        await session_card.use(message)
        await channel.send(session_card.render())
        await channel.send('Look. Now you have 1 money.')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await pinput.ask_loop('Next, check out the shop menu. Type !shop.',
                       ['!shop'],
                       'Please pull up the shop menu with !shop.')
        # Send shop menu render
        await channel.send(session_player.get_shop_menu_render())

        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await pinput.ask_loop('Here you will see all the shops you can buy cards from. '
                              'For now, you only have one unlocked. Select it with !select 1.',
                              ['select 1'],
                              'Select the shop with !select 1.')
        # Send shop render
        session_shop = session_player.get_unlocked_shops()[0]
        await channel.send(session_shop.render())
        await channel.send('That\'s a lot of information. As you can see, the seller has several cards for sale.')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await channel.send('When you buy a card, its cost is automatically deducted from cards in your inventory. ' +
                           'Since you only have 1 money, you can\'t afford any of these cards just yet.')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        await pinput.ask_loop('Lets examine a card for sale. Type !select 5.', ['!select 5'])

        await channel.send('This card has rarity EPIC -- quite a bit more powerful (and expensive) than what you have. ' +
                           'With enough patience, planning, and teamwork, ' +
                           'you will be able to fill your inventory with cards like this.')
        await asyncio.sleep(DEFAULT_MESSAGE_DELAY)
        channel.send('That should be enough for you to learn the ropes. Feel free to ask around for help, ' +
                     'and type !help to show the command list. Good luck!')
    except asyncio.TimeoutError:
        await channel.send(f'Aborting Tutorial for {session_player.get_name()}. Restart it at any time with !tutorial.')
