import asyncio
from typing import List, Set
from models import Package
from backends.base import BaseBackend

class AptBackend(BaseBackend):
    async def get_installed_apt_packages(self) -> Set[str]:
        proc = await asyncio.create_subprocess_exec(
            "dpkg-query", "-W", "-f=${db:Status-Status} ${Package}\n",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await proc.communicate()
        installed = set()
        for line in stdout.decode("utf-8", errors="ignore").splitlines():
            parts = line.strip().split()
            if len(parts) >= 2 and parts[0] == "installed":
                installed.add(parts[1])
        return installed

    async def search(self, query: str) -> List[Package]:
        # Esegui in parallelo la ricerca apt-cache e il controllo dei pacchetti installati
        search_task = asyncio.create_subprocess_exec(
            "apt-cache", "search", query,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        installed_task = self.get_installed_apt_packages()

        proc, installed_pkgs = await asyncio.gather(search_task, installed_task)
        stdout, _ = await proc.communicate()

        if not stdout:
            return []

        packages = []
        for line in stdout.decode("utf-8", errors="ignore").splitlines():
            parts = line.split(" - ", 1)
            if len(parts) == 2:
                pkg_id = parts[0].strip()
                desc = parts[1].strip()
                packages.append(Package(
                    id=pkg_id,
                    name=pkg_id,
                    desc=desc,
                    source="apt",
                    installed=(pkg_id in installed_pkgs)
                ))
        return packages

    async def install(self, pkgs: List[Package]) -> None:
        if not pkgs:
            return
        pkg_ids = [p.id for p in pkgs]
        process = await asyncio.create_subprocess_exec(
            "sudo", "apt-get", "install", "-y", *pkg_ids
        )
        await process.communicate()

    async def update(self) -> None:
        print("Running apt update...")
        p1 = await asyncio.create_subprocess_exec("sudo", "apt-get", "update")
        await p1.communicate()

        print("Running apt upgrade...")
        p2 = await asyncio.create_subprocess_exec("sudo", "apt-get", "upgrade", "-y")
        await p2.communicate()