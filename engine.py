import asyncio
from typing import List
from models import Package
from backends.apt import AptBackend
from backends.flatpak import FlatpakBackend


class SearchEngine:
    def __init__(self):
        self.backends = [
            AptBackend(),
            FlatpakBackend(),
        ]

    async def search(self, query: str) -> List[Package]:
        tasks = [backend.search(query) for backend in self.backends]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        merged: List[Package] = []
        for res in results:
            if isinstance(res, list):
                merged.extend(res)
        return merged

    async def get_all_installed(self) -> List[Package]:
        tasks = []
        for backend in self.backends:
            if hasattr(backend, "get_installed_list"):
                tasks.append(backend.get_installed_list())
            elif hasattr(backend, "get_manual_installed_packages"):
                tasks.append(backend.get_manual_installed_packages())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        installed: List[Package] = []
        for res in results:
            if isinstance(res, list):
                installed.extend(res)

        # Ordina alfabeticamente per nome pacchetto
        return sorted(installed, key=lambda pkg: pkg.name.lower())