# Jad Samara

from dotenv import load_dotenv

load_dotenv()

import os
import sqlite3
import requests
import database
import logger

# * * * * * * * * * *  BOT SETTINGS  * * * * * * * * * *

import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True

help_command = commands.DefaultHelpCommand(no_category = 'Commands')

bot = commands.Bot(
    command_prefix = commands.when_mentioned_or('='),
    description = "Mini El Gato Bot",
    help_command = help_command, 
    intents=intents
)

# * * * * * * * * * * EVENTS BELLOW * * * * * * * * * *

@bot.event
async def on_command(ctx):
    """
    Function to log when a real command is invoked.
    """
    logger.log_info(f'Command {ctx.command} was invoked by {ctx.message.author}', ctx)


@bot.event
async def on_command_error(ctx, error):
    """
    Function to log when a command has an exception.
    """
    logger.log_error(error, ctx)


@bot.event
async def on_command_completion(ctx):
    """
    Function to log when a real command has finished executing.
    """
    logger.log_info(f'Command {ctx.command} has finished for user {ctx.message.author}', ctx)


# * * * * * * * * * COMMAND FUNCTIONS * * * * * * * * *

    
# @bot.hybrid_command(name='test')
# async def test(ctx):
#     """
#     Test function
#     """

#     channel = discord.utils.get(ctx.guild.text_channels, name="bot-commands")
#     channel_1 = discord.utils.get(ctx.guild.text_channels, name="new-members")
#     channel_2 = discord.utils.get(ctx.guild.text_channels, name="assssssssfasfs")
#     await channel.send(f"channel_1: {channel_1}\nchannel_2: {channel_2}")


"""
Voice Player (No Queue)
"""


@bot.hybrid_command(name='come', description='Make the bot follow you.')
async def come(ctx, song='cute'):
    try:
        voice_channel = ctx.author.voice.channel
    except AttributeError:
        await ctx.send(content="You are not in the same voice channel!",
                       ephemeral=True)
        return 'err'

    voice_client = ctx.channel.guild.voice_client

    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif (voice_client.channel != voice_channel) and (ctx.author in voice_client.channel.members):
        await voice_client.move_to(voice_channel)

    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('sing/'+song+'.mp3'))
    if not voice_client.is_playing():
        voice_client.play(source, after=None)


@bot.hybrid_command(name='dc', description='Make the bot Disconnect.')
async def dc(ctx, from_='command'):
    voice_client = ctx.channel.guild.voice_client

    try:
        voice_channel = ctx.author.voice.channel
    except AttributeError:
        await ctx.send(content="You are not in the same voice channel!", ephemeral=True)
        return
    
    voice_client = ctx.channel.guild.voice_client

    if voice_client is None:
        return
    elif (voice_client.channel == voice_channel):
        pass
    else:
        await ctx.send(content="You are not in the same voice channel!", ephemeral=True)
        return

    if from_.startswith('list_pick'):
        import asyncio
        while voice_client.is_playing():
            await asyncio.sleep(1)
    
    voice_client.stop()
    await ctx.voice_client.disconnect()

    if from_ == 'command':
        await ctx.send(content="Disconnected", ephemeral=True)


async def wait_until_voice_ready(ctx):
    import asyncio

    voice_client = ctx.channel.guild.voice_client

    try:
        voice_channel = ctx.author.voice.channel
    except AttributeError:
        await ctx.send(content="You are not in the same voice channel!", ephemeral=True)
        return
    
    for i in range(15):
        if voice_client is not None:
            break
        await asyncio.sleep(0.25)

    while not voice_client.is_playing():
        await asyncio.sleep(0.25)

    return


"""
List Picker commands
"""

@bot.hybrid_command(name='list_pick', description='Pick a random item from the items list')
async def list_pick(ctx):

    """
    picks an item from a list that you create.

    :param string: string (optional)
    :return: sends multiple messages as a suspense, then sends the random number.
    """

    import time
    import random

    db_connection = database.connect_db(guild_id=ctx.guild.id, db_name='list')
    db_cursor = db_connection.cursor()

    res = db_cursor.execute("SELECT rowid, item_name, user_name FROM list;")
    list_of_items = res.fetchall()

    if (len(list_of_items) == 0):
        logger.log_info(f'List is empty.', ctx)
        await ctx.send(f'List is empty.')
    
    result = list_of_items[random.randint(0, len(list_of_items)-1)]
    result = f'{result[0]} - {result[1]} - {result[2]}'

    if await come(ctx, 'drum_roll') != 'err':

        await wait_until_voice_ready(ctx)
    
        message = await ctx.reply(content='🥁')
        time.sleep(1)
        await message.edit(content='🥁 🥁 ')
        time.sleep(1)
        await message.edit(content='🥁 🥁 🥁 ')
        time.sleep(1)
        await message.edit(content='🥁 🥁 🥁 🥁 ')
        time.sleep(1)
        await message.edit(content='🥁 🥁 🥁 🥁 🥁 ')
        time.sleep(1)
        await message.edit(content='🥁 🥁 🥁 🥁 🥁 🥁 ')
        time.sleep(1)
        await message.edit(content=f'Choosen item for you is: **{result}**')

    await dc(ctx, from_='list_pick')


