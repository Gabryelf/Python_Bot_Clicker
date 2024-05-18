import sqlite3
from typing import List, Tuple

DATABASE_PATH = 'database.db'


def init_db():
  conn = sqlite3.connect(DATABASE_PATH)
  cursor = conn.cursor()
  # Создаем таблицу, если она еще не существует, с дополнительным полем referrer_id
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS users (
      user_id INTEGER PRIMARY KEY,
      score REAL DEFAULT 0,
      energy INTEGER DEFAULT 50,
      token INTEGER DEFAULT 0,
      referrer_id INTEGER
  )
  ''')
  conn.commit()
  conn.close()

def get_all_user_ids():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM users"
                   )  # Получаем все уникальные user_id из базы данных
    user_ids = [row[0] for row in cursor.fetchall()
                ]  # Преобразуем результат запроса в список
    conn.close()
    return user_ids


async def get_top_users(n: int) -> List[Tuple[int, int]]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Выбираем первые n пользователей с наивысшими баллами, отсортированные по убыванию баллов
    cursor.execute(
        '''
        SELECT user_id, score
        FROM users
        ORDER BY score DESC
        LIMIT ?
    ''', (n, ))

    top_users = cursor.fetchall()

    conn.close()

    return top_users


def get_game_data(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT score, energy FROM users WHERE user_id = ?',
                   (user_id, ))
    data = cursor.fetchone()
    conn.close()
    if data is None:
        return 0.0, 50  # Возвращаем значения по умолчанию, если данные отсутствуют
    else:
        return data


def update_game_data(user_id, score, energy):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''
    INSERT OR REPLACE INTO users (user_id, score, energy) VALUES (?, ?, ?)
    ''', (user_id, score, energy))
    conn.commit()
    conn.close()


async def save_user_id(user_id: int, referrer_id: int = None) -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR IGNORE INTO users (user_id, score, energy, token, referrer_id) VALUES (?, ?, ?, ?, ?)',
        (user_id, 0.0, 50, 0, referrer_id))
    conn.commit()
    conn.close()


def add_tokens(user_id: int, tokens: int):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET token = token + ? WHERE user_id = ?',
                   (tokens, user_id))
    conn.commit()
    conn.close()

