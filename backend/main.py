# backend/main.py

import os
import requests
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from gemini_extractor import extract_with_gemini
from geocoding import geocode_place
from gmail_service import fetch_inbox_messages


# -----------------------
# ① .env を読み込み
# -----------------------
load_dotenv()
API_SECRET = os.environ.get("API_SECRET")


# -----------------------
# ② アプリ本体
# -----------------------
app = FastAPI()


# -----------------------
# ③ APIキーチェック
# -----------------------
def require_api_key(x_api_key: str = Header(None)):
    if API_SECRET is None:
        raise HTTPException(500, "API_SECRET not set")

    if x_api_key != API_SECRET:
        raise HTTPException(401, "Unauthorized")


# -----------------------
# ④ CORS（開発用）
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://shuhei-yamamoto-app.github.io"
    ],
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)


# -----------------------
# ⑤ Gemini API
# -----------------------
class ExtractRequest(BaseModel):
    text: str

class ExtractResponse(BaseModel):
    places: list[str]
    times: list[str] = []
    actions: list[str] = []

@app.post("/extract_with_gemini", response_model=ExtractResponse)
def extract_place_gemini(req: ExtractRequest):
    result = extract_with_gemini(req.text)
    return ExtractResponse(
        places=result.get("places", []),
        times=result.get("times", []),
        actions=result.get("actions", []),
    )


# -----------------------
# ⑥ Google Maps JS を代理配信
# -----------------------
@app.get("/maps-js")
def serve_maps_js():
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

    if not api_key:
        return Response(
            "console.error('GOOGLE_MAPS_API_KEY not set');",
            media_type="application/javascript"
        )

    url = (
        "https://maps.googleapis.com/maps/api/js"
        f"?key={api_key}"
        "&callback=initMap"
        "&libraries=places,marker"
    )

    resp = requests.get(url)
    return Response(resp.text, media_type="application/javascript")


# -----------------------
# ⑦ Geocoding API
# -----------------------
class GeocodeRequest(BaseModel):
    place: str

class GeocodeResponse(BaseModel):
    lat: float
    lng: float
    formatted_address: str | None = None

@app.post("/geocode", response_model=GeocodeResponse)
async def geocode(req: GeocodeRequest):
    result = await geocode_place(req.place)
    if result is None:
        raise HTTPException(400, "Geocoding failed")
    return result

@app.get("/gmail/inbox")
def get_gmail_inbox():
    try:
        inbox = fetch_inbox_messages(max_results=30)
        return {"messages": inbox}
    except Exception as e:
        return {"error": str(e)}


# -----------------------
# ⑧ 最後に frontend をルートにマウント
# -----------------------
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")