from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, SmallInteger
from sqlalchemy.sql import func

from .base import Base


class PostComment(Base):
    __tablename__ = "post_comments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey("posts.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content = Column(String(500), nullable=False)
    status = Column(SmallInteger, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
