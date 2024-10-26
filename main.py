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

app = FastAPI()

# templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#    return templates.TemplateResponse("upload.html", {"request": request})

# @app.post("/upload", response_class=HTMLResponse)
# async def upload_image(request: Request, file: UploadFile = File(...)):
#    contents = await file.read()
#    encoded_image = base64.b64encode(contents).decode('utf-8')
    
#    try:
#        inference_result = await inference_router.routes[0].endpoint({"img": encoded_image})
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
    
#    return templates.TemplateResponse("upload.html", {"request": request, "result": inference_result, "image": encoded_image})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
