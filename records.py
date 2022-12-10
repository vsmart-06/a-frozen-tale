import mysql.connector as db
import numpy as np
import os
import dotenv

dotenv.load_dotenv()

h = os.getenv("HOST")
u = os.getenv("USER")
p = os.getenv("PASSWORD")
d = os.getenv("DATABASE")

conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
)
c = conn.cursor()

try:
    c.execute('''CREATE TABLE snowball_leaderboards (
        id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        guild_id BIGINT NOT NULL,
        user_id BIGINT NOT NULL,
        hits BIGINT NOT NULL,
        misses BIGINT NOT NULL,
        knock_outs BIGINT NOT NULL,
        )''')
    conn.commit()

except db.errors.ProgrammingError:
    pass

def change_stats(guild_id, user_id, status):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM snowball_leaderboards WHERE guild_id = {guild_id} AND user_id = {user_id}")
        data = c.fetchone()[1:]
    except:
        stats = [0, 0, 0]
        stats[status] = 1
        c.execute(f"INSERT INTO snowball_leaderboards (guild_id, user_id, hits, misses, knock_outs) VALUES ({guild_id}, {user_id}, {stats[0]}, {stats[1]}, {stats[2]})")
    else:
        if status == 0:
            data[2] += 1
            c.execute(f"UPDATE snowball_leaderboards SET hits = {data[2]} WHERE guild_id = {guild_id} AND user_id = {user_id}")
        elif status == 1:
            data[3] += 1
            c.execute(f"UPDATE snowball_leaderboards SET hits = {data[3]} WHERE guild_id = {guild_id} AND user_id = {user_id}")
        elif status == 2:
            data[4] += 1
            c.execute(f"UPDATE snowball_leaderboards SET hits = {data[4]} WHERE guild_id = {guild_id} AND user_id = {user_id}")
    conn.commit()
    c.close()
    conn.close()
    return

def get_stats(guild_id, user_id):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()

    try:
        c.execute(f"SELECT * FROM snowball_leaderboards WHERE guild_id = {guild_id} AND user_id = {user_id}")
        data = c.fetchone()[3:]
    except:
        data = None

    c.close()
    conn.close()
    return data

def get_leaderboard(guild_id):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM snowball_leaderboards WHERE guild_id = {guild_id} ORDER BY hits")
        data = np.array(c.fetchmany(10))[:, 2:].tolist()
    except:
        data = None

    c.close()
    conn.close()
    return data

c.close()
conn.close()