from typing import List, Dict

import requests

from configs.settings import settings
from ai.prompt import build_recommend_prompt
from ai.parser import parse_recommendation


class LLMClient:
    def __init__(self) -> None:
        self.api_url = settings.llm_api_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model

    def recommend(
        self, mood: str, tastes: List[str], scene: str, style: str, context: List[str] | None = None
    ) -> List[Dict[str, str]]:
        prompt = build_recommend_prompt(mood, tastes, scene, style, context=context)
        if not self.api_url:
            return _fallback_items()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是专业精酿侍酒师。输出严格 JSON。"},
                {"role": "user", "content": prompt},
            ],
            "thinking": {"type": "disabled"},          # 关闭思考，极速响应
            "response_format": {"type": "json_object"}, # 约束 JSON 输出
            "temperature": 0.4,
            "max_tokens": 2048,                         # 3 款推荐，1024 足够
        }
        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        print("URL:", self.api_url)
        print("MODEL:", self.model)
        print("STATUS:", resp.status_code)
        print("TEXT:", resp.text)
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return parse_recommendation(content)


def _fallback_items() -> List[Dict[str, str]]:
    return [
        {
            "beer_name": "鹅岛 IPA",
            "brewery_name": "Goose Island",
            "reason": "经典美式IPA，苦味与柑橘香平衡，适合放松小酌。",
        },
        {
            "beer_name": "角鲨头 60分钟IPA",
            "brewery_name": "Dogfish Head",
            "reason": "酒体扎实、松脂香明显，适合重口味偏好。",
        },
        {
            "beer_name": "酿酒狗 朋克IPA",
            "brewery_name": "BrewDog",
            "reason": "麦香与果香兼具，适合聚会氛围。",
        },
    ]