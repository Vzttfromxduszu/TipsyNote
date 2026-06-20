from dataclasses import dataclass
from typing import Optional


@dataclass
class BeerWikiSearchDTO:
    q: str
    limit: int = 10