@bot.hybrid_command(name='list_pick_sheet', description='Pick a random item from the items list')
async def list_pick_sheet(ctx):

    """
    picks an item from a list from google sheet movie list.

    :param string: string (optional)
    :return: sends multiple messages as a suspense, then sends the random number.
    """

    import time
    import random
    import requests

    url = 'https://script.google.com/macros/s/AKfycbzKnfnuRSs1SszTi4BJJJC8czAXJ8ZrJyAvz6tiapxfIun-NjLXW3K89Dvmi7LiviZq/exec'
    response = requests.get(url)
    list_of_items = list(response.json())

    if (len(list_of_items) == 0):
        logger.log_info(f'List is empty.', ctx)
        await ctx.send(f'List is empty.')
    
    result = list_of_items[random.randint(0, len(list_of_items)-1)]
    result = f'{result[1]} - {result[0]}'

    if await come(ctx, 'drum_roll') != 'err':

        await wait_until_voice_ready(ctx)
    
        message = await ctx.reply(content='🥁')
        time.sleep(1)
        await message.edit(content='🥁 🥁 ')
        time.sleep(1)
        await message.edit(content='🥁 🥁 🥁 ')
        time.sleep(1)
        await message.edit(content='🥁 🥁 🥁 🥁 ')
        time.sleep(1)
        await message.edit(content='🥁 🥁 🥁 🥁 🥁 ')
        time.sleep(1)
        await message.edit(content='🥁 🥁 🥁 🥁 🥁 🥁 ')
        time.sleep(1)
        await message.edit(content=f'Choosen item for you is: **{result}**')

    await dc(ctx, from_='list_pick_sheet')


@bot.hybrid_command(name='list_add', description='Add an to the item list in order to pick a random item')
async def item_add(ctx, *, item_name):

    """
    adds an item to the items list

    :param item_name: string
    :return: confirmation if the item has been added or not
    """

    db_connection = database.connect_db(guild_id=ctx.guild.id, db_name='list')
    db_cursor = db_connection.cursor()

    user_name = ctx.author

    try:
        res = db_cursor.execute(f'INSERT INTO list (item_name, item_name_lower, user_name) VALUES ("{item_name}", "{item_name.lower()}", "{user_name}")')
        db_connection.commit()
    except sqlite3.IntegrityError:
        logger.log_info(f'Item already added by you.', ctx)
        await ctx.send(f'Item already added by you.')
        return
    
    logger.log_info(f'Item Added: {item_name} - {user_name}', ctx)
    await ctx.send(f'Item Added!\n```{item_name} - {user_name}```')
    await list_view(ctx)


@bot.hybrid_command(name='list_clear', description='Clear the items list')
async def list_clear(ctx):

    """
    cleares the items list

    :return: confirmation if the list has been cleared or not
    """

    db_connection = database.connect_db(guild_id=ctx.guild.id, db_name='list')
    db_cursor = db_connection.cursor()

    db_cursor.execute("DROP TABLE IF EXISTS list;")
    db_connection.commit()

    logger.log_info(f'List list have been cleared.', ctx)
    await ctx.send(f'List have been cleared.')


@bot.hybrid_command(name='list_view', description='View the items list')
async def list_view(ctx):

    """
    view the items list

    :return: current items list
    """

    db_connection = database.connect_db(guild_id=ctx.guild.id, db_name='list')
    db_cursor = db_connection.cursor()

    res = db_cursor.execute("SELECT rowid, item_name, user_name FROM list;")
    fetch = res.fetchall()

    print(fetch)

    if (len(fetch) == 0):
        logger.log_info(f'List is empty.', ctx)
        await ctx.send(f'List is empty.')
    else:
        item_list = f'Item list:\n```{fetch[0][0]} - {fetch[0][1]} - {fetch[0][2]}'
        for i in range(1, len(fetch)):
            item_list+=f'\n{fetch[i][0]} - {fetch[i][1]} - {fetch[i][2]}'
        item_list+='```'
        
        logger.log_info(fetch, ctx)
        await ctx.send(item_list)


