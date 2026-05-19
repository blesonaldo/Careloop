import asyncio
from app.database import engine

async def migrate():
    async with engine.connect() as conn:
        try:
            await conn.exec_driver_sql("ALTER TABLE users ADD COLUMN avatar TEXT")
            print("Added avatar column")
        except Exception as e:
            print(f"avatar: {e}")
        try:
            await conn.exec_driver_sql("ALTER TABLE users ADD COLUMN preferred_currency VARCHAR(10) DEFAULT 'USD'")
            print("Added preferred_currency column")
        except Exception as e:
            print(f"preferred_currency: {e}")
        await conn.commit()

asyncio.run(migrate())
