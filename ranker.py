from typing import List
from rapidfuzz import fuzz
from models import Package

def get_package_score(p: Package, query: str) -> float:
    name = p.name.lower()
    q = query.lower()
    desc = (p.desc or "").lower()

    # 1. Punteggio fuzzy base (nome 70%, descrizione 30%)
    name_fuzz = fuzz.WRatio(q, name)
    desc_fuzz = fuzz.partial_ratio(q, desc)
    score = (name_fuzz * 0.7) + (desc_fuzz * 0.3)

    # 2. Match esatto o parziale sul nome
    if name == q:
        score += 1000
    elif name == f"python3-{q}":
        score += 500
    elif name.startswith(q) or name.endswith(q):
        score += 300
    elif q in name:
        score += 150

    # 3. Penalità per documentazione e debug
    if name.endswith("-doc") or name.endswith("-data"):
        score -= 400
    elif name.endswith("-dev") or name.endswith("-dbg"):
        score -= 100

    return score

def rank_packages(packages: List[Package], query: str) -> List[Package]:
    reverse=True  # Ordina in ordine decrescente di punteggio
    return sorted(packages, key=lambda p: get_package_score(p, query), reverse=reverse)