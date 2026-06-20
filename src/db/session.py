from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from configs.settings import settings


def get_engine() -> Engine:
    if not settings.mysql_url:
        raise RuntimeError("MYSQL_URL 未设置")
    return create_engine(settings.mysql_url, pool_pre_ping=True)


def get_session_factory():
    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
