from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.database import init_db


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1_STR)

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app.mount("/assets", StaticFiles(directory=WEB_DIR / "assets"), name="assets")
app.mount("/web-static", StaticFiles(directory=WEB_DIR), name="web-static")


@app.get("/")
def root():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "database": settings.DATABASE_URL,
    }

@app.get("/app")
def app_frontend():
    return FileResponse(WEB_DIR / "index.html")

@app.get("/app/{asset_path:path}")
def app_assets(asset_path: str):
    requested = (WEB_DIR / asset_path).resolve()
    if WEB_DIR.resolve() not in requested.parents and requested != WEB_DIR.resolve():
        raise HTTPException(status_code=404, detail="Asset not found")
    if requested.is_file():
        return FileResponse(requested)
    raise HTTPException(status_code=404, detail="Asset not found")
