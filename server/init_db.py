from database import engine, Base, get_raw_connection
from models import *  # register models with Base
from auth import AuthService

# Create tables
Base.metadata.create_all(bind=engine)

# Insert default users if they don't exist
conn = get_raw_connection()
cur = conn.cursor()
try:
    cur.execute("SELECT COUNT(1) as cnt FROM users")
    row = cur.fetchone()
    if not row or row['cnt'] == 0:
        # Register default users
        AuthService.register_user('admin', 'password123', 'admin')
        AuthService.register_user('manager', 'password123', 'manager')
        AuthService.register_user('operator', 'password123', 'operator')
        print('Default users created')
    else:
        print('Users already present')
finally:
    cur.close()
    conn.close()
