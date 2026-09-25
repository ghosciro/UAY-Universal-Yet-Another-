import asyncio
from typing import List
from uay.models import Package
from uay.backends.base import BaseBackend

class FlatpakBackend(BaseBackend):
    async def search(self, query: str) -> List[Package]:
        process = await asyncio.create_subprocess_exec(
            'flatpak', 'search', query,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        if not stdout:
            return []
            
        packages = []
        for line in stdout.decode('utf-8', errors='ignore').splitlines():
            if not line.strip() or line.startswith("Name") or line.startswith("Nome"):
                continue
                
            # flatpak output can be tab or space separated
            parts = [p.strip() for p in line.split('\t') if p.strip()]
            if len(parts) < 3:
                parts = [p.strip() for p in line.split('  ') if p.strip()]
                
            if len(parts) >= 3:
                name = parts[0]
                desc = parts[1]
                pkg_id = parts[2]
                packages.append(Package(
                    id=pkg_id,
                    name=name,
                    desc=desc,
                    source='flatpak'
                ))
        return packages

    async def install(self, pkgs: List[Package]) -> None:
        if not pkgs:
            return
        pkg_ids = [p.id for p in pkgs]
        process = await asyncio.create_subprocess_exec(
            'flatpak', 'install', '-y', *pkg_ids
        )
        await process.communicate()

    async def update(self) -> None:
        print("Running flatpak update...")
        process = await asyncio.create_subprocess_exec(
            'flatpak', 'update', '-y'
        )
        await process.communicate()
