"""
Authentication service with bcrypt password hashing.
SQLite version.
"""
import bcrypt
import sqlite3
from server.database import get_raw_connection

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except ValueError:
            # Возвращаем False, если хэш имеет некорректный формат
            return False

    @staticmethod
    def authenticate(username: str, password: str):
        conn = get_raw_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, username, password_hash, role FROM users WHERE username = ?",
                (username,)
            )
            user = cursor.fetchone()
            if user and AuthService.verify_password(password, user['password_hash']):
                return {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'role': user['role']
                }
            return None
        finally:
            conn.close()

    @staticmethod
    def register_user(username: str, password: str, role: str = 'operator'):
        conn = get_raw_connection()
        try:
            cursor = conn.cursor()
            password_hash = AuthService.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    