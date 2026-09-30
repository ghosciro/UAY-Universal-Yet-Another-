import shutil
from models import Package  # o dal path relativo del tuo progetto
from abc import ABC, abstractmethod
from typing import ClassVar, List
import asyncio

class BaseBackend(ABC):
    
    def __init__(self):
        self.binary_name: str = ""
        self.install_cmd_prefix: List[str] = []

    def is_available(self) -> bool:
        """Returns True if the backend CLI tool exists on the system."""
        return shutil.which(self.binary_name) is not None

    @abstractmethod
    async def search(self, query: str) -> List[Package]:
        pass

    async def install(self, pkg_id: str) -> None:
        if not pkg_id or not self.install_cmd_prefix:
            return
            
        # Unisce il prefisso del comando con il nome del pacchetto
        cmd = self.install_cmd_prefix + [pkg_id]
        
        # L'asterisco * spacchetta la lista in argomenti separati
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.communicate()

    @abstractmethod
    async def update(self) -> None:
        pass

    @abstractmethod
    async def remove(self, package_id: str, autoremove: bool = False) -> bool:
        pass