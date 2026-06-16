"""
Factory Pattern for creating repository instances.
"""
from server.repositories.orm_repository import OrmComponentRepository, OrmOrderRepository, OrmUserRepository
from server.repositories.sql_repository import SqlComponentRepository, SqlOrderRepository, SqlUserRepository

class RepositoryFactory:
    """Factory for creating ORM or SQL repository instances."""

    @staticmethod
    def create_component_repository(use_orm: bool = True):
        if use_orm:
            return OrmComponentRepository()
        return SqlComponentRepository()

    @staticmethod
    def create_order_repository(use_orm: bool = True):
        if use_orm:
            return OrmOrderRepository()
        return SqlOrderRepository()

    @staticmethod
    def create_user_repository(use_orm: bool = True):
        if use_orm:
            return OrmUserRepository()
        return SqlUserRepository()
