import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from server.database import get_raw_connection
from server.auth import AuthService, is_sqlite

conn = get_raw_connection()
cur = conn.cursor()
try:
    try:
        cur.execute("SELECT username FROM users WHERE username = ?", ('admin',))
    except Exception:
        # try postgres placeholder
        cur.execute("SELECT username FROM users WHERE username = %s", ('admin',))
    row = cur.fetchone()
    if row:
        print('Admin already exists')
    else:
        uid = AuthService.register_user('admin', 'password123', 'admin')
        print('Created admin user id=', uid)
finally:
    cur.close()
    conn.close()
