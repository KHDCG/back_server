from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes.route import router
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from routes.route import router as inference_router
import base64
import httpx
from worker.inference_worker import inference_worker
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("[BACKGROUND] Startup event started.", flush=True)  # 시작 메시지
    # 비동기 Worker 실행
    app.state.worker_task = asyncio.create_task(inference_worker())
    print("[BACKGROUND] Worker started.", flush=True)  # 워커 시작 확인

# 서버 종료 시 실행할 작업 정의
@app.on_event("shutdown")
async def shutdown_event():
    print("[BACKGROUND] Shutdown event started.", flush=True)  # 종료 메시지
    app.state.worker_task.cancel() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
