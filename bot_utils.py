import discord
import asyncio


async def ask_loop(message: discord.Message, question: str, responses: list,
                   restated_question: str = None, tries: int = -1,
                   timeout: int = 60, case_sensitive=False) -> str:
    """
    Asks for a response. Will keep asking until a correct response is given, the message times out,
    or the user runs out of tries.
    Parameters:
        message: Discord Message from the player in the correct channel.
        question: The question to ask.
        restated_question: A (shortened) form when repeating the question.
        tries: How many times to try asking before giving up. If set to -1, will try forever.
        timeout: How long to wait before giving up. In seconds.
        responses: List of valid responses.
        case_sensitive: if no, all responses are converted to lowercase.
    """
    message.channel.send(question)

    def check(m: discord.Message):
        return m.author == message.author and m.channel == message.channel

    if restated_question is None:
        restated_question = question
    while 1:
        msg = await message.channel.wait_for('message', check=check, timeout=timeout)
        if case_sensitive:
            if msg.content in responses:
                return msg.content
        else:
            if msg.content.lower() in responses:
                return msg.content
        tries -= 1
        if tries == 0:
            raise asyncio.TimeoutError('Out of tries')
        message.channel.send(restated_question)


async def yes_or_no(message: discord.Message, question: str,
                    restated_question: str = None, tries: int = -1, timeout: int = 60):
    """Special case of ask_loop, to ask a yes or no question. Do not include the (y/n) in the message."""
    question += ' (y/n)'
    restated_question += ' (y/n)'
    yeses = ['yes', 'y', 'yep', 'ye', 'yep', 'yeet']
    nos = ['no', 'n', 'nope', 'nada']
    response = await ask_loop(message, question, yeses+nos, restated_question, tries, timeout)
    if response in yeses:
        return 'yes'
    return 'no'


async def player_input(message: discord.Message, question: str, timeout: int = 60):
    """Asks for a response to given question."""
    def check(m):
        return m.channel == message.channel and m.author == message.author
    return message.channel.wait_for(question, check=check, timeout=timeout)
