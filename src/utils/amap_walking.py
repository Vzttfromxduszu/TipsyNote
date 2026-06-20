from typing import Tuple

import requests

from configs.settings import settings


def get_walking_route(origin_lng: float, origin_lat: float, dest_lng: float, dest_lat: float) -> Tuple[float, int]:
    if not settings.amap_key:
        raise ValueError("AMAP_KEY 未设置")
    origin = f"{origin_lng:.6f},{origin_lat:.6f}"
    destination = f"{dest_lng:.6f},{dest_lat:.6f}"
    params = {
        "key": settings.amap_key,
        "origin": origin,
        "destination": destination,
        "show_fields": "cost",
        "output": "JSON",
    }
    resp = requests.get(settings.amap_walk_url, params=params, timeout=5)
    data = resp.json()
    if str(data.get("status")) != "1":
        raise ValueError(f"高德步行规划失败: {data.get('info')}")
    route = data.get("route") or {}
    paths = route.get("paths") or []
    if not paths:
        raise ValueError("高德步行规划无结果")
    path0 = paths[0]
    distance_m = float(path0.get("distance", 0))
    cost = path0.get("cost") or {}
    duration_s = int(float(cost.get("duration", 0)))
    duration_min = max(1, round(duration_s / 60)) if duration_s else 0
    return distance_m, duration_min
