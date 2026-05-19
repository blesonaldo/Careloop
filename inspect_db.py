import asyncio
from app.database import engine

async def inspect():
    async with engine.connect() as conn:
        tables = await conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        print("=== TABLES ===")
        for t in tables.fetchall():
            print(" ", t[0])
            cols = await conn.exec_driver_sql(f"PRAGMA table_info({t[0]})")
            for col in cols.fetchall():
                print(f"      {col[1]} ({col[2]})")

asyncio.run(inspect())
