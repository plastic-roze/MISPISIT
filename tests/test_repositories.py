"""
Unit tests for CRUD operations (ORM and SQL).
"""
import pytest
from server.factory import RepositoryFactory
from server.repositories.base_repository import IComponentRepository, IOrderRepository, IUserRepository

class TestComponentRepository:
    @pytest.mark.parametrize("use_orm", [True, False])
    def test_create_component(self, sample_component_data, use_orm):
        repo = RepositoryFactory.create_component_repository(use_orm)
        component_id = repo.create(sample_component_data)
        assert isinstance(component_id, int)
        assert component_id > 0

    @pytest.mark.parametrize("use_orm", [True, False])
    def test_get_component(self, sample_component_data, use_orm):
        repo = RepositoryFactory.create_component_repository(use_orm)
        component_id = repo.create(sample_component_data)
        component = repo.get_by_id(component_id)

        assert component is not None
        assert component['component_name'] == sample_component_data['component_name']
        assert component['brand'] == sample_component_data['brand']

    @pytest.mark.parametrize("use_orm", [True, False])
    def test_get_all_with_filter(self, sample_component_data, use_orm):
        repo = RepositoryFactory.create_component_repository(use_orm)
        repo.create(sample_component_data)

        # Filter by brand
        results = repo.get_all({'brand': 'Intel'})
        assert len(results) > 0
        assert all('Intel' in r['brand'] for r in results)

    @pytest.mark.parametrize("use_orm", [True, False])
    def test_update_component(self, sample_component_data, use_orm):
        repo = RepositoryFactory.create_component_repository(use_orm)
        component_id = repo.create(sample_component_data)

        result = repo.update(component_id, {'quantity_in_stock': 20})
        assert result is True

        updated = repo.get_by_id(component_id)
        assert updated['quantity_in_stock'] == 20

    @pytest.mark.parametrize("use_orm", [True, False])
    def test_delete_component(self, sample_component_data, use_orm):
        repo = RepositoryFactory.create_component_repository(use_orm)
        component_id = repo.create(sample_component_data)

        result = repo.delete(component_id)
        assert result is True

        deleted = repo.get_by_id(component_id)
        assert deleted is None

class TestOrderRepository:
    @pytest.mark.parametrize("use_orm", [True, False])
    def test_create_order(self, sample_order_data, use_orm):
        repo = RepositoryFactory.create_order_repository(use_orm)
        order_id = repo.create(sample_order_data)
        assert isinstance(order_id, int)

    @pytest.mark.parametrize("use_orm", [True, False])
    def test_update_status(self, sample_order_data, use_orm):
        repo = RepositoryFactory.create_order_repository(use_orm)
        order_id = repo.create(sample_order_data)

        result = repo.update_status(order_id, 'assembling')
        assert result is True

        order = repo.get_by_id(order_id)
        assert order['status'] == 'assembling'

class TestUserRepository:
    @pytest.mark.parametrize("use_orm", [True, False])
    def test_user_crud(self, use_orm):
        repo = RepositoryFactory.create_user_repository(use_orm)

        # Create
        user_data = {
            'username': 'test_user_123',
            'password_hash': 'test_hash',
            'role': 'operator'
        }
        user_id = repo.create(user_data)
        assert isinstance(user_id, int)

        # Read
        user = repo.get_by_id(user_id)
        assert user['username'] == 'test_user_123'

        # List
        users = repo.get_all()
        assert len(users) > 0

        # Delete
        result = repo.delete(user_id)
        assert result is True
        assert repo.get_by_id(user_id) is None
