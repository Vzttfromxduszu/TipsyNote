from sqlalchemy import BigInteger, String, SmallInteger, Column, DateTime, DECIMAL, ForeignKey, Index, Integer
from sqlalchemy.sql import func

from .base import Base


class BeerInventory(Base):
    __tablename__ = "beer_inventory"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pub_id = Column(BigInteger, ForeignKey("pubs.id"), nullable=False)
    beer_name = Column(String(100), nullable=False)
    brewery_name = Column(String(100), nullable=False)
    style = Column(String(50), nullable=True)
    abv = Column(DECIMAL(4, 2), nullable=True)
    volume_ml = Column(Integer, nullable=True)
    price = Column(DECIMAL(8, 2), nullable=True)
    status = Column(SmallInteger, nullable=False, default=1)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_beer_name", "beer_name"),
        Index("idx_brewery_name", "brewery_name"),
    )
