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
        knock_outs BIGINT NOT NULL
        )''')

    c.execute('''CREATE TABLE snowmen (
        user_id BIGINT NOT NULL PRIMARY KEY,
        bottom_radius BIGINT NOT NULL,
        middle_radius BIGINT NOT NULL,
        top_radius BIGINT NOT NULL,
        arm_length BIGINT NOT NULL,
        num_buttons BIGINT NOT NULL,
        p_hat VARCHAR(6) NOT NULL,
        s_hat VARCHAR(6) NOT NULL,
        p_scarf VARCHAR(6) NOT NULL,
        s_scarf VARCHAR(6) NOT NULL,
        bg_colour VARCHAR(6) NOT NULL
        )''')
    conn.commit()

except db.errors.ProgrammingError:
    pass

def save_snowman(user_id: int, data: list):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    try:
        c.execute(f"UPDATE snowmen SET bottom_radius = {data[0]}, middle_radius = {data[1]}, top_radius = {data[2]}, arm_length = {data[3]}, num_buttons = {data[4]}, p_hat = {data[5]}, s_hat = {data[6]}, p_scarf = {data[7]}, s_scarf = {data[8]}, bg_colour = {data[9]} WHERE user_id = {user_id}")
    except:
        c.execute(f"INSERT INTO snowmen (user_id, bottom_radius, middle_radius, top_radius, arm_length, num_buttons, p_hat, s_hat, p_scarf, s_scarf, bg_colour) VALUES ({user_id}, {data[0]}, {data[1]}, {data[2]}, {data[3]}, {data[4]}, {data[5]}, {data[6]}, {data[7]}, {data[8]}, {data[9]})")
    conn.commit()
    c.close()
    conn.close()

def get_snowman(user_id: int):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM snowmen WHERE user_id = {user_id}")
        data = c.fetchone()[1:]
    except:
        data = None
    return data

def change_stats(guild_id: int, user_id: int, status: int):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM snowball_leaderboards WHERE guild_id = {guild_id} AND user_id = {user_id}")
        data = list(c.fetchone()[1:])
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
            c.execute(f"UPDATE snowball_leaderboards SET misses = {data[3]} WHERE guild_id = {guild_id} AND user_id = {user_id}")
        elif status == 2:
            data[4] += 1
            c.execute(f"UPDATE snowball_leaderboards SET knock_outs = {data[4]} WHERE guild_id = {guild_id} AND user_id = {user_id}")
    conn.commit()
    c.close()
    conn.close()
    return

def get_stats(guild_id: int, user_id: int):
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

def get_leaderboard(guild_id: int):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM snowball_leaderboards WHERE guild_id = {guild_id} ORDER BY hits DESC, misses ASC, knock_outs ASC")
        data = np.array(c.fetchmany(10))[:, 2:].tolist()
    except:
        data = None

    c.close()
    conn.close()
    return data

c.close()
conn.close()