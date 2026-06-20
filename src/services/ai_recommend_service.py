from typing import List, Dict
import json

from sqlalchemy.orm import Session

from dtos.ai import AIRecommendDTO
from models.ai_recommend_log import AIRecommendLog
from repositories.ai_recommend_logs_repository import AIRecommendLogsRepository
from ai.client import LLMClient
from ai.retriever import retrieve_beer_context


class AIRecommendService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = AIRecommendLogsRepository(session)
        self.llm = LLMClient()

    def recommend(self, user_id: int, dto: AIRecommendDTO) -> List[Dict[str, str]]:
        context = retrieve_beer_context(self.session, dto.mood, dto.tastes, dto.scene, dto.style)
        items = self.llm.recommend(dto.mood, dto.tastes, dto.scene, dto.style, context=context)
        log = AIRecommendLog(
            user_id=user_id,
            prompt_tags=json.dumps(
                {
                    "mood": dto.mood,
                    "tastes": dto.tastes,
                    "scene": dto.scene,
                    "style": dto.style,
                },
                ensure_ascii=False,
            ),
            ai_response=json.dumps(items, ensure_ascii=False),
        )
        self.repo.create(log)
        self.session.commit()
        return items
