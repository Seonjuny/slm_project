# app/main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import BASE_DIR
from app.routers import lodging, cheap, manage  # 필요시 chat, util 추가 가능

app = FastAPI(
    title="Local RAG Lab",
    description="Qwen2.5 14B Q4_K + FastAPI + 공공데이터 RAG 실험실",
    version="0.2.0",
)

# 라우터 등록
app.include_router(lodging.router)
app.include_router(cheap.router)
app.include_router(manage.router)


# 정적 파일
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    index_path = static_dir / "index.html"
    return index_path.read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "ok"}
