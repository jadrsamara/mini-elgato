import os
import sqlite3

def connect_db(guild_id, db_name):

    """
    The function: "connect_db" returns you a connection to the database you need.

    :param guild_id: server guild id
    :param db_name: database name
    :return: sqlite connection object
    """

    isExist = os.path.exists(f'databases/{str(db_name)}/')
    if not isExist:
        os.makedirs(f'databases/{str(db_name)}/')

    file = open(f'databases/{str(db_name)}/{str(guild_id)}.db', "a")
    file.close()

    connection = sqlite3.connect(f'databases/{str(db_name)}/{str(guild_id)}.db')
    init_db(connection, db_name)
    
    return connection


def init_db(connection, db_name):

    if db_name.__eq__('list'):
        db_cursor = connection.cursor()
        db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS list (
                item_name TEXT,
                item_name_lower TEXT,
                user_name TEXT, 
                PRIMARY KEY (item_name_lower, user_name)
            );
        """)
        connection.commit()

    if db_name.__eq__('user_theme_song_permissions'):
        db_cursor = connection.cursor()
        db_cursor.execute("CREATE TABLE IF NOT EXISTS user_theme_song_permissions(id text PRIMARY KEY, permit text);")
        connection.commit()

    if db_name.__eq__('role_theme_song_permissions'):
        db_cursor = connection.cursor()
        db_cursor.execute("CREATE TABLE IF NOT EXISTS role_theme_song_permissions(role text PRIMARY KEY);")
        connection.commit()

    if db_name.__eq__('user_theme_songs'):
        db_cursor = connection.cursor()
        db_cursor.execute("CREATE TABLE IF NOT EXISTS user_theme_songs(id text PRIMARY KEY, url text, options text);")
        connection.commit()