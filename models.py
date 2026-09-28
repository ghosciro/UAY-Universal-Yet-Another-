from dataclasses import dataclass

@dataclass
class Package:
    id: str
    name: str
    desc: str
    source: str
    installed: bool = False
    score: float = 0.0

    def __iter__(self):
        yield self