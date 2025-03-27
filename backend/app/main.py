from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ai_assist  # 加這行
from app.services.ai_engine import sync_gitlab_repo, build_faiss_index
from app.api import preview

sync_gitlab_repo()
build_faiss_index()


app = FastAPI()

# 前端跨域允許
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 掛上 API
app.include_router(ai_assist.router)

app.include_router(preview.router)