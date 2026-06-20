from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_optional_user
from dtos.beer_wiki import BeerWikiSearchDTO
from schema.beer_wiki import (
    BeerStyleBrief,
    BeerStyleDetail,
    BeerItemBrief,
    BeerItemDetail,
    BeerSearchResult,
    BeerSuggestItem,
    BeerSuggestResponse,
    StyleBeersResponse,
)
from services.beer_wiki_service import BeerWikiService
from models.beer_item import BeerItem
from models.beer_style import BeerStyle
from models.post import Post
from models.post_like import PostLike
from models.user import User
from utils.avatar_url import normalize_avatar_url

router = APIRouter(tags=["beer-wiki"])


# ── 辅助函数 ──
def _style_to_brief(s: BeerStyle) -> BeerStyleBrief:
    return BeerStyleBrief(
        id=s.id,
        name=s.name,
        name_en=s.name_en,
        category=s.category,
        description=s.description,
        icon=s.icon,
    )


def _style_to_detail(s: BeerStyle) -> BeerStyleDetail:
    return BeerStyleDetail(
        id=s.id,
        name=s.name,
        name_en=s.name_en,
        category=s.category,
        description=s.description,
        origin_story=s.origin_story,
        tasting_notes=s.tasting_notes,
        ibu_min=s.ibu_min,
        ibu_max=s.ibu_max,
        srm_min=s.srm_min,
        srm_max=s.srm_max,
        abv_min=float(s.abv_min) if s.abv_min else None,
        abv_max=float(s.abv_max) if s.abv_max else None,
        icon=s.icon,
    )


def _item_to_brief(item: BeerItem, db: Session) -> BeerItemBrief:
    style_name: Optional[str] = None
    if item.style_id:
        style = db.get(BeerStyle, item.style_id)
        if style:
            style_name = style.name
    return BeerItemBrief(
        id=item.id,
        name=item.name,
        name_en=item.name_en,
        brewery=item.brewery,
        country=item.country,
        style_name=style_name,
        abv=float(item.abv) if item.abv else None,
        ibu=item.ibu,
        image_url=item.image_url,
        is_classic=item.is_classic,
    )


def _item_to_detail(item: BeerItem, db: Session) -> BeerItemDetail:
    style_name: Optional[str] = None
    if item.style_id:
        style = db.get(BeerStyle, item.style_id)
        if style:
            style_name = style.name
    return BeerItemDetail(
        id=item.id,
        name=item.name,
        name_en=item.name_en,
        brewery=item.brewery,
        country=item.country,
        style_id=item.style_id,
        style_name=style_name,
        description=item.description,
        abv=float(item.abv) if item.abv else None,
        ibu=item.ibu,
        og=float(item.og) if item.og else None,
        image_url=item.image_url,
        flavor_tags=item.flavor_tags,
        is_classic=item.is_classic,
    )


# ── 搜索联想 ──
@router.get("/beer-wiki/suggest", response_model=BeerSuggestResponse)
def autocomplete(
    q: str = Query(min_length=1, description="搜索关键词"),
    limit: int = Query(default=8, ge=1, le=20),
    db: Session = Depends(get_db),
):
    service = BeerWikiService(db)
    items = service.suggest(q, limit)
    return {"items": [BeerSuggestItem(**it) for it in items]}


# ── 搜索 ──
@router.get("/beer-wiki/search", response_model=BeerSearchResult)
def search(
    q: str = Query(min_length=1, description="搜索关键词"),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    service = BeerWikiService(db)
    styles, beers = service.search(BeerWikiSearchDTO(q=q, limit=limit))
    return BeerSearchResult(
        styles=[_style_to_brief(s) for s in styles],
        beers=[_item_to_brief(b, db) for b in beers],
    )


# ── 所有品类（金刚区用） ──
@router.get("/beer-wiki/styles", response_model=list[BeerStyleBrief])
def list_styles(db: Session = Depends(get_db)):
    service = BeerWikiService(db)
    styles = service.get_all_styles()
    return [_style_to_brief(s) for s in styles]


# ── 品类详情 + 其下酒款 ──
@router.get("/beer-wiki/styles/{style_id}", response_model=StyleBeersResponse)
def style_detail(
    style_id: int,
    db: Session = Depends(get_db),
):
    service = BeerWikiService(db)
    try:
        style = service.get_style_detail(style_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    all_beers = service.get_items_by_style(style_id)
    classics = service.get_classics_by_style(style_id)

    return StyleBeersResponse(
        style=_style_to_brief(style),
        beers=[_item_to_brief(b, db) for b in all_beers],
        classic_beers=[_item_to_brief(b, db) for b in classics],
    )


# ── 品类百科详细（含雷达图数据） ──
@router.get("/beer-wiki/styles/{style_id}/detail", response_model=BeerStyleDetail)
def style_detail_full(
    style_id: int,
    db: Session = Depends(get_db),
):
    service = BeerWikiService(db)
    try:
        style = service.get_style_detail(style_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return _style_to_detail(style)


# ── 所有经典酒款 ──
@router.get("/beer-wiki/classics", response_model=list[BeerItemBrief])
def list_classic_beers(db: Session = Depends(get_db)):
    service = BeerWikiService(db)
    items = service.get_all_classics()
    return [_item_to_brief(b, db) for b in items]


# ── 酒款详情 + 社区联动 ──
@router.get("/beer-wiki/items/{item_id}")
def beer_detail(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    service = BeerWikiService(db)
    try:
        item = service.get_item_detail(item_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    detail = _item_to_detail(item, db)

    # 社区联动：搜索包含该酒款名的帖子
    related_posts: list = []
    if item.name:
        from repositories.posts_repository import PostsRepository
        posts_repo = PostsRepository(db)
        keyword_posts = posts_repo.search(
            keyword=item.name,
            user_id=None,
            status=1,
            offset=0,
            limit=5,
        )
        for p in keyword_posts:
            user = db.get(User, p.user_id)
            liked = False
            if current_user:
                liked = db.query(PostLike).filter(
                    PostLike.post_id == p.id, PostLike.user_id == current_user.id
                ).first() is not None
            related_posts.append({
                "id": p.id,
                "title": p.title,
                "content": p.content[:200] if p.content else "",
                "like_count": p.like_count or 0,
                "comment_count": p.comment_count or 0,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "user_nickname": user.nickname if user else None,
                "user_avatar": normalize_avatar_url(user.avatar_url) if user else None,
                "liked": liked,
            })

    return {
        "beer": detail.model_dump(),
        "related_posts": related_posts,
    }
