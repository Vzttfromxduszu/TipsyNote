from sqlalchemy import BigInteger, String, SmallInteger, Column, DateTime, DECIMAL, ForeignKey, Index
from sqlalchemy.sql import func

from .base import Base


class Pub(Base):
    __tablename__ = "pubs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    pub_name = Column(String(100), nullable=False)
    cover_url = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    longitude = Column(DECIMAL(10, 6), nullable=True)
    latitude = Column(DECIMAL(10, 6), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    business_hours = Column(String(50), nullable=True)
    status = Column(SmallInteger, nullable=False, default=1)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    score = Column(DECIMAL(3, 2), nullable=True)
    __table_args__ = (
        Index("idx_pubs_pub_name", "pub_name"),
    )
