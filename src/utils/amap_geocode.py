from typing import Optional, Tuple
from typing import Any
import requests

from configs.settings import settings


def geocode_address(address: str, city: Optional[str] = None) -> Tuple[float, float]:
    if not settings.amap_key:
        raise ValueError("AMAP_KEY 未设置")
    params = {
        "key": settings.amap_key,
        "address": address,
        "output": "JSON",
    }
    if city:
        params["city"] = city
    resp = requests.get(settings.amap_geocode_url, params=params, timeout=5)
    data = resp.json()
    if str(data.get("status")) != "1":
        raise ValueError(f"高德地理编码失败: {data.get('info')}")
    geocodes = data.get("geocodes") or []
    if not geocodes:
        raise ValueError("高德地理编码无结果")
    location = geocodes[0].get("location")
    if not location or "," not in location:
        raise ValueError("高德地理编码返回坐标无效")
    lng_str, lat_str = location.split(",", 1)
    return float(lng_str), float(lat_str)

def reverse_geocode(lng: float, lat: float) -> dict[str, Any]:
    """
    高德逆地理编码

    返回适合中文展示的地址：
    例如：
    广东省深圳市南山区粤海街道深圳大学
    """

    if not settings.amap_key:
        raise ValueError("AMAP_KEY 未设置")

    params = {
        "key": settings.amap_key,
        "location": f"{lng},{lat}",
        "output": "JSON",
        "extensions": "base",
    }

    try:
        resp = requests.get(
            settings.amap_reverse_geocode_url,
            params=params,
            timeout=5,
        )

        resp.raise_for_status()

        data = resp.json()

    except requests.RequestException as e:
        raise ValueError(f"高德逆地理编码请求失败: {str(e)}")

    if str(data.get("status")) != "1":
        raise ValueError(f"高德逆地理编码失败: {data.get('info')}")

    regeocode = data.get("regeocode")

    if not regeocode:
        raise ValueError("高德逆地理编码无结果")

    address_component = regeocode.get("addressComponent", {})

    province = address_component.get("province", "")
    city = address_component.get("city", "")
    district = address_component.get("district", "")
    township = address_component.get("township", "")

    if isinstance(city, list):
        city = ""

    if not city:
        city = province

    neighborhood = address_component.get("neighborhood", {})
    neighborhood_name = neighborhood.get("name", "")
    building = address_component.get("building", {})
    building_name = building.get("name", "")
    street_number = address_component.get("streetNumber", {})
    street = street_number.get("street", "")
    number = street_number.get("number", "")

    # ==========
    # 中文自然地址生成
    # 优先级：
    # 社区 > 建筑 > 门牌
    # ==========
    detail = ""

    if neighborhood_name:
        detail = neighborhood_name

    elif building_name:
        detail = building_name

    elif street:
        detail = street + number

    display_address = "".join(
        filter(
            None,
            [
                province,
                city if city != province else "",
                district,
                township,
                detail,
            ],
        )
    )

    return {
        "address": display_address,
        "province": province,
        "city": city,
        "district": district,
        "township": township,
        "detail": detail,
        "location": {
            "lng": lng,
            "lat": lat,
        },
    }
