"""
pytest fixtures.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server.auth import AuthService

@pytest.fixture
def auth_service():
    return AuthService()
