"""
ORM Repository implementations using SQLAlchemy.
"""
from typing import List, Dict, Any, Optional
from server.repositories.base_repository import IComponentRepository, IOrderRepository, IUserRepository
from server.database import SessionLocal, get_raw_connection
from server.models import Component, Order, User, Client, CatalogBuild, OrderItem, Finance
from sqlalchemy import and_

class OrmComponentRepository(IComponentRepository):
    def __init__(self):
        self.db = SessionLocal()

    def create(self, data: Dict[str, Any]) -> int:
        component = Component(**data)
        self.db.add(component)
        self.db.commit()
        self.db.refresh(component)
        return component.component_id

    def get_by_id(self, component_id: int) -> Optional[Dict[str, Any]]:
        component = self.db.query(Component).filter(Component.component_id == component_id).first()
        if component:
            return {
                'component_id': component.component_id,
                'component_name': component.component_name,
                'brand': component.brand,
                'model': component.model,
                'price': float(component.price),
                'selling_price': float(component.selling_price),
                'quantity_in_stock': component.quantity_in_stock,
                'category_id': component.category_id
            }
        return None

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = self.db.query(Component)
        if filters:
            conditions = []
            if 'category_id' in filters:
                conditions.append(Component.category_id == filters['category_id'])
            if 'brand' in filters:
                conditions.append(Component.brand.ilike(f"%{filters['brand']}%"))
            if 'component_name' in filters:
                conditions.append(Component.component_name.ilike(f"%{filters['component_name']}%"))
            if conditions:
                query = query.filter(and_(*conditions))

        components = query.all()
        return [{
            'component_id': c.component_id,
            'component_name': c.component_name,
            'brand': c.brand,
            'model': c.model,
            'price': float(c.price),
            'selling_price': float(c.selling_price),
            'quantity_in_stock': c.quantity_in_stock,
            'category_id': c.category_id
        } for c in components]

    def update(self, component_id: int, data: Dict[str, Any]) -> bool:
        component = self.db.query(Component).filter(Component.component_id == component_id).first()
        if not component:
            return False
        for key, value in data.items():
            setattr(component, key, value)
        self.db.commit()
        return True

    def delete(self, component_id: int) -> bool:
        component = self.db.query(Component).filter(Component.component_id == component_id).first()
        if not component:
            return False
        self.db.delete(component)
        self.db.commit()
        return True

class OrmOrderRepository(IOrderRepository):
    def __init__(self):
        self.db = SessionLocal()

    def create(self, data: Dict[str, Any]) -> int:
        order = Order(**data)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        # Create finance record for income
        if 'total_price' in data:
            finance = Finance(
                order_id=order.order_id,
                record_type='income',
                amount=data['total_price'],
                description=f'Order #{order.order_id} income'
            )
            self.db.add(finance)
            self.db.commit()

        return order.order_id

    def get_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        order = self.db.query(Order).filter(Order.order_id == order_id).first()
        if order:
            return {
                'order_id': order.order_id,
                'client_id': order.client_id,
                'build_id': order.build_id,
                'order_type': order.order_type,
                'status': order.status,
                'total_price': float(order.total_price),
                'order_date': order.order_date.isoformat() if order.order_date else None
            }
        return None

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = self.db.query(Order)
        if filters:
            conditions = []
            if 'status' in filters:
                conditions.append(Order.status == filters['status'])
            if 'client_id' in filters:
                conditions.append(Order.client_id == filters['client_id'])
            if 'order_type' in filters:
                conditions.append(Order.order_type == filters['order_type'])
            if conditions:
                query = query.filter(and_(*conditions))

        orders = query.all()
        return [{
            'order_id': o.order_id,
            'client_id': o.client_id,
            'build_id': o.build_id,
            'order_type': o.order_type,
            'status': o.status,
            'total_price': float(o.total_price),
            'order_date': o.order_date.isoformat() if o.order_date else None
        } for o in orders]

    def update_status(self, order_id: int, status: str) -> bool:
        order = self.db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return False
        order.status = status
        if status == 'issued':
            from datetime import datetime
            order.completion_date = datetime.now()
        self.db.commit()
        return True

    def delete(self, order_id: int) -> bool:
        order = self.db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return False
        self.db.delete(order)
        self.db.commit()
        return True

class OrmUserRepository(IUserRepository):
    def __init__(self):
        self.db = SessionLocal()

    def create(self, data: Dict[str, Any]) -> int:
        user = User(**data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user.user_id

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if user:
            return {
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        return None

    def get_all(self) -> List[Dict[str, Any]]:
        users = self.db.query(User).all()
        return [{
            'user_id': u.user_id,
            'username': u.username,
            'role': u.role,
            'created_at': u.created_at.isoformat() if u.created_at else None
        } for u in users]

    def delete(self, user_id: int) -> bool:
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
