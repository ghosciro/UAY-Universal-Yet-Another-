import asyncio
from typing import List
from models import Package
from backends.base import BaseBackend

class SnapBackend(BaseBackend):
    def binary_name(self) -> str:
        return "snap"
    
    async def search(self, query: str) -> List[Package]:
        process = await asyncio.create_subprocess_exec(
            'snap', 'find', query,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        if not stdout:
            return []
            
        packages = []
        for line in stdout.decode('utf-8', errors='ignore').splitlines():
            if not line.strip() or line.startswith("Name"):
                continue
                
            parts = [p.strip() for p in line.split() if p.strip()]
            if len(parts) >= 2:
                name = parts[0]
                # Il sommario è solitamente l'ultima colonna o il resto della riga
                desc = " ".join(parts[4:]) if len(parts) > 4 else " ".join(parts[1:])
                packages.append(Package(
                    id=name,
                    name=name,
                    desc=desc,
                    source='snap'
                ))
        return packages

    async def install(self, pkgs) -> None:
        if not pkgs:
            return
        if isinstance(pkgs, (str, Package)):
            pkgs = [pkgs]
        pkg_ids = [p if isinstance(p, str) else p.id for p in pkgs]
        
        process = await asyncio.create_subprocess_exec(
            'sudo', 'snap', 'install', *pkg_ids
        )
        await process.communicate()

    async def update(self) -> None:
        print("Running snap refresh...")
        process = await asyncio.create_subprocess_exec(
            'sudo', 'snap', 'refresh'
        )
        await process.communicate()

    async def get_installed_list(self) -> List[Package]:
        proc = await asyncio.create_subprocess_exec(
            "snap", "list",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        if not stdout:
            return []
            
        packages = []
        for line in stdout.decode('utf-8', errors='ignore').splitlines():
            if not line.strip() or line.startswith("Name"):
                continue
                
            parts = [p.strip() for p in line.split() if p.strip()]
            if len(parts) >= 2:
                name = parts[0]
                pkg_id = parts[0]  # Snap uses the same name as ID
                desc = ""  # Snap list does not provide description
                packages.append(Package(
                    id=pkg_id,
                    name=name,
                    desc=desc,
                    source='snap'
                ))
        return packages

    async def remove(self, pkg_id: str,autoremove: bool = False) -> None:
        process = await asyncio.create_subprocess_exec(
            'sudo', 'snap', 'remove', "--purge" ,pkg_id
        )
        await process.communicate()