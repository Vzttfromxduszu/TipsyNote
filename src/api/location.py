from fastapi import APIRouter, HTTPException, Query, status
from utils.amap_geocode import reverse_geocode

router = APIRouter(tags=["location"])


@router.get("/location/reverse-geocode")
def get_reverse_geocode(
    lng: float = Query(..., ge=-180, le=180),
    lat: float = Query(..., ge=-90, le=90),
):
    """
    根据经纬度获取中文地址
    """

    try:
        result = reverse_geocode(lng, lat)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="逆地理编码服务异常",
        )

    return {
        "address": result["address"],
        "province": result["province"],
        "city": result["city"],
        "district": result["district"],
        "township": result["township"],
        "location": result["location"],
    }