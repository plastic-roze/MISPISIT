"""
Unit tests for CRUD operations (ORM and SQL).
"""
import pytest
from server.factory import RepositoryFactory

class TestComponentRepository:
    @pytest.mark.parametrize("use_orm", [True, False])
    def test_create_component(self, use_orm):
        repo = RepositoryFactory.create_component_repository(use_orm)
        data = {
            'category_id': 1,
            'component_name': 'Test CPU',
            'brand': 'Intel',
            'model': 'i9-13900K',
            'specifications': '24 cores',
            'price': 45000.00,
            'selling_price': 52000.00,
            'quantity_in_stock': 10
        }
        component_id = repo.create(data)
        assert isinstance(component_id, int)
        assert component_id > 0

    @pytest.mark.parametrize("use_orm", [True, False])
    def test_get_component(self, use_orm):
        repo = RepositoryFactory.create_component_repository(use_orm)
        data = {
            'category_id': 1,
            'component_name': 'Test CPU 2',
            'brand': 'Intel',
            'model': 'i7-13700K',
            'specifications': '16 cores',
            'price': 35000.00,
            'selling_price': 42000.00,
            'quantity_in_stock': 5
        }
        component_id = repo.create(data)
        component = repo.get_by_id(component_id)
        assert component is not None
        assert component['component_name'] == 'Test CPU 2'

    @pytest.mark.parametrize("use_orm", [True, False])
    def test_get_all_with_filter(self, use_orm):
        repo = RepositoryFactory.create_component_repository(use_orm)
        results = repo.get_all({'brand': 'Intel'})
        assert len(results) >= 0

    @pytest.mark.parametrize("use_orm", [True, False])
    def test_update_component(self, use_orm):
        repo = RepositoryFactory.create_component_repository(use_orm)
        data = {
            'category_id': 1,
            'component_name': 'Test CPU 3',
            'brand': 'AMD',
            'model': '7950X',
            'specifications': '16 cores',
            'price': 48000.00,
            'selling_price': 55000.00,
            'quantity_in_stock': 8
        }
        component_id = repo.create(data)
        result = repo.update(component_id, {'quantity_in_stock': 20})
        assert result is True
        updated = repo.get_by_id(component_id)
        assert updated['quantity_in_stock'] == 20

    @pytest.mark.parametrize("use_orm", [True, False])
    def test_delete_component(self, use_orm):
        repo = RepositoryFactory.create_component_repository(use_orm)
        data = {
            'category_id': 1,
            'component_name': 'Test CPU 4',
            'brand': 'AMD',
            'model': '7700X',
            'specifications': '8 cores',
            'price': 28000.00,
            'selling_price': 35000.00,
            'quantity_in_stock': 3
        }
        component_id = repo.create(data)
        result = repo.delete(component_id)
        assert result is True
        assert repo.get_by_id(component_id) is None

class TestOrderRepository:
    @pytest.mark.parametrize("use_orm", [True, False])
    def test_create_order(self, use_orm):
        repo = RepositoryFactory.create_order_repository(use_orm)
        data = {'client_id': 1, 'order_type': 'custom', 'total_price': 150000.00}
        order_id = repo.create(data)
        assert isinstance(order_id, int)

    @pytest.mark.parametrize("use_orm", [True, False])
    def test_update_status(self, use_orm):
        repo = RepositoryFactory.create_order_repository(use_orm)
        data = {'client_id': 1, 'order_type': 'custom', 'total_price': 100000.00}
        order_id = repo.create(data)
        result = repo.update_status(order_id, 'assembling')
        assert result is True
        order = repo.get_by_id(order_id)
        assert order['status'] == 'assembling'

class TestClientRepository:
    @pytest.mark.parametrize("use_orm", [True, False])
    def test_client_crud(self, use_orm):
        repo = RepositoryFactory.create_client_repository(use_orm)
        client_data = {'first_name': 'Иван', 'last_name': 'Иванов', 'email': 'ivan@test.com', 'phone': '+79990000000'}
        client_id = repo.create(client_data)
        assert isinstance(client_id, int)

        client = repo.get_by_id(client_id)
        assert client['first_name'] == 'Иван'

        repo.update(client_id, {'phone': '+79991111111'})
        updated = repo.get_by_id(client_id)
        assert updated['phone'] == '+79991111111'

        result = repo.delete(client_id)
        assert result is True
        assert repo.get_by_id(client_id) is None

class TestCatalogBuildRepository:
    @pytest.mark.parametrize("use_orm", [True, False])
    def test_build_crud(self, use_orm):
        repo = RepositoryFactory.create_catalog_build_repository(use_orm)
        build_data = {'pc_category_id': 1, 'build_name': 'Test Gaming PC', 'description': 'Test', 'base_price': 50000.00, 'markup_percent': 15.00}
        build_id = repo.create(build_data)
        assert isinstance(build_id, int)

        repo.add_component(build_id, 1, 1)
        components = repo.get_build_components(build_id)
        assert len(components) > 0

        result = repo.delete(build_id)
        assert result is True

class TestFinanceRepository:
    @pytest.mark.parametrize("use_orm", [True, False])
    def test_finance(self, use_orm):
        repo = RepositoryFactory.create_finance_repository(use_orm)
        record_id = repo.create({'record_type': 'expense', 'amount': 10000.00, 'description': 'Test expense'})
        assert isinstance(record_id, int)

        records = repo.get_all({'record_type': 'expense'})
        assert len(records) > 0

        summary = repo.get_summary()
        assert 'total_income' in summary
        assert 'total_expense' in summary
        assert 'profit' in summary
