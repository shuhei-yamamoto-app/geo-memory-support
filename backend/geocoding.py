import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


async def geocode_place(place: str):
    params = {
        "address": place,
        "key": GOOGLE_API_KEY
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(GEOCODE_URL, params=params)
        data = res.json()

    # Google API の基本チェック
    if data.get("status") != "OK":
        print("Google API status:", data.get("status"), "error:", data.get("error_message"))
        return None

    # 最初の候補を取得
    result = data["results"][0]

    lat = result["geometry"]["location"]["lat"]
    lng = result["geometry"]["location"]["lng"]
    addr = result.get("formatted_address", place)

    return {
        "lat": lat,
        "lng": lng,
        "formatted_address": addr
    }
