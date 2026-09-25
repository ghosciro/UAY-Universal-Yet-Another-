import argparse
import asyncio
import sys
from engine import Engine
from ranker import rank_packages
from ui import select_packages

async def amain():
    parser = argparse.ArgumentParser(description="yay-py: A Python wrapper for apt and flatpak")
    parser.add_argument("query", nargs="*", help="Packages to search and install")
    args = parser.parse_args()

    engine = Engine()

    if not args.query:
        print("Starting system update...")
        await engine.update_all()
        print("System update complete.")
    else:
        query_str = " ".join(args.query)
        print(f"Searching for '{query_str}'...")
        packages = await engine.search(query_str)
        
        if not packages:
            print("No packages found.")
            return

        ranked_packages = rank_packages(packages, query_str)
        selected = select_packages(ranked_packages)
        
        if not selected:
            print("Nothing selected. Exiting.")
            return
            
        print(f"Installing {len(selected)} packages...")
        await engine.install(selected)
        print("Installation complete.")

def main():
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)

if __name__ == "__main__":
    main()
