"""
SQL Repository implementations using raw sqlite3.
"""
from typing import List, Dict, Any, Optional
from server.repositories.base_repository import (
    IComponentRepository, IOrderRepository, IUserRepository,
    IClientRepository, ICatalogBuildRepository, IFinanceRepository
)
from server.database import get_raw_connection

class SqlComponentRepository(IComponentRepository):
    def _get_connection(self):
        return get_raw_connection()

    def create(self, data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO components (category_id, component_name, brand, model, specifications, price, selling_price, quantity_in_stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data['category_id'], data['component_name'], data['brand'], data['model'],
                  data.get('specifications'), data['price'], data['selling_price'], data.get('quantity_in_stock', 0)))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, component_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, cc.category_name 
                FROM components c 
                LEFT JOIN component_categories cc ON c.category_id = cc.category_id 
                WHERE c.component_id = ?
            """, (component_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            conn.close()

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT c.*, cc.category_name 
                FROM components c 
                LEFT JOIN component_categories cc ON c.category_id = cc.category_id 
                WHERE 1=1
            """
            params = []
            if filters:
                if 'category_id' in filters:
                    query += " AND c.category_id = ?"
                    params.append(filters['category_id'])
                if 'brand' in filters:
                    query += " AND c.brand LIKE ?"
                    params.append(f"%{filters['brand']}%")
                if 'component_name' in filters:
                    query += " AND c.component_name LIKE ?"
                    params.append(f"%{filters['component_name']}%")
                if 'in_stock' in filters and filters['in_stock']:
                    query += " AND c.quantity_in_stock > 0"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update(self, component_id: int, data: Dict[str, Any]) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values()) + [component_id]
            cursor.execute(f"UPDATE components SET {set_clause} WHERE component_id = ?", values)
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, component_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM components WHERE component_id = ?", (component_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

class SqlOrderRepository(IOrderRepository):
    def _get_connection(self):
        return get_raw_connection()

    def create(self, data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (client_id, build_id, order_type, status, total_price)
                VALUES (?, ?, ?, ?, ?)
            """, (data['client_id'], data.get('build_id'), data['order_type'], 
                  data.get('status', 'accepted'), data['total_price']))
            order_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO finances (order_id, record_type, amount, description)
                VALUES (?, 'income', ?, ?)
            """, (order_id, data['total_price'], f'Order #{order_id} income'))

            conn.commit()
            return order_id
        finally:
            conn.close()

    def get_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.*, c.first_name, c.last_name, cb.build_name
                FROM orders o
                LEFT JOIN clients c ON o.client_id = c.client_id
                LEFT JOIN catalog_builds cb ON o.build_id = cb.build_id
                WHERE o.order_id = ?
            """, (order_id,))
            result = cursor.fetchone()
            if result:
                row = dict(result)
                row['client_name'] = f"{row.get('first_name', '')} {row.get('last_name', '')}".strip()
                return row
            return None
        finally:
            conn.close()

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT o.*, c.first_name, c.last_name, cb.build_name
                FROM orders o
                LEFT JOIN clients c ON o.client_id = c.client_id
                LEFT JOIN catalog_builds cb ON o.build_id = cb.build_id
                WHERE 1=1
            """
            params = []
            if filters:
                if 'status' in filters:
                    query += " AND o.status = ?"
                    params.append(filters['status'])
                if 'client_id' in filters:
                    query += " AND o.client_id = ?"
                    params.append(filters['client_id'])
                if 'order_type' in filters:
                    query += " AND o.order_type = ?"
                    params.append(filters['order_type'])
            cursor.execute(query, params)
            result = []
            for row in cursor.fetchall():
                d = dict(row)
                d['client_name'] = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip()
                result.append(d)
            return result
        finally:
            conn.close()

    def update_status(self, order_id: int, status: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if status == 'issued':
                cursor.execute("""
                    UPDATE orders SET status = ?, completion_date = CURRENT_TIMESTAMP 
                    WHERE order_id = ?
                """, (status, order_id))
            else:
                cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, order_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT oi.*, c.component_name, c.brand
                FROM order_items oi
                JOIN components c ON oi.component_id = c.component_id
                WHERE oi.order_id = ?
            """, (order_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def add_order_item(self, order_id: int, component_id: int, quantity: int, unit_price: float) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO order_items (order_id, component_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (order_id, component_id, quantity, unit_price))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

class SqlUserRepository(IUserRepository):
    def _get_connection(self):
        return get_raw_connection()

    def create(self, data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (data['username'], data['password_hash'], data.get('role', 'operator')))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, role, created_at FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            conn.close()

    def get_all(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, role, created_at FROM users")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete(self, user_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

class SqlClientRepository(IClientRepository):
    def _get_connection(self):
        return get_raw_connection()

    def create(self, data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clients (first_name, last_name, email, phone)
                VALUES (?, ?, ?, ?)
            """, (data['first_name'], data['last_name'], data.get('email'), data.get('phone')))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, client_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            conn.close()

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM clients WHERE 1=1"
            params = []
            if filters:
                if 'first_name' in filters:
                    query += " AND first_name LIKE ?"
                    params.append(f"%{filters['first_name']}%")
                if 'last_name' in filters:
                    query += " AND last_name LIKE ?"
                    params.append(f"%{filters['last_name']}%")
                if 'email' in filters:
                    query += " AND email LIKE ?"
                    params.append(f"%{filters['email']}%")
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update(self, client_id: int, data: Dict[str, Any]) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values()) + [client_id]
            cursor.execute(f"UPDATE clients SET {set_clause} WHERE client_id = ?", values)
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, client_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

