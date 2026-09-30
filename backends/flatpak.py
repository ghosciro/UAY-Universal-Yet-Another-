import asyncio
from typing import List
from models import Package
from backends.base import BaseBackend

class FlatpakBackend(BaseBackend):
    def __init__(self):
        super().__init__()
        self.binary_name = "flatpak"
        self.install_cmd_prefix = ["sudo", "flatpak", "install", "-y"]
    
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

    async def update(self) -> None:
        print("Running flatpak update...")
        process = await asyncio.create_subprocess_exec(
            'flatpak', 'update', '-y'
        )
        await process.communicate()

    async def get_installed_list(self) -> List[Package]:
        proc = await asyncio.create_subprocess_exec(
            "flatpak", "list", "--app", "--columns=application,name,description",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await proc.communicate()
        packages = []
        for line in stdout.decode().splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                app_id = parts[0].strip()
                name = parts[1].strip()
                desc = parts[2].strip() if len(parts) > 2 else ""
                packages.append(
                    Package(
                        id=app_id,
                        name=name,
                        source="FLATPAK",
                        desc=desc,
                        installed=True
                    )
                )
        return packages

    async def remove(self, package_id: str, autoremove: bool = False) -> bool:
            proc = await asyncio.create_subprocess_exec("flatpak", "uninstall", "-y", package_id)
            if await proc.wait() != 0:
                return False

            if autoremove:
                cleanup = await asyncio.create_subprocess_exec("flatpak", "uninstall", "--unused", "-y")
                await cleanup.wait()
                return cleanup.returncode == 0

            return True