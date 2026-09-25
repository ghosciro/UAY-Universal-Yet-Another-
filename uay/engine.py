import asyncio
from typing import List
from uay.models import Package
from uay.backends.base import BaseBackend
from uay.backends.apt import AptBackend
from uay.backends.flatpak import FlatpakBackend

class Engine:
    def __init__(self):
        self.backends: List[BaseBackend] = [AptBackend(), FlatpakBackend()]

    async def search(self, query: str) -> List[Package]:
        tasks = [backend.search(query) for backend in self.backends]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_packages = []
        for result in results:
            if isinstance(result, list):
                all_packages.extend(result)
        return all_packages
        
    async def update_all(self) -> None:
        tasks = [backend.update() for backend in self.backends]
        await asyncio.gather(*tasks)

    async def install(self, pkgs: List[Package]) -> None:
        apt_pkgs = [p for p in pkgs if p.source == 'apt']
        flatpak_pkgs = [p for p in pkgs if p.source == 'flatpak']
        
        tasks = []
        if apt_pkgs:
            tasks.append(AptBackend().install(apt_pkgs))
        if flatpak_pkgs:
            tasks.append(FlatpakBackend().install(flatpak_pkgs))
            
        if tasks:
            await asyncio.gather(*tasks)
