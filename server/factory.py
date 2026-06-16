"""
Factory Pattern for creating repository instances.
"""
from server.repositories.orm_repository import (
    OrmComponentRepository, OrmOrderRepository, OrmUserRepository,
    OrmClientRepository, OrmCatalogBuildRepository, OrmFinanceRepository
)
from server.repositories.sql_repository import (
    SqlComponentRepository, SqlOrderRepository, SqlUserRepository,
    SqlClientRepository, SqlCatalogBuildRepository, SqlFinanceRepository
)

class RepositoryFactory:
    @staticmethod
    def create_component_repository(use_orm: bool = True):
        return OrmComponentRepository() if use_orm else SqlComponentRepository()

    @staticmethod
    def create_order_repository(use_orm: bool = True):
        return OrmOrderRepository() if use_orm else SqlOrderRepository()

    @staticmethod
    def create_user_repository(use_orm: bool = True):
        return OrmUserRepository() if use_orm else SqlUserRepository()

    @staticmethod
    def create_client_repository(use_orm: bool = True):
        return OrmClientRepository() if use_orm else SqlClientRepository()

    @staticmethod
    def create_catalog_build_repository(use_orm: bool = True):
        return OrmCatalogBuildRepository() if use_orm else SqlCatalogBuildRepository()

    @staticmethod
    def create_finance_repository(use_orm: bool = True):
        return OrmFinanceRepository() if use_orm else SqlFinanceRepository()
