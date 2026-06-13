import sqlite3
conn = sqlite3.connect('careloop.db')
cols = [d[1] for d in conn.execute('PRAGMA table_info(users)').fetchall()]
if 'avatar' not in cols:
    conn.execute('ALTER TABLE users ADD COLUMN avatar TEXT')
if 'preferred_currency' not in cols:
    conn.execute('ALTER TABLE users ADD COLUMN preferred_currency VARCHAR(10) DEFAULT "USD"')
conn.commit()
conn.close()
print('Done')
