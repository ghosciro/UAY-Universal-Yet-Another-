import re
from typing import List
from rapidfuzz import fuzz
from models import Package

SOURCE_PRIORITY = {
    "FLATPAK": 50,
    "SNAP": 40,
    "PIPX": 30,
    "APT": 20,
    "HOMEBREW": 10,
}

def get_package_score(p: Package, query: str) -> float:
    name = (p.name or "").lower().strip()
    pkg_id = (p.id or "").lower().strip()
    q = query.lower().strip()
    desc = (p.desc or "").lower()
    source = (p.source or "").upper()
    is_installed = getattr(p, "installed", False)

    score = 0.0

    # TIER 1: Match Esatto (100.000+)
    if name == q or pkg_id == q:
        score += 100_000.0

    # TIER 2: Prefisso Diretto (es. spotify-qt, spotify-launcher) (50.000+)
    elif name.startswith(f"{q}-") or name.startswith(f"{q}_"):
        score += 50_000.0
    elif name.startswith(q):
        score += 40_000.0

    # TIER 3: Sottostringa nel Nome / ID (20.000+)
    elif q in name or q in pkg_id:
        score += 20_000.0
        # Premio se la parola è isolata nel nome (es. "ncspot")
        score += (1.0 - (len(name) - len(q)) / max(len(name), 1)) * 5_000.0

    # TIER 4: Match solo nella Descrizione (1.000+)
    else:
        # Punteggio basso: non può competere con i nomi
        if re.search(rf"\b{re.escape(q)}\b", desc):
            score += 2_000.0
        score += fuzz.partial_ratio(q, desc) * 10.0

    # Bonus Sorgente & Desktop (Flatpak / Snap)
    score += SOURCE_PRIORITY.get(source, 0)

    # Bonus Pacchetto già installato (visibilità immediata)
    if is_installed:
        score += 500.0

    # Penalità librerie/dev/doc se non richieste esplicitamente
    if not any(term in q for term in ("dev", "doc", "dbg", "lib", "python")):
        if name.startswith("python3-") or name.startswith("lib"):
            score -= 10_000.0
        if any(name.endswith(sfx) for sfx in ("-doc", "-dev", "-data", "-dbg")):
            score -= 10_000.0

    return score

def rank_packages(packages: List[Package], query: str) -> List[Package]:
    if not packages:
        return []
    # reverse=True mette il punteggio più alto in cima all'array
    return sorted(packages, key=lambda p: get_package_score(p, query), reverse=True)