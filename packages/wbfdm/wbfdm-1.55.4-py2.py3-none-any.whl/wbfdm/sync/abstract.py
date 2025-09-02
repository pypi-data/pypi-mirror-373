from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Sync(Generic[T], ABC):
    @abstractmethod
    def update(self):
        """Updates all items"""
        ...

    @abstractmethod
    def update_or_create_item(self, external_id: int) -> T:
        """Updates or creates a single item from an external id and returns it"""
        ...

    @abstractmethod
    def update_item(self, item: T) -> T:
        """Updates a single item and returns it"""
        ...

    @abstractmethod
    def get_item(self, external_id: int) -> dict:
        """Retrieves a dictionairy representation of the item"""
        ...

    @abstractmethod
    def trigger_partial_update(self):
        """Figures out if an update is necessary and then tries to update the entire database in the most efficiant way"""
        ...
