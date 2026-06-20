from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from dtos.beer_inventory import BeerCreateDTO, BeerSearchDTO, BeerUpdateDTO
from schema.beer_inventory import (
    BeerCreateRequest,
    BeerUpdateRequest,
    BeerResponse,
    BeerListResponse,
    BeerStyleSearchResponse,
)
from services.beer_inventory_service import BeerInventoryService
from services.pubs_service import PubsService


router = APIRouter(tags=["beer_inventory"])


def _to_beer_response(beer) -> dict:
    return {
        "id": beer.id,
        "pub_id": beer.pub_id,
        "beer_name": beer.beer_name,
        "brewery_name": beer.brewery_name,
        "style": beer.style,
        "abv": float(beer.abv) if beer.abv is not None else None,
        "volume_ml": beer.volume_ml,
        "price": float(beer.price) if beer.price is not None else None,
        "status": beer.status,
    }


@router.post("/beers", response_model=BeerResponse)
def create_beer(
    payload: BeerCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in (1, 2):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅商家可创建酒款")
    pubs_service = PubsService(db)
    pub = pubs_service.get_pub(payload.pub_id)
    if current_user.role != 2 and pub.merchant_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限为该酒馆添加酒款")
    service = BeerInventoryService(db)
    beer = service.create_beer(BeerCreateDTO(**payload.model_dump()))
    return _to_beer_response(beer)


@router.get("/beers/{beer_id}", response_model=BeerResponse)
def get_beer(beer_id: int, db: Session = Depends(get_db)):
    service = BeerInventoryService(db)
    beer = service.get_beer(beer_id)
    return _to_beer_response(beer)


@router.put("/beers/{beer_id}", response_model=BeerResponse)
def update_beer(
    beer_id: int,
    payload: BeerUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in (1, 2):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅商家可修改酒款")
    service = BeerInventoryService(db)
    beer = service.get_beer(beer_id)
    pubs_service = PubsService(db)
    pub = pubs_service.get_pub(beer.pub_id)
    if current_user.role != 2 and pub.merchant_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改该酒馆酒款")
    beer = service.update_beer(beer_id, BeerUpdateDTO(**payload.model_dump()))
    return _to_beer_response(beer)


@router.delete("/beers/{beer_id}")
def delete_beer(
    beer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in (1, 2):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅商家可删除酒款")
    service = BeerInventoryService(db)
    beer = service.get_beer(beer_id)
    pubs_service = PubsService(db)
    pub = pubs_service.get_pub(beer.pub_id)
    if current_user.role != 2 and pub.merchant_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限删除该酒馆酒款")
    service.delete_beer(beer_id)
    return {"deleted": True}


@router.get("/beers", response_model=BeerListResponse)
def search_beers(
    keyword: Optional[str] = None,
    pub_id: Optional[int] = None,
    status: Optional[int] = None,
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    service = BeerInventoryService(db)
    dto = BeerSearchDTO(keyword=keyword, pub_id=pub_id, status=status, offset=offset, limit=limit)
    beers = service.search_beers(dto)
    return {
        "items": [_to_beer_response(b) for b in beers],
        "offset": offset,
        "limit": limit,
    }


@router.get("/beers/by-style", response_model=BeerStyleSearchResponse)
def search_beers_by_style(
    style: str,
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    service = BeerInventoryService(db)
    rows = service.search_beers_by_style(style, offset, limit)
    items = []
    for beer, pub in rows:
        items.append(
            {
                "beer": _to_beer_response(beer),
                "pub": {
                    "id": pub.id,
                    "merchant_user_id": pub.merchant_user_id,
                    "pub_name": pub.pub_name,
                    "cover_url": pub.cover_url,
                    "address": pub.address,
                    "longitude": float(pub.longitude) if pub.longitude is not None else None,
                    "latitude": float(pub.latitude) if pub.latitude is not None else None,
                    "contact_phone": pub.contact_phone,
                    "business_hours": pub.business_hours,
                    "status": pub.status,
                },
            }
        )
    return {"items": items, "offset": offset, "limit": limit}
