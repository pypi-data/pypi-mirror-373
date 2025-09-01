"""Abstract base driver for akron drivers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseDriver(ABC):
    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        raise NotImplementedError

    @abstractmethod
    def find(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def update(self, table_name: str, filters: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        raise NotImplementedError

    @abstractmethod
    def delete(self, table_name: str, filters: Dict[str, Any]) -> int:
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError
