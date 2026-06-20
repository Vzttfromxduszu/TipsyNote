from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func

from .base import Base


class AIRecommendLog(Base):
    __tablename__ = "ai_recommend_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    prompt_tags = Column(JSON, nullable=True)
    ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
