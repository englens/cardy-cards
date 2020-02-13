import discord
import asyncio

"""
Module Description:
    Utility functions regarding the discord bot.
"""


async def ask_loop(client: discord.Client, message: discord.Message, question: str, responses: list,
                   restated_question: str = None, tries: int = -1,
                   timeout: int = 60, case_sensitive=False):
    """
    Asks for a response. Will keep asking until a correct response is given, the message times out,
    or the user runs out of tries.
    Parameters:
        client: Discord client (from main)
        message: Discord Message from the player in the correct channel.
        question: The question to ask.
        restated_question: A (shortened) form when repeating the question.
        tries: How many times to try asking before giving up. If set to -1, will try forever.
        timeout: How long to wait before giving up. In seconds.
        responses: List of valid responses.
        case_sensitive: if no, all responses are converted to lowercase.
    """
    await message.channel.send(question)

    def check(m: discord.Message):
        return m.author == message.author and m.channel == message.channel

    if restated_question is None:
        restated_question = question
    while 1:
        msg = await client.wait_for('message', check=check, timeout=timeout)
        if case_sensitive:
            if msg.content in responses:
                return msg.content
        else:
            if msg.content.lower() in responses:
                return msg.content
        tries -= 1
        if tries == 0:
            raise asyncio.TimeoutError('Out of tries')
        await message.channel.send(restated_question)


async def yes_or_no(client: discord.Client, message: discord.Message, question: str,
                    restated_question: str = None, tries: int = -1, timeout: int = 60):
    """Special case of ask_loop, to ask a yes or no question. Do not include the (y/n) in the message."""
    question += ' (y/n)'
    if restated_question is not None:
        restated_question += ' (y/n)'
    yeses = ['yes', 'y', 'yep', 'ye', 'yep', 'yeet']
    nos = ['no', 'n', 'nope', 'nada']
    response = await ask_loop(client, message, question, yeses+nos, restated_question, tries, timeout)
    if response in yeses:
        return 'yes'
    return 'no'


async def player_input(client: discord.Client, message: discord.Message, question: str, timeout: int = 60):
    """Asks for a response to given question."""
    def check(m):
        return m.channel == message.channel and m.author == message.author
    await message.channel.send(question)
    msg = await client.wait_for('message', check=check, timeout=timeout)
    return msg.content


class PInput:
    """Stores message and client to reduce repetition when calling other bot util commands
        Provides methods wrapping other functions using given PInput information."""
    def __init__(self, client, message):
        self.client = client
        self.message = message

    async def yes_or_no(self, question: str, restated_question: str = None, tries: int = -1, timeout: int = 60):
        return await yes_or_no(self.client, self.message, question, restated_question, tries, timeout)

    async def player_input(self, question: str, timeout: int = 60):
        return await player_input(self.client, self.message, question, timeout)

    async def ask_loop(self, question: str, responses: list, restated_question: str = None, tries: int = -1,
                       timeout: int = 60, case_sensitive=False):
        return await ask_loop(self.client, self.message, question, responses,
                              restated_question, tries, timeout, case_sensitive)
