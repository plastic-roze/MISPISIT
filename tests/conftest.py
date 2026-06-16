"""
pytest fixtures for PC Assembly System tests.
"""
import pytest
import sys
import os

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from server.auth import AuthService
from server.database import get_raw_connection

@pytest.fixture
def auth_service():
    return AuthService()

@pytest.fixture
def db_connection():
    conn = get_raw_connection()
    yield conn
    conn.close()

@pytest.fixture
def sample_component_data():
    return {
        'category_id': 1,
        'component_name': 'Test CPU',
        'brand': 'Intel',
        'model': 'i9-13900K',
        'specifications': '24 cores, 32 threads',
        'price': 45000.00,
        'selling_price': 52000.00,
        'quantity_in_stock': 10
    }

@pytest.fixture
def sample_order_data():
    return {
        'client_id': 1,
        'order_type': 'custom',
        'total_price': 150000.00
    }
