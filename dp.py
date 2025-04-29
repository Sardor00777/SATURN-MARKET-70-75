import asyncpg
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "mybotdb")
DB_USER = os.getenv("DB_USER", "botuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_HOST = os.getenv("DB_HOST", "localhost")

pool = None

async def init_pool():
    global pool
    pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        min_size=5,
        max_size=20
    )

@asynccontextmanager
async def get_connection():
    async with pool.acquire() as conn:
        yield conn

async def create_dp():
    try:
        async with get_connection() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE,
                    ism TEXT NOT NULL,
                    tel_nomer TEXT NOT NULL,
                    yosh INTEGER NOT NULL,
                    qayerliki TEXT NOT NULL,
                    ish_joyi TEXT NOT NULL
                )
            """)
    except asyncpg.PostgresError as e:
        print(f"Database creation error: {e}")
        raise

async def save_user(user_data: dict, telegram_id: int):
    try:
        async with get_connection() as conn:
            await conn.execute("""
                INSERT INTO users (telegram_id, ism, tel_nomer, yosh, qayerliki, ish_joyi)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, telegram_id, user_data['ism'], user_data['tel_nomer'], 
                int(user_data['yosh']), user_data['qayerliki'], user_data['ish_joyi'])
    except asyncpg.UniqueViolationError:
        raise ValueError("Bu Telegram ID bilan foydalanuvchi allaqachon ro‘yxatdan o‘tgan.")
    except asyncpg.PostgresError as e:
        print(f"Database save error: {e}")
        raise