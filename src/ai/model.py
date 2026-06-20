from typing import TypedDict


class RecommendationItem(TypedDict):
    beer_name: str
    brewery_name: str
    reason: str