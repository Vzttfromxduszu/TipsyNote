from dataclasses import dataclass
from typing import List


@dataclass
class AIRecommendDTO:
    mood: str
    tastes: List[str]
    scene: str
    style: str
