from config import PASSWORD
from sqlalchemy import create_engine


def get_id_list():
    engine = create_engine(f"postgresql+psycopg2://bot_vk:{PASSWORD}@localhost:5432/bot_vk")
    cursor = engine.connect()
    k = cursor.execute(f"select user_id from users ").fetchall()
    id_list = [x[0] for x in k]
    return id_list


def insert_db(table, column, values):
    engine = create_engine(f"postgresql+psycopg2://bot_vk:{PASSWORD}@localhost:5432/bot_vk")
    cursor = engine.connect()
    cursor.execute(f"insert into {table} ({column}) values ({values})")


def get_user_id(user_id):
    engine = create_engine(f"postgresql+psycopg2://bot_vk:{PASSWORD}@localhost:5432/bot_vk")
    cursor = engine.connect()
    u_id = cursor.execute(f"select id from users where user_id = {user_id}").fetchone()
    u_id = u_id[0]
    return u_id

