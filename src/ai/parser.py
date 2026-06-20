import json
from typing import List, Dict


def parse_recommendation(content: str) -> List[Dict[str, str]]:
    try:
        data = json.loads(content)
    except Exception as exc:  # pragma: no cover - runtime safety
        raise ValueError("大模型返回格式不正确") from exc
    if not isinstance(data, list):
        raise ValueError("大模型返回格式不正确")
    return data