"""
SQLAlchemy ORM models - SQLite compatible.
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from server.database import Base
from datetime import datetime

class ComponentCategory(Base):
    __tablename__ = 'component_categories'
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

class Component(Base):
    __tablename__ = 'components'
    component_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('component_categories.category_id'), nullable=False)
    component_name = Column(String(100), nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    specifications = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    selling_price = Column(DECIMAL(10, 2), nullable=False)
    quantity_in_stock = Column(Integer, nullable=False, default=0)
    category = relationship("ComponentCategory")

class PCCategory(Base):
    __tablename__ = 'pc_categories'
    pc_category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

class CatalogBuild(Base):
    __tablename__ = 'catalog_builds'
    build_id = Column(Integer, primary_key=True, autoincrement=True)
    pc_category_id = Column(Integer, ForeignKey('pc_categories.pc_category_id'), nullable=False)
    build_name = Column(String(100), nullable=False)
    description = Column(Text)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    markup_percent = Column(DECIMAL(5, 2), nullable=False, default=0.00)
    category = relationship("PCCategory")

class CatalogBuildItem(Base):
    __tablename__ = 'catalog_build_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    build_id = Column(Integer, ForeignKey('catalog_builds.build_id', ondelete='CASCADE'), nullable=False)
    component_id = Column(Integer, ForeignKey('components.component_id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

class Client(Base):
    __tablename__ = 'clients'
    client_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    registration_date = Column(Date, nullable=False, default=datetime.now)

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='operator')
    created_at = Column(DateTime, nullable=False, default=datetime.now)

class Order(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        CheckConstraint("order_type IN ('catalog', 'custom')", name='check_order_type'),
        CheckConstraint("status IN ('accepted', 'assembling', 'ready', 'issued', 'cancelled')", name='check_status'),
    )
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.client_id'), nullable=False)
    build_id = Column(Integer, ForeignKey('catalog_builds.build_id'))
    order_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default='accepted')
    total_price = Column(DECIMAL(10, 2), nullable=False)
    order_date = Column(DateTime, nullable=False, default=datetime.now)
    completion_date = Column(DateTime)

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)
    component_id = Column(Integer, ForeignKey('components.component_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)

class Finance(Base):
    __tablename__ = 'finances'
    __table_args__ = (
        CheckConstraint("record_type IN ('income', 'expense')", name='check_record_type'),
    )
    record_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    record_type = Column(String(20), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text)
    record_date = Column(DateTime, nullable=False, default=datetime.now)
