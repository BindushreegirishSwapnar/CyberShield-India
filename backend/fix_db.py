"""Re-initialize the database — run this once to create all tables."""
from database import init_db, get_db_connection, _add_new_tables
init_db()
_add_new_tables()
conn = get_db_connection()
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables created:", [t[0] for t in tables])
conn.close()
print("Database ready.")
