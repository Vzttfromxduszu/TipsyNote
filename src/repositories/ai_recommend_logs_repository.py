from sqlalchemy.orm import Session

from models.ai_recommend_log import AIRecommendLog


class AIRecommendLogsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, log: AIRecommendLog) -> AIRecommendLog:
        self.session.add(log)
        self.session.flush()
        return log
