from typing import List

from pydantic import BaseModel, Field


class AIRecommendRequest(BaseModel):
    mood: str = Field(min_length=1)
    tastes: List[str] = Field(default_factory=list)
    scene: str = Field(min_length=1)
    style: str = Field(min_length=1)


class AIRecommendItem(BaseModel):
    beer_name: str
    brewery_name: str
    reason: str


class AIRecommendResponse(BaseModel):
    items: List[AIRecommendItem]