@bot.hybrid_command(name='list_view_sheet', description='View the items list')
async def list_view_sheet(ctx):

    """
    view the items list from google sheet

    :return: current items list from google sheet
    """

    import requests

    url = 'https://script.google.com/macros/s/AKfycbzKnfnuRSs1SszTi4BJJJC8czAXJ8ZrJyAvz6tiapxfIun-NjLXW3K89Dvmi7LiviZq/exec'
    response = requests.get(url)
    list_of_items = list(response.json())

    if (len(list_of_items) == 0):
        logger.log_info(f'List is empty.', ctx)
        await ctx.send(f'List is empty.')
    else:
        item_list = f'Item list:\n```{1} - {list_of_items[0][1]} - {list_of_items[0][0]}'
        for i, value in enumerate(list_of_items):
            if i == 0:
                continue
            item_list+=f'\n{i+1} - {value[1]} - {value[0]}'
        item_list+='```'
        await ctx.send(item_list)


@bot.hybrid_command(name='list_delete', description='Clear the an item from the items list')
async def list_delete(ctx, *, num):

    """
    remove an item from the items list

    :return: confirmation if the item has been deleted or not
    """

    import re

    numbers = re.findall('[0-9]+', num)

    db_connection = database.connect_db(guild_id=ctx.guild.id, db_name='list')
    db_cursor = db_connection.cursor()

    res = db_cursor.execute(f'SELECT user_name FROM list WHERE rowid = {numbers[0]};')
    fetch = res.fetchone()

    if (fetch is None):
        logger.log_info(f'Item picked is not on the list.', ctx)
        await ctx.send(f'Item picked is not on the list.')
    elif fetch[0].__eq__(ctx.author):
        db_cursor.execute(f"""
            DELETE FROM list
            WHERE rowid = {numbers[0]};
        """)

        db_cursor.execute("""
            UPDATE list
            SET rowid = (SELECT rank FROM (SELECT rowid,(SELECT count()+1 FROM (SELECT DISTINCT rowid FROM list AS t WHERE t.rowid < list.rowid)) rank FROM list) AS sub
            WHERE sub.rowid = list.rowid
            );
        """)
        
        db_connection.commit()

        logger.log_info(f'List has been deleted.', ctx)
        await ctx.send(f'List has been deleted.')
        await list_view(ctx)
    else:
        logger.log_info(f'You can only delete items picked by you. [{fetch[0]} != {ctx.author}]', ctx)
        await ctx.send(f'You can only delete items picked by you.')


"""
Random commands
"""

@bot.hybrid_command(name='joke', description='Tells a lame Joke')
async def joke(ctx):

    """
    tells you a randome lame (dad) joke.

    :return: sends a joke as a message to the same channel.
    """

    response = requests.get("https://icanhazdadjoke.com/",
                            headers={
                                "Accept": "application/json",
                                "User-Agent": "El Gato - Discord bot"
                            })
    await ctx.reply(response.json()['joke'])
    logger.log_info(f'User was given this lame joke: {response.json()["joke"]}', ctx)


@bot.hybrid_command(name='bored', description='I\'m board, what should I do?')
async def bored(ctx):
    
    """
    tells you something to do when you're bored.

    :return: sends a suggestion as a message to the same channel.
    """

    response = requests.get("https://www.boredapi.com/api/activity",
                            headers={"User-Agent": "El Gato - Discord bot"})
    await ctx.reply(response.json()['activity'])
    logger.log_info(f'User was recommended this activity: {response.json()["activity"]}', ctx)


# * * * * * * * * * * * RUN BOT * * * * * * * * * * * *

@bot.command()
async def sync(ctx):
    if ctx.message.author.mention.__eq__('<@465981081456214019>'):
        _sync = await ctx.bot.tree.sync()
        await ctx.send(f'Synced {len(_sync)} commands!')
        logger.log_info('Commands synced!', ctx)
    else:
        await ctx.send(f'You don\'t have permission.')
        logger.log_info('User have no permission to sync commands', ctx)

@bot.command()
async def ping(ctx):

    """
    a way to make sure the bot is running. 

    :return: sends a message "pong" to the channel.
    """

    await ctx.send(f'Pong')
    logger.log_info('Pong', ctx)



my_secret = os.environ['BOT_KEY']
bot.run(my_secret)