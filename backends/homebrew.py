import asyncio
import json
import os
import shutil
from typing import List, Union
from models import Package
from backends.base import BaseBackend


class HomebrewBackend(BaseBackend):
    def binary_name(self) -> str:
        for path in [
            shutil.which("brew"),
            "/home/linuxbrew/.linuxbrew/bin/brew",
            os.path.expanduser("~/.linuxbrew/bin/brew"),
        ]:
            if path and os.path.exists(path):
                return path
        return "brew"

    async def search(self, query: str) -> List[Package]:
        brew_bin = self.binary_name()
        
        # 1. Ricerca formule
        proc = await asyncio.create_subprocess_exec(
            brew_bin, "search", query,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await proc.communicate()
        if not stdout:
            return []

        names: List[str] = []
        for line in stdout.decode("utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("==>"):
                continue
            names.extend(line.split())

        if not names:
            return []

        # 2. Estrazione descrizioni in blocco (limite sui primi 25 per reattività)
        sample_names = names[:25]
        desc_map = {}
        try:
            info_proc = await asyncio.create_subprocess_exec(
                brew_bin, "info", "--json=v2", *sample_names,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )
            info_out, _ = await info_proc.communicate()
            if info_out:
                data = json.loads(info_out.decode("utf-8", errors="ignore"))
                for item in data.get("formulae", []):
                    desc_map[item["name"]] = item.get("desc", "") or ""
                for item in data.get("casks", []):
                    desc_list = item.get("desc", [])
                    desc = desc_list[0] if isinstance(desc_list, list) and desc_list else str(desc_list or "")
                    desc_map[item["token"]] = desc
        except Exception:
            pass

        return [
            Package(
                id=name,
                name=name,
                desc=desc_map.get(name, ""),
                source="BREW"
            )
            for name in names
        ]

    async def get_installed_list(self) -> List[Package]:
        brew_bin = self.binary_name()
        proc = await asyncio.create_subprocess_exec(
            brew_bin, "list", "--formula",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await proc.communicate()
        if not stdout:
            return []

        packages = []
        for line in stdout.decode("utf-8", errors="ignore").splitlines():
            name = line.strip()
            if name:
                packages.append(Package(
                    id=name,
                    name=name,
                    desc="",
                    source="BREW",
                    installed=True
                ))
        return packages

    async def install(
            self, pkgs: Union[List[Union[Package, str]], Package, str]
        ) -> None:
            if not pkgs:
                return

            # Normalizza in una lista uniforme
            pkg_sequence: List[Union[Package, str]]
            if isinstance(pkgs, (list, tuple, set)):
                pkg_sequence = list(pkgs)
            else:
                pkg_sequence = [pkgs]

            installed = {p.id for p in await self.get_installed_list()}
            to_install: List[str] = []

            for item in pkg_sequence:
                pkg_id = item.id if isinstance(item, Package) else str(item)
                if pkg_id in installed:
                    print(f"brew: '{pkg_id}' è già installato.")
                else:
                    to_install.append(pkg_id)

            if not to_install:
                return

            process = await asyncio.create_subprocess_exec(
                self.binary_name(), "install", *to_install
            )
            await process.communicate()

    async def update(self) -> None:
        print("Running brew update && brew upgrade...")
        proc_update = await asyncio.create_subprocess_exec(
            self.binary_name(), "update"
        )
        await proc_update.communicate()

        proc_upgrade = await asyncio.create_subprocess_exec(
            self.binary_name(), "upgrade"
        )
        await proc_upgrade.communicate()

    async def remove(self, package_id: str, autoremove: bool = False) -> bool:
        cmd = [self.binary_name(), "uninstall"]
        cmd.append(package_id)
        if autoremove:
            cmd.append("&& brew autoremove")
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.communicate()
        return process.returncode == 0