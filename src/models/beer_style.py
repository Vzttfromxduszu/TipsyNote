from sqlalchemy import BigInteger, String, SmallInteger, Column, DateTime, Text, DECIMAL
from sqlalchemy.sql import func

from .base import Base


class BeerStyle(Base):
    """精酿啤酒风格品类（BJCP 分类简化版）"""
    __tablename__ = "beer_styles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, comment="品类中文名，如 IPA、世涛")
    name_en = Column(String(128), nullable=True, comment="英文全称")
    category = Column(String(32), nullable=False, comment="大类：艾尔/拉格/特色")
    description = Column(Text, nullable=True, comment="风格简介")
    origin_story = Column(Text, nullable=True, comment="历史起源简述")
    tasting_notes = Column(Text, nullable=True, comment="品鉴要点")
    ibu_min = Column(SmallInteger, nullable=True, comment="苦度下限")
    ibu_max = Column(SmallInteger, nullable=True, comment="苦度上限")
    srm_min = Column(SmallInteger, nullable=True, comment="色度下限")
    srm_max = Column(SmallInteger, nullable=True, comment="色度上限")
    abv_min = Column(DECIMAL(4, 1), nullable=True, comment="酒精度下限")
    abv_max = Column(DECIMAL(4, 1), nullable=True, comment="酒精度上限")
    icon = Column(String(32), nullable=True, comment="展示图标 emoji")
    sort_order = Column(SmallInteger, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
