import sqlite3 as sq


async def db_start():
    conn = sq.connect('database.db')
    cur = conn.cursor()  # объект "cursor" для выполнения SQL-запросов и операций с базой данных
    cur.execute('''
    CREATE TABLE IF NOT EXISTS profile (
    user_id TEXT PRIMARY KEY, 
    area TEXT,
    route TEXT,
    type_road_deficiencies TEXT,
    photo_road_deficiencies TEXT,
    locate_road_deficiencies TEXT
    )
    ''')
    conn.commit()  # cохраняем изменения


async def create_profile(user_id):
    conn = sq.connect('database.db')
    cur = conn.cursor()
    user = cur.execute("SELECT 1 FROM profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO profile VALUES(?,?,?,?,?,?)", (user_id, '', '', '', '', ''))
        conn.commit()


async def edit_area(area, user_id):
    conn = sq.connect('database.db')
    cur = conn.cursor()
    cur.execute("UPDATE profile SET area == '{}' WHERE user_id == '{}'".format(
        area, user_id))
    conn.commit()



