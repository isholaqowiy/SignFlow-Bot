import aiosqlite
from config import DB_NAME

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                file_path TEXT
            )
        ''')
        await db.commit()

async def register_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.commit()

async def save_sig_meta(user_id: int, title: str, path: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO signatures (user_id, title, file_path) VALUES (?, ?, ?)", (user_id, title, path))
        await db.commit()

async def get_user_sigs(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id, title, file_path FROM signatures WHERE user_id = ?", (user_id,)) as cursor:
            return [{"id": row[0], "title": row[1], "path": row[2]} for row in await cursor.fetchall()]

async def get_stats_meta():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c1, db.execute("SELECT COUNT(*) FROM signatures") as c2:
            u = (await c1.fetchone())[0]
            s = (await c2.fetchone())[0]
            return u, s

