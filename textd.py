import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def verify():
    DATABASE_URL = "sqlite+aiosqlite:///./careloop.db"  
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        # For SQLite
        result = await conn.execute(text("PRAGMA table_info(users)"))
        rows = result.fetchall()
        columns = [row[1] for row in rows]
        print("Database columns:", columns)
        print("last_login_at in DB:", 'last_login_at' in columns)
    await engine.dispose()

asyncio.run(verify())