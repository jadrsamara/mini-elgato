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
    description = "El Gato Singer 🎤🐈 Bot",
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

@bot.hybrid_command(name='sing', description='Plays a song for you')
async def sing(ctx):

    """
    tells you a randome lame (dad) joke.

    :return: sends a joke as a message to the same channel.
    """

    
@bot.hybrid_command(name='test')
async def test(ctx):
    """
    Test function
    """

    channel = discord.utils.get(ctx.guild.text_channels, name="bot-commands")
    channel_1 = discord.utils.get(ctx.guild.text_channels, name="new-members")
    channel_2 = discord.utils.get(ctx.guild.text_channels, name="assssssssfasfs")
    await channel.send(f"channel_1: {channel_1}\nchannel_2: {channel_2}")



"""
Music Player
"""

from youtube_dl import YoutubeDL
from queue import Queue
import asyncio
import nacl

guilds = {}
guild_song_names = {}
player_flag = {}
local_counter = 2
queue_cache = {}
queue_size = 20


@bot.hybrid_command(name='play', description='Play a song by name or url')
async def play(ctx, *, name):

    check_result = await check_voice_channel(ctx)
    if check_result == 'err':
        await ctx.send(content="You are not in a voice channel!", ephemeral=True)
        return

    global guilds, local_counter

    if not guilds.get(ctx.guild.id).full():

        new_name, options = check_options(name)

        video, source_ = await search(new_name)
        song_name = video['title']

        FFMPEG_OPTS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'+options,
            'options': '-vn -probesize 32 -analyzeduration 0'
        }
        # FFMPEG_OPTS = {
        #     'before_options': '',
        #     'options': ''
        # }
        # source = discord.FFmpegPCMAudio(source_, **FFMPEG_OPTS)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source_, **FFMPEG_OPTS))

        local_counter += 1
        new_q = guilds.get(ctx.guild.id)
        new_q.put(source)
        new_q_name = guild_song_names.get(ctx.guild.id)
        new_q_name.put(song_name)
        guilds.update({ctx.guild.id: new_q})
        guild_song_names.update({ctx.guild.id: new_q_name})

        voice_channel = ctx.author.voice.channel
        voice_client = voice_channel.guild.voice_client

        if not voice_client.is_playing():
            await player(ctx)
        else:
            await ctx.send(content=f'Enqueued **{song_name}**',
                           ephemeral=True)
    else:
        await ctx.send(content="Queue is full!", ephemeral=True)



def check_options(name):
    options = ''
    new_name = name.split('--')[0]

    ### Start ###

    if name.__contains__('--start '):
        start = name.split('--start ')[1].split('--')[0].strip()
        if start != '':
            options += ' -ss '+start

    if name.__contains__('--begin '):
        start = name.split('--begin ')[1].split('--')[0].strip()
        if start != '':
            options += '-ss '+start

    ### Finish ###

    if name.__contains__('--finish '):
        finish = name.split('--finish ')[1].split('--')[0].strip()
        if finish != '':
            options += ' -to '+finish

    if name.__contains__('--stop '):
        finish = name.split('--stop ')[1].split('--')[0].strip()
        if finish != '':
            options += ' -to '+finish

    if name.__contains__('--end '):
        finish = name.split('--end ')[1].split('--')[0].strip()
        if finish != '':
            options += ' -to '+finish

    ### Duration ###

    if name.__contains__('--for '):
        finish = name.split('--for ')[1].split('--')[0].strip()
        if finish != '':
            options += ' -t '+finish

    if name.__contains__('--duration '):
        finish = name.split('--duration ')[1].split('--')[0].strip()
        if finish != '':
            options += ' -t '+finish

    return new_name, options


async def check_voice_channel(ctx):
    try:
        voice_channel = ctx.author.voice.channel
    except AttributeError:
        return 'err'

    global guilds, local_counter, queue_cache

    voice_client = ctx.channel.guild.voice_client
    if voice_client is None:
        voice_client = await voice_channel.connect()
        guilds.update({ctx.guild.id: Queue(maxsize=queue_size)})
        guild_song_names.update({ctx.guild.id: Queue(maxsize=queue_size)})
        player_flag.update({ctx.guild.id: 0})

    elif (voice_client.channel != voice_channel) and (player_flag.get(
            ctx.guild.id) == 0):
        await ctx.voice_client.disconnect()
        voice_client = await voice_channel.connect()
    elif (voice_client.channel == voice_channel):
        do_nothing = 0
    else:
        await ctx.send(content="Bot is already in a voice channel",
                       ephemeral=True)
        return 'err'


async def search(query):
    if query.__contains__('youtube.com/shorts/'):
        query = query.replace('shorts/', 'watch?v=')
    with YoutubeDL({
            'format': 'bestaudio',
            'keepvideo': False,
            'noplaylist': 'True'
    }) as ydl:
        try:
            print(requests.get(query))
        except:
            info = ydl.extract_info(f"ytsearch:{query}",
                                    download=False)['entries'][0]
        else:
            info = ydl.extract_info(query, download=False)
    return (info, info['formats'][0]['url'])


