from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import uvicorn

from configs.settings import settings

from api.users import router as users_router
from api.auth import router as auth_router
from api.pubs import router as pubs_router
from api.beer_inventory import router as beer_inventory_router
from api.ai import router as ai_router
from api.location import router as location_router
from api.posts import router as posts_router
from api.comments import router as comments_router
from api.likes import router as likes_router
from api.beer_wiki import router as beer_wiki_router
from db.session import get_session_factory
from services.pubs_service import PubsService

app = FastAPI(title="酒馆项目 API", version="0.1.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(users_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(pubs_router, prefix="/api")
app.include_router(beer_inventory_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(location_router, prefix="/api")
app.include_router(posts_router, prefix="/api")
app.include_router(comments_router, prefix="/api")
app.include_router(likes_router, prefix="/api")
app.include_router(beer_wiki_router, prefix="/api")

# 挂载头像静态文件目录，使前端可通过 /api/avatars/xxx.jpg 访问
avatars_dir = Path(settings.storage_path) / "avatars"
avatars_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/avatars", StaticFiles(directory=str(avatars_dir)), name="avatars")

# 挂载酒馆封面静态文件目录
covers_dir = Path(settings.storage_path) / "covers"
covers_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/covers", StaticFiles(directory=str(covers_dir)), name="covers")


@app.on_event("startup")
def sync_redis_geo_on_startup() -> None:
	SessionLocal = get_session_factory()
	with SessionLocal() as session:
		service = PubsService(session)
		service.sync_geo_to_redis()


if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