class SqlCatalogBuildRepository(ICatalogBuildRepository):
    def _get_connection(self):
        return get_raw_connection()

    def create(self, data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO catalog_builds (pc_category_id, build_name, description, base_price, markup_percent)
                VALUES (?, ?, ?, ?, ?)
            """, (data['pc_category_id'], data['build_name'], data.get('description'), 
                  data['base_price'], data['markup_percent']))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, build_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cb.*, pc.category_name
                FROM catalog_builds cb
                LEFT JOIN pc_categories pc ON cb.pc_category_id = pc.pc_category_id
                WHERE cb.build_id = ?
            """, (build_id,))
            result = cursor.fetchone()
            if result:
                row = dict(result)
                row['components'] = self.get_build_components(build_id)
                return row
            return None
        finally:
            conn.close()

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT cb.*, pc.category_name,
                       (SELECT COUNT(*) FROM catalog_build_items WHERE build_id = cb.build_id) as components_count
                FROM catalog_builds cb
                LEFT JOIN pc_categories pc ON cb.pc_category_id = pc.pc_category_id
                WHERE 1=1
            """
            params = []
            if filters and 'pc_category_id' in filters:
                query += " AND cb.pc_category_id = ?"
                params.append(filters['pc_category_id'])
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def add_component(self, build_id: int, component_id: int, quantity: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO catalog_build_items (build_id, component_id, quantity)
                VALUES (?, ?, ?)
            """, (build_id, component_id, quantity))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_build_components(self, build_id: int) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cbi.*, c.component_name, c.brand, c.model, c.selling_price
                FROM catalog_build_items cbi
                JOIN components c ON cbi.component_id = c.component_id
                WHERE cbi.build_id = ?
            """, (build_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete(self, build_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM catalog_build_items WHERE build_id = ?", (build_id,))
            cursor.execute("DELETE FROM catalog_builds WHERE build_id = ?", (build_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

class SqlFinanceRepository(IFinanceRepository):
    def _get_connection(self):
        return get_raw_connection()

    def create(self, data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO finances (order_id, record_type, amount, description)
                VALUES (?, ?, ?, ?)
            """, (data.get('order_id'), data['record_type'], data['amount'], data.get('description')))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM finances WHERE 1=1"
            params = []
            if filters:
                if 'record_type' in filters:
                    query += " AND record_type = ?"
                    params.append(filters['record_type'])
                if 'order_id' in filters:
                    query += " AND order_id = ?"
                    params.append(filters['order_id'])
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_summary(self) -> Dict[str, Any]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM finances WHERE record_type = 'income'")
            income = cursor.fetchone()[0]
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM finances WHERE record_type = 'expense'")
            expense = cursor.fetchone()[0]
            return {
                'total_income': float(income),
                'total_expense': float(expense),
                'profit': float(income) - float(expense)
            }
        finally:
            conn.close()
