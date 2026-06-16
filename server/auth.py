"""
Authentication service with bcrypt password hashing.
"""
import bcrypt
import sqlite3
from server.database import get_raw_connection, is_sqlite, RealDictCursor

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Generate bcrypt hash with salt."""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except (ValueError, TypeError):
            return False

    @staticmethod
    def authenticate(username: str, password: str):
        """Authenticate user and return user data if successful."""
        conn = get_raw_connection()
        # For SQLite use default cursor; for Postgres use RealDictCursor if available
        if is_sqlite() or RealDictCursor is None:
            cursor = conn.cursor()
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            query = None
            params = (username,)
            if is_sqlite():
                query = "SELECT user_id, username, password_hash, role FROM users WHERE username = ?"
            else:
                query = "SELECT user_id, username, password_hash, role FROM users WHERE username = %s"

            try:
                cursor.execute(query, params)
            except sqlite3.OperationalError as e:
                msg = str(e)
                if is_sqlite() and ('near "%"' in msg or '%s' in query):
                    q2 = query.replace('%s', '?')
                    cursor.execute(q2, params)
                else:
                    raise
            user = cursor.fetchone()
            if user and AuthService.verify_password(password, user['password_hash']):
                return {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'role': user['role']
                }
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def register_user(username: str, password: str, role: str = 'operator'):
        """Register new user with hashed password."""
        conn = get_raw_connection()
        cursor = conn.cursor()
        try:
            password_hash = AuthService.hash_password(password)
            if is_sqlite():
                try:
                    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash, role))
                except sqlite3.OperationalError as e:
                    msg = str(e)
                    if 'near "%"' in msg:
                        q2 = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
                        cursor.execute(q2, (username, password_hash, role))
                    else:
                        raise
                user_id = cursor.lastrowid
            else:
                try:
                    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) RETURNING user_id", (username, password_hash, role))
                    user_id = cursor.fetchone()[0]
                except sqlite3.OperationalError:
                    # fallback: replace %s -> ? for sqlite
                    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash, role))
                    user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
