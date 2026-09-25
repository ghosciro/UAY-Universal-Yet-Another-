from abc import ABC, abstractmethod
from typing import List
from uay.models import Package

class BaseBackend(ABC):
    @abstractmethod
    async def search(self, query: str) -> List[Package]:
        """Search for packages."""
        pass
        
    @abstractmethod
    async def install(self, pkgs: List[Package]) -> None:
        """Install packages."""
        pass
        
    @abstractmethod
    async def update(self) -> None:
        """Update packages metadata and upgrade system."""
        pass
