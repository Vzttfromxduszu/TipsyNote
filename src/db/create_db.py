import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


ROOT = Path(__file__).resolve().parents[2]  # 项目根目录
sys.path.append(str(ROOT))

from models import Base  # noqa: E402
import models.user  # noqa: F401,E402
import models.pub  # noqa: F401,E402
import models.beer_inventory  # noqa: F401,E402
import models.post  # noqa: F401,E402
import models.post_like  # noqa: F401,E402
import models.post_comment  # noqa: F401,E402
import models.ai_recommend_log  # noqa: F401,E402
import models.beer_style  # noqa: F401,E402
import models.beer_item  # noqa: F401,E402


def create_database_and_tables() -> None:
    load_dotenv(dotenv_path=ROOT / ".env", override=False)
    mysql_url = os.getenv("MYSQL_URL")
    if not mysql_url:
        raise RuntimeError("MYSQL_URL 未设置")

    url = make_url(mysql_url)
    db_name = url.database or os.getenv("MYSQL_DB")
    if not db_name:
        raise RuntimeError("MYSQL_DB 未设置，且 MYSQL_URL 不包含数据库名")

    admin_url = url.set(database="mysql")
    admin_engine = create_engine(admin_url, pool_pre_ping=True)
    with admin_engine.connect() as conn:
        conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        )

    engine = create_engine(url.set(database=db_name), pool_pre_ping=True)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_database_and_tables()