async def player(ctx):
    global guilds
    voice_client = ctx.channel.guild.voice_client
    voice_channel = ctx.author.voice.channel
    try:
        voice_client = await voice_channel.connect()
    except Exception as e:
        print(e)
    global player_flag
    while not guilds.get(ctx.guild.id).empty():
        player_flag.update({ctx.guild.id: 1})
        if not voice_client.is_playing():
            current_q = guilds.get(ctx.guild.id)
            song_name_q = guild_song_names.get(ctx.guild.id)

            song_to_be_played = current_q.get()
            await ctx.send(content=f'Playing **{song_name_q.get()}**',
                           ephemeral=False)
            voice_client.play(song_to_be_played)
            while voice_client.is_playing():
                await asyncio.sleep(1)

        player_flag.update({ctx.guild.id: 0})


@bot.hybrid_command(name='skip', description='Skip this song...')
async def skip(ctx):
    voice_client = ctx.channel.guild.voice_client

    try:
        voice_channel = ctx.author.voice.channel
    except AttributeError:
        await ctx.send(content="You are not in the same voice channel!",
                       ephemeral=True)
        return
    voice_client = ctx.channel.guild.voice_client
    if voice_client is None:
        await ctx.send(content="No music is playing.", ephemeral=True)
        return
    elif (voice_client.channel == voice_channel):
        do_nothing = 0
    else:
        await ctx.send(content="You are not in the same voice channel!",
                       ephemeral=True)
        return

    voice_client.stop()
    await ctx.send(content="Skipped", ephemeral=True)


@bot.hybrid_command(name='dc',
                    description='Disconnects from the voice channel.')
async def dc(ctx):
    await clear_queue(ctx, False)


@bot.hybrid_command(name='stop', description='Stopps the current queue.')
async def stop(ctx):
    await clear_queue(ctx, True)


async def clear_queue(ctx, stop_):
    voice_client = ctx.channel.guild.voice_client

    try:
        voice_channel = ctx.author.voice.channel
    except AttributeError:
        await ctx.send(content="You are not in the same voice channel!",
                       ephemeral=True)
        return
    voice_client = ctx.channel.guild.voice_client
    if voice_client is None:
        await ctx.send(content="No music is playing.", ephemeral=True)
        return
    elif (voice_client.channel == voice_channel):
        do_nothing = 0
    else:
        await ctx.send(content="You are not in the same voice channel!",
                       ephemeral=True)
        return

    with guilds.get(ctx.guild.id).mutex:
        guilds.get(ctx.guild.id).queue.clear()
    if not stop_:
        await ctx.voice_client.disconnect()
        await ctx.send(content="Disconnected", ephemeral=True)
    else:
        voice_client.stop()
        await ctx.send(content="Stopped", ephemeral=True)


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
        try:
            guilds.get(ctx.guild.id).empty()
        except AttributeError:
            guilds.update({ctx.guild.id: Queue(maxsize=queue_size)})
            guild_song_names.update(
                {ctx.guild.id: Queue(maxsize=queue_size)})
            player_flag.update({ctx.guild.id: 0})
    elif (voice_client.channel != voice_channel) and (
        (ctx.author in voice_client.channel.members) or
            (player_flag.get(ctx.guild.id) == 0)):
        await voice_client.move_to(voice_channel)
    # else:
    #     await ctx.send(content="Bot is already in a voice channel",
    #                    ephemeral=True)
    #     return

    source = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio('sing/'+song+'.mp3'))
    if not voice_client.is_playing():
        voice_client.play(source, after=None)
    if not str(ctx.message.type).__eq__('MessageType.default'):
        await ctx.send(content="I'm here!", ephemeral=True)

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

    # time.sleep(0.5)
    # add check if voice bot is present 

    if await come(ctx, 'drum_roll') != 'err':
    
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
        await message.edit(content=f'Choosen item for you is: **{result}**')


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
    result = f'{result[0]} - {result[1]}'

    # time.sleep(0.5)
    # add check if voice bot is present

    if await come(ctx, 'drum_roll') != 'err':
    
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
        await message.edit(content=f'Choosen item for you is: **{result}**')


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
        item_list = f'Item list:\n```{1} - {list_of_items[0][0]} - {list_of_items[0][1]}'
        for i, value in enumerate(list_of_items):
            if i == 0:
                continue
            item_list+=f'\n{i+1} - {value[0]} - {value[1]}'
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


# * * * * * * * * * * * RUN BOT * * * * * * * * * * * *

@bot.command()
async def sync(ctx):
    if ctx.message.author.mention.__eq__('<@465981081456214019>'):
        _sync = await ctx.bot.tree.sync()
        await ctx.send(f'Synced {len(_sync)} commands!')
    else:
        await ctx.send(f'You don\'t have permission.')



my_secret = os.environ['BOT_KEY']
bot.run(my_secret)