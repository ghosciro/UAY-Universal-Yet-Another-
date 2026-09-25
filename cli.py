import argparse
import asyncio
import sys
import re
from engine import SearchEngine
from ranker import rank_packages
from ui import select_packages


async def handle_update(engine: SearchEngine) -> None:
    print("\033[1;34m::\033[0m Starting update process for APT and Flatpak...")
    print("\033[1;32m==>\033[0m Updating APT packages...")
    proc_apt = await asyncio.create_subprocess_exec("sudo", "apt", "update")
    await proc_apt.wait()
    proc_apt_up = await asyncio.create_subprocess_exec("sudo", "apt", "upgrade", "-y")
    await proc_apt_up.wait()

    print("\n\033[1;35m==>\033[0m Updating Flatpak...")
    proc_flatpak = await asyncio.create_subprocess_exec("flatpak", "update", "-y")
    await proc_flatpak.wait()

async def has_matching_bigram(query: str, text: str) -> bool:
    q = query.lower()
    t = text.lower()
    # Se la query ha solo 1 carattere, basta che sia presente
    if len(q) < 2:
        return q in t
    # Genera tutte le coppie di 2 lettere consecutive (bigrammi) della query
    bigrams = [q[i : i + 2] for i in range(len(q) - 1)]
    # Verifica che almeno una coppia compaia consecutivamente nel testo
    return any(bg in t for bg in bigrams)

async def handle_uninstall(engine: SearchEngine, initial_query: str = "") -> None:
    print("\033[1;34m::\033[0m Finding installed packages...")
    packages = await engine.get_all_installed()
    if not packages:
        print("No Packages found.")
        return

    # Passa initial_query direttamente a fzf
    selected = select_packages(
        packages, prompt="Uninstall > ", query=initial_query
    )
    if not selected:
        print("Operation cancelled.")
        return

    print(f"\nSelected: {len(selected)}")
    for pkg in selected:
        backend = next(
            (
                b
                for b in engine.backends
                if pkg.source.lower() in b.__class__.__name__.lower()
            ),
            None,
        )
        if backend:
            print(
                f"\n\033[1;31m==>\033[0m Uninstalling {pkg.name} ({pkg.source})..."
            )
            await backend.remove(pkg.id)

def contains_exact_word(query: str, text: str) -> bool:
    if not query or not text:
        return False
    # \b assicura che il termine sia una parola intera delimitata da spazi o punteggiatura
    pattern = rf"\b{re.escape(query.strip())}\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


async def handle_search_and_install(engine: SearchEngine, query: str) -> None:
    print(f"\033[1;34m::\033[0m Searching for '{query}'...")
    results = await engine.search(query)
    if not results:
        print("No packages found.")
        return

    # Filtra tenendo solo i pacchetti che contengono la parola esatta nel nome, ID o descrizione
    filtered = [
        p
        for p in results
        if contains_exact_word(query, p.name)
        or contains_exact_word(query, p.id or "")
        or contains_exact_word(query, p.desc or "")
    ]

    if not filtered:
        print(f"No packages found containing the exact word '{query}'.")
        return

    ranked = rank_packages(filtered, query)
    selected = select_packages(ranked, prompt="Install > ")
    if not selected:
        print("Operation cancelled.")
        return

    print(f"\nPackages to install: {len(selected)}")
    for pkg in selected:
        backend = next(
            (
                b
                for b in engine.backends
                if pkg.source.lower() in b.__class__.__name__.lower()
            ),
            None,
        )
        if backend:
            print(
                f"\n\033[1;32m==>\033[0m Installing {pkg.name} ({pkg.source})..."
            )
            await backend.install(pkg.id)


async def run() -> None:
    parser = argparse.ArgumentParser(
        prog="uay",
        description="Universal Yet Another - Wrapper unificato per APT e Flatpak",
    )
    parser.add_argument(
        "-u",
        "--uninstall",
        action="store_true",
        help="Visualizza i pacchetti installati e seleziona cosa rimuovere",
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Nome o filtro dell'applicazione",
    )

    args = parser.parse_args()
    engine = SearchEngine()

    if args.uninstall:
        # Permette sia `uay -u` che `uay -u query`
        await handle_uninstall(engine, initial_query=args.query)
    elif not args.query:
        await handle_update(engine)
    else:
        await handle_search_and_install(engine, args.query)


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()