import shutil
from models import Package  # o dal path relativo del tuo progetto
from abc import ABC, abstractmethod
from typing import ClassVar, List


class BaseBackend(ABC):
    binary_name: ClassVar[str]

    def is_available(self) -> bool:
        """Returns True if the backend CLI tool exists on the system."""
        return shutil.which(self.binary_name) is not None

    @abstractmethod
    async def search(self, query: str) -> List[Package]:
        pass

    @abstractmethod
    async def install(self, pkgs: List[Package]) -> None:
        pass

    @abstractmethod
    async def update(self) -> None:
        pass

    @abstractmethod
    async def remove(self, package_id: str, autoremove: bool = False) -> bool:
        pass