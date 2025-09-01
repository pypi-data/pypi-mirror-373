from typing import List
from myreze.store.product import Product
from abc import ABC, abstractmethod


class ProductProvider(ABC):
    """Abstract base class for providing products to the store."""

    @abstractmethod
    async def get_products(self) -> List[Product]:
        """Return a list of available products."""
        pass
