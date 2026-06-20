from typing import Optional, List
from pydantic import BaseModel


# ── 风格品类 ──
class BeerStyleBrief(BaseModel):
    """品类简要（列表/金刚区用）"""
    id: int
    name: str
    name_en: Optional[str] = None
    category: str
    description: Optional[str] = None
    icon: Optional[str] = None

    class Config:
        from_attributes = True


class BeerStyleDetail(BaseModel):
    """品类百科详情"""
    id: int
    name: str
    name_en: Optional[str] = None
    category: str
    description: Optional[str] = None
    origin_story: Optional[str] = None
    tasting_notes: Optional[str] = None
    ibu_min: Optional[int] = None
    ibu_max: Optional[int] = None
    srm_min: Optional[int] = None
    srm_max: Optional[int] = None
    abv_min: Optional[float] = None
    abv_max: Optional[float] = None
    icon: Optional[str] = None

    class Config:
        from_attributes = True


# ── 酒款 ──
class BeerItemBrief(BaseModel):
    """酒款简要"""
    id: int
    name: str
    name_en: Optional[str] = None
    brewery: Optional[str] = None
    country: Optional[str] = None
    style_name: Optional[str] = None
    abv: Optional[float] = None
    ibu: Optional[int] = None
    image_url: Optional[str] = None
    is_classic: int = 0

    class Config:
        from_attributes = True


class BeerItemDetail(BaseModel):
    """酒款详情"""
    id: int
    name: str
    name_en: Optional[str] = None
    brewery: Optional[str] = None
    country: Optional[str] = None
    style_id: Optional[int] = None
    style_name: Optional[str] = None
    description: Optional[str] = None
    abv: Optional[float] = None
    ibu: Optional[int] = None
    og: Optional[float] = None
    image_url: Optional[str] = None
    flavor_tags: Optional[str] = None
    is_classic: int = 0

    class Config:
        from_attributes = True


# ── 搜索 ──
class BeerSuggestItem(BaseModel):
    """搜索联想单项"""
    type: str          # "style" | "beer"
    id: int
    name: str
    subtitle: Optional[str] = None   # 风格品类名 或 酒厂名


class BeerSuggestResponse(BaseModel):
    items: List[BeerSuggestItem]


class BeerSearchResult(BaseModel):
    """搜索结果"""
    styles: List[BeerStyleBrief] = []
    beers: List[BeerItemBrief] = []


# ── 品类下的酒款列表 ──
class StyleBeersResponse(BaseModel):
    style: BeerStyleBrief
    beers: List[BeerItemBrief] = []
    classic_beers: List[BeerItemBrief] = []   # 经典代表作
