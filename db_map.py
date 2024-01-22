import sqlite3 as sq


async def db_start():
    conn = sq.connect('database.db')
    cur = conn.cursor()  # объект "cursor" для выполнения SQL-запросов и операций с базой данных
    cur.execute('''
    CREATE TABLE IF NOT EXISTS profile (
    user_id TEXT PRIMARY KEY, 
    route TEXT,
    photo_road_deficiencies TEXT,
    longitude FLOAT,
    latitude FLOAT
    )
    ''')
    conn.commit()  # cохраняем изменения


async def create_profile(user_id):
    conn = sq.connect('database.db')
    cur = conn.cursor()
    user = cur.execute("SELECT 1 FROM profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO profile VALUES(?,?,?,?,?)", (user_id, '', '', '', ''))
        conn.commit()


async def edit_route(route, user_id):
    conn = sq.connect('database.db')
    cur = conn.cursor()
    cur.execute("UPDATE profile SET route == '{}' WHERE user_id == '{}'".format(
        route, user_id))
    conn.commit()


async def edit_location(longitude, latitude, user_id):
    conn = sq.connect('database.db')
    cur = conn.cursor()
    cur.execute("UPDATE profile SET longitude == '{}' WHERE user_id == '{}'".format(
        longitude, user_id))
    cur.execute("UPDATE profile SET latitude == '{}' WHERE user_id == '{}'".format(
        latitude, user_id))
    conn.commit()

