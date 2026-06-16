"""
SQL Repository implementations using raw psycopg2.
"""
from typing import List, Dict, Any, Optional
from server.repositories.base_repository import IComponentRepository, IOrderRepository, IUserRepository
from server.database import get_raw_connection, is_sqlite, RealDictCursor
import sqlite3


def _execute(cursor, query, params=None):
    """Execute query, and on SQLite retry by replacing Postgres placeholders "%s" with "?".
    This helps when code calls into SQL written for Postgres while running SQLite.
    """
    try:
        if params is None:
            return cursor.execute(query)
        return cursor.execute(query, params)
    except sqlite3.OperationalError as e:
        msg = str(e)
        if is_sqlite() and 'near "%"' in msg or is_sqlite() and '%s' in query:
            q2 = query.replace('%s', '?')
            return cursor.execute(q2, params or ())
        raise

class SqlComponentRepository(IComponentRepository):
    def _get_connection(self):
        return get_raw_connection()

    def create(self, data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if is_sqlite():
                _execute(cursor,
                    """
                    INSERT INTO components (category_id, component_name, brand, model, specifications, price, selling_price, quantity_in_stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (data['category_id'], data['component_name'], data['brand'], data['model'],
                     data.get('specifications'), data['price'], data['selling_price'], data.get('quantity_in_stock', 0))
                )
                component_id = cursor.lastrowid
            else:
                _execute(cursor, """
                    INSERT INTO components (category_id, component_name, brand, model, specifications, price, selling_price, quantity_in_stock)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING component_id
                """, (data['category_id'], data['component_name'], data['brand'], data['model'],
                      data.get('specifications'), data['price'], data['selling_price'], data.get('quantity_in_stock', 0)))
                component_id = cursor.fetchone()[0]
            conn.commit()
            return component_id
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, component_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        if is_sqlite():
            cursor = conn.cursor()
            try:
                _execute(cursor, "SELECT * FROM components WHERE component_id = ?", (component_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
            finally:
                cursor.close()
                conn.close()
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                _execute(cursor, "SELECT * FROM components WHERE component_id = %s", (component_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
            finally:
                cursor.close()
                conn.close()

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        params = []
        if is_sqlite():
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM components WHERE 1=1"
                if filters:
                    if 'category_id' in filters:
                        query += " AND category_id = ?"
                        params.append(filters['category_id'])
                    if 'brand' in filters:
                        query += " AND brand LIKE ?"
                        params.append(f"%{filters['brand']}%")
                    if 'component_name' in filters:
                        query += " AND component_name LIKE ?"
                        params.append(f"%{filters['component_name']}%")
                _execute(cursor, query, params)
                return [dict(row) for row in cursor.fetchall()]
            finally:
                cursor.close()
                conn.close()
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                query = "SELECT * FROM components WHERE 1=1"
                if filters:
                    if 'category_id' in filters:
                        query += " AND category_id = %s"
                        params.append(filters['category_id'])
                    if 'brand' in filters:
                        query += " AND brand ILIKE %s"
                        params.append(f"%{filters['brand']}%")
                    if 'component_name' in filters:
                        query += " AND component_name ILIKE %s"
                        params.append(f"%{filters['component_name']}%")
                _execute(cursor, query, params)
                return [dict(row) for row in cursor.fetchall()]
            finally:
                cursor.close()
                conn.close()

    def update(self, component_id: int, data: Dict[str, Any]) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if is_sqlite():
                set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
                values = list(data.values()) + [component_id]
                _execute(cursor, f"UPDATE components SET {set_clause} WHERE component_id = ?", values)
            else:
                set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
                values = list(data.values()) + [component_id]
                _execute(cursor, f"UPDATE components SET {set_clause} WHERE component_id = %s", values)
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def delete(self, component_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if is_sqlite():
                _execute(cursor, "DELETE FROM components WHERE component_id = ?", (component_id,))
            else:
                _execute(cursor, "DELETE FROM components WHERE component_id = %s", (component_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

class SqlOrderRepository(IOrderRepository):
    def _get_connection(self):
        return get_raw_connection()

    def create(self, data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if is_sqlite():
                _execute(cursor,
                    """
                    INSERT INTO orders (client_id, build_id, order_type, status, total_price)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (data['client_id'], data.get('build_id'), data['order_type'], 
                     data.get('status', 'accepted'), data['total_price'])
                )
                order_id = cursor.lastrowid
                _execute(cursor,
                    """
                    INSERT INTO finances (order_id, record_type, amount, description)
                    VALUES (?, 'income', ?, ?)
                    """,
                    (order_id, data['total_price'], f'Order #{order_id} income')
                )
            else:
                _execute(cursor, """
                    INSERT INTO orders (client_id, build_id, order_type, status, total_price)
                    VALUES (%s, %s, %s, %s, %s) RETURNING order_id
                """, (data['client_id'], data.get('build_id'), data['order_type'], 
                      data.get('status', 'accepted'), data['total_price']))
                order_id = cursor.fetchone()[0]
                _execute(cursor, """
                    INSERT INTO finances (order_id, record_type, amount, description)
                    VALUES (%s, 'income', %s, %s)
                """, (order_id, data['total_price'], f'Order #{order_id} income'))

            conn.commit()
            return order_id
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        if is_sqlite():
            cursor = conn.cursor()
            try:
                _execute(cursor, "SELECT * FROM orders WHERE order_id = ?", (order_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
            finally:
                cursor.close()
                conn.close()
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                _execute(cursor, "SELECT * FROM orders WHERE order_id = %s", (order_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
            finally:
                cursor.close()
                conn.close()

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        params = []
        if is_sqlite():
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM orders WHERE 1=1"
                if filters:
                    if 'status' in filters:
                        query += " AND status = ?"
                        params.append(filters['status'])
                    if 'client_id' in filters:
                        query += " AND client_id = ?"
                        params.append(filters['client_id'])
                    if 'order_type' in filters:
                        query += " AND order_type = ?"
                        params.append(filters['order_type'])
                _execute(cursor, query, params)
                return [dict(row) for row in cursor.fetchall()]
            finally:
                cursor.close()
                conn.close()
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                query = "SELECT * FROM orders WHERE 1=1"
                if filters:
                    if 'status' in filters:
                        query += " AND status = %s"
                        params.append(filters['status'])
                    if 'client_id' in filters:
                        query += " AND client_id = %s"
                        params.append(filters['client_id'])
                    if 'order_type' in filters:
                        query += " AND order_type = %s"
                        params.append(filters['order_type'])
                _execute(cursor, query, params)
                return [dict(row) for row in cursor.fetchall()]
            finally:
                cursor.close()
                conn.close()

    def update_status(self, order_id: int, status: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if is_sqlite():
                if status == 'issued':
                    _execute(cursor, "UPDATE orders SET status = ?, completion_date = CURRENT_TIMESTAMP WHERE order_id = ?", (status, order_id))
                else:
                    _execute(cursor, "UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
            else:
                if status == 'issued':
                    _execute(cursor, """
                        UPDATE orders SET status = %s, completion_date = CURRENT_TIMESTAMP 
                        WHERE order_id = %s
                    """, (status, order_id))
                else:
                    _execute(cursor, "UPDATE orders SET status = %s WHERE order_id = %s", (status, order_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def delete(self, order_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if is_sqlite():
                _execute(cursor, "DELETE FROM orders WHERE order_id = ?", (order_id,))
            else:
                _execute(cursor, "DELETE FROM orders WHERE order_id = %s", (order_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

class SqlUserRepository(IUserRepository):
    def _get_connection(self):
        return get_raw_connection()

    def create(self, data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if is_sqlite():
                _execute(cursor, "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (data['username'], data['password_hash'], data.get('role', 'operator')))
                user_id = cursor.lastrowid
            else:
                _execute(cursor, """
                    INSERT INTO users (username, password_hash, role)
                    VALUES (%s, %s, %s) RETURNING user_id
                """, (data['username'], data['password_hash'], data.get('role', 'operator')))
                user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        if is_sqlite():
            cursor = conn.cursor()
            try:
                _execute(cursor, "SELECT user_id, username, role, created_at FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
            finally:
                cursor.close()
                conn.close()
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                _execute(cursor, "SELECT user_id, username, role, created_at FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
            finally:
                cursor.close()
                conn.close()

    def get_all(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        if is_sqlite():
            cursor = conn.cursor()
            try:
                _execute(cursor, "SELECT user_id, username, role, created_at FROM users")
                return [dict(row) for row in cursor.fetchall()]
            finally:
                cursor.close()
                conn.close()
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                _execute(cursor, "SELECT user_id, username, role, created_at FROM users")
                return [dict(row) for row in cursor.fetchall()]
            finally:
                cursor.close()
                conn.close()

    def delete(self, user_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if is_sqlite():
                _execute(cursor, "DELETE FROM users WHERE user_id = ?", (user_id,))
            else:
                _execute(cursor, "DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
