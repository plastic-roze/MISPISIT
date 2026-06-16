"""
ORM Repository implementations - SQLite.
"""
from typing import List, Dict, Any, Optional
from server.repositories.base_repository import (
    IComponentRepository, IOrderRepository, IUserRepository,
    IClientRepository, ICatalogBuildRepository, IFinanceRepository
)
from server.database import SessionLocal
from server.models import (
    Component, Order, User, Client, CatalogBuild, CatalogBuildItem,
    OrderItem, Finance, ComponentCategory, PCCategory
)
from sqlalchemy import and_, func

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
        comp = self.db.query(Component).filter(Component.component_id == component_id).first()
        if comp:
            cat = self.db.query(ComponentCategory).filter(ComponentCategory.category_id == comp.category_id).first()
            return {
                'component_id': comp.component_id,
                'component_name': comp.component_name,
                'brand': comp.brand,
                'model': comp.model,
                'specifications': comp.specifications,
                'price': float(comp.price),
                'selling_price': float(comp.selling_price),
                'quantity_in_stock': comp.quantity_in_stock,
                'category_id': comp.category_id,
                'category_name': cat.category_name if cat else 'Unknown'
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
            if 'in_stock' in filters and filters['in_stock']:
                conditions.append(Component.quantity_in_stock > 0)
            if conditions:
                query = query.filter(and_(*conditions))

        components = query.all()
        result = []
        for c in components:
            cat = self.db.query(ComponentCategory).filter(ComponentCategory.category_id == c.category_id).first()
            result.append({
                'component_id': c.component_id,
                'component_name': c.component_name,
                'brand': c.brand,
                'model': c.model,
                'specifications': c.specifications,
                'price': float(c.price),
                'selling_price': float(c.selling_price),
                'quantity_in_stock': c.quantity_in_stock,
                'category_id': c.category_id,
                'category_name': cat.category_name if cat else 'Unknown'
            })
        return result

    def update(self, component_id: int, data: Dict[str, Any]) -> bool:
        comp = self.db.query(Component).filter(Component.component_id == component_id).first()
        if not comp:
            return False
        for key, value in data.items():
            setattr(comp, key, value)
        self.db.commit()
        return True

    def delete(self, component_id: int) -> bool:
        comp = self.db.query(Component).filter(Component.component_id == component_id).first()
        if not comp:
            return False
        self.db.delete(comp)
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
            client = self.db.query(Client).filter(Client.client_id == order.client_id).first()
            build = self.db.query(CatalogBuild).filter(CatalogBuild.build_id == order.build_id).first() if order.build_id else None
            return {
                'order_id': order.order_id,
                'client_id': order.client_id,
                'client_name': f"{client.first_name} {client.last_name}" if client else 'Unknown',
                'build_id': order.build_id,
                'build_name': build.build_name if build else None,
                'order_type': order.order_type,
                'status': order.status,
                'total_price': float(order.total_price),
                'order_date': order.order_date.isoformat() if order.order_date else None,
                'completion_date': order.completion_date.isoformat() if order.completion_date else None
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
        result = []
        for o in orders:
            client = self.db.query(Client).filter(Client.client_id == o.client_id).first()
            build = self.db.query(CatalogBuild).filter(CatalogBuild.build_id == o.build_id).first() if o.build_id else None
            result.append({
                'order_id': o.order_id,
                'client_id': o.client_id,
                'client_name': f"{client.first_name} {client.last_name}" if client else 'Unknown',
                'build_id': o.build_id,
                'build_name': build.build_name if build else None,
                'order_type': o.order_type,
                'status': o.status,
                'total_price': float(o.total_price),
                'order_date': o.order_date.isoformat() if o.order_date else None
            })
        return result

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

    def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        items = self.db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        result = []
        for item in items:
            comp = self.db.query(Component).filter(Component.component_id == item.component_id).first()
            result.append({
                'id': item.id,
                'component_id': item.component_id,
                'component_name': comp.component_name if comp else 'Unknown',
                'brand': comp.brand if comp else 'Unknown',
                'quantity': item.quantity,
                'unit_price': float(item.unit_price)
            })
        return result

    def add_order_item(self, order_id: int, component_id: int, quantity: int, unit_price: float) -> bool:
        item = OrderItem(
            order_id=order_id,
            component_id=component_id,
            quantity=quantity,
            unit_price=unit_price
        )
        self.db.add(item)
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

class OrmClientRepository(IClientRepository):
    def __init__(self):
        self.db = SessionLocal()

    def create(self, data: Dict[str, Any]) -> int:
        client = Client(**data)
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client.client_id

    def get_by_id(self, client_id: int) -> Optional[Dict[str, Any]]:
        client = self.db.query(Client).filter(Client.client_id == client_id).first()
        if client:
            return {
                'client_id': client.client_id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email,
                'phone': client.phone,
                'registration_date': client.registration_date.isoformat() if client.registration_date else None
            }
        return None

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = self.db.query(Client)
        if filters:
            conditions = []
            if 'first_name' in filters:
                conditions.append(Client.first_name.ilike(f"%{filters['first_name']}%"))
            if 'last_name' in filters:
                conditions.append(Client.last_name.ilike(f"%{filters['last_name']}%"))
            if 'email' in filters:
                conditions.append(Client.email.ilike(f"%{filters['email']}%"))
            if conditions:
                query = query.filter(and_(*conditions))
        return [{
            'client_id': c.client_id,
            'first_name': c.first_name,
            'last_name': c.last_name,
            'email': c.email,
            'phone': c.phone,
            'registration_date': c.registration_date.isoformat() if c.registration_date else None
        } for c in query.all()]

    def update(self, client_id: int, data: Dict[str, Any]) -> bool:
        client = self.db.query(Client).filter(Client.client_id == client_id).first()
        if not client:
            return False
        for key, value in data.items():
            setattr(client, key, value)
        self.db.commit()
        return True

    def delete(self, client_id: int) -> bool:
        client = self.db.query(Client).filter(Client.client_id == client_id).first()
        if not client:
            return False
        self.db.delete(client)
        self.db.commit()
        return True

class OrmCatalogBuildRepository(ICatalogBuildRepository):
    def __init__(self):
        self.db = SessionLocal()

    def create(self, data: Dict[str, Any]) -> int:
        build = CatalogBuild(**data)
        self.db.add(build)
        self.db.commit()
        self.db.refresh(build)
        return build.build_id

    def get_by_id(self, build_id: int) -> Optional[Dict[str, Any]]:
        build = self.db.query(CatalogBuild).filter(CatalogBuild.build_id == build_id).first()
        if build:
            cat = self.db.query(PCCategory).filter(PCCategory.pc_category_id == build.pc_category_id).first()
            components = self.get_build_components(build_id)
            total = sum(c['selling_price'] * c['quantity'] for c in components)
            return {
                'build_id': build.build_id,
                'build_name': build.build_name,
                'description': build.description,
                'base_price': float(build.base_price),
                'markup_percent': float(build.markup_percent),
                'pc_category_id': build.pc_category_id,
                'category_name': cat.category_name if cat else 'Unknown',
                'components': components,
                'total_cost': total,
                'final_price': total * (1 + float(build.markup_percent) / 100)
            }
        return None

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = self.db.query(CatalogBuild)
        if filters and 'pc_category_id' in filters:
            query = query.filter(CatalogBuild.pc_category_id == filters['pc_category_id'])

        builds = query.all()
        result = []
        for b in builds:
            cat = self.db.query(PCCategory).filter(PCCategory.pc_category_id == b.pc_category_id).first()
            components = self.get_build_components(b.build_id)
            total = sum(c['selling_price'] * c['quantity'] for c in components)
            result.append({
                'build_id': b.build_id,
                'build_name': b.build_name,
                'description': b.description,
                'base_price': float(b.base_price),
                'markup_percent': float(b.markup_percent),
                'category_name': cat.category_name if cat else 'Unknown',
                'components_count': len(components),
                'total_cost': total
            })
        return result

    def add_component(self, build_id: int, component_id: int, quantity: int) -> bool:
        item = CatalogBuildItem(build_id=build_id, component_id=component_id, quantity=quantity)
        self.db.add(item)
        self.db.commit()
        return True

    def get_build_components(self, build_id: int) -> List[Dict[str, Any]]:
        items = self.db.query(CatalogBuildItem).filter(CatalogBuildItem.build_id == build_id).all()
        result = []
        for item in items:
            comp = self.db.query(Component).filter(Component.component_id == item.component_id).first()
            if comp:
                result.append({
                    'component_id': comp.component_id,
                    'component_name': comp.component_name,
                    'brand': comp.brand,
                    'model': comp.model,
                    'selling_price': float(comp.selling_price),
                    'quantity': item.quantity
                })
        return result

    def delete(self, build_id: int) -> bool:
        build = self.db.query(CatalogBuild).filter(CatalogBuild.build_id == build_id).first()
        if not build:
            return False
        self.db.query(CatalogBuildItem).filter(CatalogBuildItem.build_id == build_id).delete()
        self.db.delete(build)
        self.db.commit()
        return True

class OrmFinanceRepository(IFinanceRepository):
    def __init__(self):
        self.db = SessionLocal()

    def create(self, data: Dict[str, Any]) -> int:
        record = Finance(**data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record.record_id

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = self.db.query(Finance)
        if filters:
            if 'record_type' in filters:
                query = query.filter(Finance.record_type == filters['record_type'])
            if 'order_id' in filters:
                query = query.filter(Finance.order_id == filters['order_id'])

        records = query.all()
        result = []
        for r in records:
            result.append({
                'record_id': r.record_id,
                'order_id': r.order_id,
                'record_type': r.record_type,
                'amount': float(r.amount),
                'description': r.description,
                'record_date': r.record_date.isoformat() if r.record_date else None
            })
        return result

    def get_summary(self) -> Dict[str, Any]:
        income = self.db.query(func.sum(Finance.amount)).filter(Finance.record_type == 'income').scalar() or 0
        expense = self.db.query(func.sum(Finance.amount)).filter(Finance.record_type == 'expense').scalar() or 0
        return {
            'total_income': float(income),
            'total_expense': float(expense),
            'profit': float(income) - float(expense)
        }
