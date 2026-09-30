from database import get_db_connection, init_db
init_db()
conn = get_db_connection()
tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)
conn.close()
