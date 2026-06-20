from sqlalchemy import BigInteger, String, Column, DateTime, Text, DECIMAL, SmallInteger, ForeignKey
from sqlalchemy.sql import func

from .base import Base


class BeerItem(Base):
    """具体酒款知识库"""
    __tablename__ = "beer_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, comment="酒款中文名")
    name_en = Column(String(256), nullable=True, comment="酒款英文名")
    brewery = Column(String(128), nullable=True, comment="酒厂/品牌")
    country = Column(String(64), nullable=True, comment="产地国家")
    style_id = Column(BigInteger, ForeignKey("beer_styles.id"), nullable=True, comment="所属风格品类")
    description = Column(Text, nullable=True, comment="酒款描述/风味介绍")
    abv = Column(DECIMAL(4, 1), nullable=True, comment="酒精度 ABV")
    ibu = Column(SmallInteger, nullable=True, comment="苦度 IBU")
    og = Column(DECIMAL(5, 2), nullable=True, comment="原麦汁浓度 °P")
    image_url = Column(String(512), nullable=True, comment="酒标图片")
    flavor_tags = Column(String(256), nullable=True, comment="风味标签，逗号分隔")
    is_classic = Column(SmallInteger, nullable=False, default=0, comment="是否经典代表作: 1=是")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
