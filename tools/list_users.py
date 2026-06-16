import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from server.database import get_raw_connection, is_sqlite

conn = get_raw_connection()
cur = conn.cursor()
try:
    try:
        cur.execute("SELECT user_id, username, password_hash, role, created_at FROM users")
    except Exception as e:
        print('Query failed:', e)
        raise
    rows = cur.fetchall()
    if not rows:
        print('No users found')
    for r in rows:
        print(r)
finally:
    cur.close()
    conn.close()
