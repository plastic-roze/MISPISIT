"""
Unit tests for authentication service.
"""
import pytest
from server.auth import AuthService

def test_password_hashing(auth_service):
    password = "test_password123"
    hashed = auth_service.hash_password(password)
    assert hashed != password
    assert hashed.startswith('$2b$')
    assert auth_service.verify_password(password, hashed)
    assert not auth_service.verify_password("wrong_password", hashed)

def test_password_hash_uniqueness(auth_service):
    password = "test_password123"
    hash1 = auth_service.hash_password(password)
    hash2 = auth_service.hash_password(password)
    assert hash1 != hash2
    assert auth_service.verify_password(password, hash1)
    assert auth_service.verify_password(password, hash2)

def test_verify_password_invalid_hash(auth_service):
    assert not auth_service.verify_password("password", "invalid_hash")

def test_hash_password_empty(auth_service):
    hashed = auth_service.hash_password("")
    assert auth_service.verify_password("", hashed)
