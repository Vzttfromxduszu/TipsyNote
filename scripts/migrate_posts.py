"""快速迁移：给 posts 表增加缺失列"""
import os, sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
load_dotenv(dotenv_path=ROOT / ".env", override=False)

mysql_url = os.getenv("MYSQL_URL")
if not mysql_url:
    raise RuntimeError("MYSQL_URL 未设置")

url = make_url(mysql_url)
engine = create_engine(url, pool_pre_ping=True)

# 给 posts 表增加缺失的列
alter_statements = [
    "ALTER TABLE posts ADD COLUMN title VARCHAR(256) NOT NULL DEFAULT ''",
    "ALTER TABLE posts ADD COLUMN content TEXT NOT NULL",
    "ALTER TABLE posts ADD COLUMN image_urls JSON NULL",
    "ALTER TABLE posts ADD COLUMN like_count INT NOT NULL DEFAULT 0",
    "ALTER TABLE posts ADD COLUMN comment_count INT NOT NULL DEFAULT 0",
    "ALTER TABLE posts ADD COLUMN status SMALLINT NOT NULL DEFAULT 1",
]

with engine.connect() as conn:
    for stmt in alter_statements:
        print(f"执行: {stmt[:70]}...")
        try:
            conn.execute(text(stmt))
            conn.commit()
            print("  ✓ 成功")
        except Exception as e:
            print(f"  ⚠ 跳过（可能已存在）: {e}")

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE posts ADD INDEX idx_posts_title (title)"))
        conn.commit()
        print("索引 idx_posts_title ✓")
except Exception:
    print("索引 idx_posts_title ⚠ 跳过（可能已存在）")

print("\n迁移完成！")
