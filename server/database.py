"""
Database configuration module.
Supports PostgreSQL (psycopg2) and a local SQLite fallback.
Provides connections for SQLAlchemy ORM and raw DBAPI connections.
"""
import os
import sqlite3
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Environment flag to force SQLite (default: enabled for local/dev)
USE_SQLITE = os.getenv('USE_SQLITE', '1').lower() in ('1', 'true', 'yes')

# PostgreSQL connection settings (default)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'pc_assembly'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Decide engine URL
if USE_SQLITE:
    DATABASE_URL = f"sqlite:///{DB_CONFIG['database']}.db"
else:
    DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def is_sqlite() -> bool:
    return DATABASE_URL.startswith('sqlite')

def get_raw_connection():
    """Return a raw DBAPI connection: psycopg2 for Postgres or sqlite3 for SQLite."""
    if is_sqlite():
        conn = sqlite3.connect(f"{DB_CONFIG['database']}.db")
        conn.row_factory = sqlite3.Row
        return conn
    return psycopg2.connect(**DB_CONFIG)

def get_db_session():
    """Get SQLAlchemy session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# When using SQLite for local development, ensure tables exist by importing models
if is_sqlite():
    try:
        # Import models to register them with Base
        import server.models  # noqa: F401
        Base.metadata.create_all(bind=engine)
    except Exception:
        # If something goes wrong during automatic initialization, ignore here;
        # init_db.py can be run manually for detailed errors.
        pass
