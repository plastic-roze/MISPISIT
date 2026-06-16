"""
Base repository interfaces (Strategy Pattern).
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IComponentRepository(ABC):
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_by_id(self, component_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update(self, component_id: int, data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def delete(self, component_id: int) -> bool:
        pass

class IOrderRepository(ABC):
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_status(self, order_id: int, status: str) -> bool:
        pass

    @abstractmethod
    def delete(self, order_id: int) -> bool:
        pass

class IUserRepository(ABC):
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass
