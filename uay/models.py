from dataclasses import dataclass
from typing import Optional

@dataclass
class Package:
    id: str
    name: str
    desc: str
    source: str
    installed: bool = False
    score: float = 0.0
