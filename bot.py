import asyncio
from aiogram import Router, Bot, Dispatcher
from aiogram.types import Message, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import sqlite3
from typing import List, Tuple


DATABASE_PATH = 'database.db'

router = Router()
API_TOKEN = "6778725238:AAHKDzpjp6Dckq6yEH5DkDMOo1JtG8DkL0s"

url_ngrok = "https://8855-46-148-176-30.ngrok-free.app"
url_ref = "https://t.me/CookiesClickerGameBot"

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


init_db()  # Вызываем функцию инициализации базы данны

def get_all_user_ids():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM users")  # Получаем все уникальные user_id из базы данных
    user_ids = [row[0] for row in cursor.fetchall()]  # Преобразуем результат запроса в список
    conn.close()
    return user_ids


async def get_top_users(n: int) -> List[Tuple[int, int]]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Выбираем первые n пользователей с наивысшими баллами, отсортированные по убыванию баллов
    cursor.execute('''
        SELECT user_id, score
        FROM users
        ORDER BY score DESC
        LIMIT ?
    ''', (n,))

    top_users = cursor.fetchall()

    conn.close()

    return top_users


def get_game_data(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT score, energy FROM users WHERE user_id = ?', (user_id,))
    data = cursor.fetchone()
    conn.close()
    if data is None:
        return 0.0, 50  # Возвращаем значения по умолчанию, если данные отсутствуют
    else:
        return data

def update_game_data(user_id, score, energy):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO users (user_id, score, energy) VALUES (?, ?, ?)
    ''', (user_id, score, energy))
    conn.commit()
    conn.close()

async def save_user_id(user_id: int, referrer_id: int = None) -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, score, energy, token, referrer_id) VALUES (?, ?, ?, ?, ?)',
                   (user_id, 0.0, 50, 0, referrer_id))
    conn.commit()
    conn.close()

def add_tokens(user_id: int, tokens: int):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET token = token + ? WHERE user_id = ?', (tokens, user_id))
    conn.commit()
    conn.close()


def web_app_builder(user_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    web_app_url = f"{url_ngrok}?user_id={user_id}"
    # Выводим web_app_url в консоль
    print("Web App URL:", web_app_url)
    builder.button(text="ClickerGame!", web_app=WebAppInfo(url=web_app_url))

    return builder.as_markup()

async def get_user_id(message: Message):
    user_id = message.from_user.id
    return user_id


@router.message(CommandStart())
async def start(message: Message) -> None:
    # Разделяем текст сообщения на части по пробелу
    args = message.text.split()
    # Проверяем, есть ли аргументы после команды /start
    referrer_id = args[1] if len(args) > 1 else None

    new_user_id = message.from_user.id
    if referrer_id:
        # Пользователь перешел по реферальной ссылке
        try:
            # Преобразуем referrer_id в целое число
            referrer_id = int(referrer_id)
            await save_user_id(new_user_id, referrer_id=referrer_id)
            # Начисляем токены рефереру и новому пользователю
            add_tokens(referrer_id, 5)
            add_tokens(new_user_id, 5)
        except ValueError:
            # Если referrer_id не является целым числом, обрабатываем ошибку
            print(f"Invalid referrer_id: {referrer_id}")
    else:
        # Обычная регистрация без реферальной ссылки
        await save_user_id(new_user_id)

    # Отправка приветственного сообщения и кнопки для входа в игру
    await message.reply(f"Hello! Your user_id is {new_user_id}.", reply_markup=web_app_builder(new_user_id))



async def main() -> None:
    bot = Bot(API_TOKEN)

    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
