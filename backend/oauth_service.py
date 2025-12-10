import os
import json
import requests
from fastapi.responses import RedirectResponse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# --- OAuth 設定 ---
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

# 本番用 Redirect URI
REDIRECT_URI = "https://geo-memory-support-backend.onrender.com/oauth/callback"


# --- OAuth 認証画面へリダイレクト ---
def start_gmail_oauth():
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=https://www.googleapis.com/auth/gmail.readonly"
        "&access_type=offline"
        "&prompt=consent"
    )
    return RedirectResponse(auth_url)


# --- 認可コードを token.json に交換 ---
def handle_oauth_callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    res = requests.post(token_url, data=data)
    token_json = res.json()

    # 保存場所
    user_token_dir = os.path.join(os.path.dirname(__file__), "user_tokens")
    os.makedirs(user_token_dir, exist_ok=True)

    with open(os.path.join(user_token_dir, "user1_token.json"), "w", encoding="utf-8") as f:
        json.dump(token_json, f, indent=2)

    return token_json


# --- Gmail メール取得 ---
def fetch_gmail_inbox():
    token_path = os.path.join(os.path.dirname(__file__), "user_tokens", "user1_token.json")

    if not os.path.exists(token_path):
        return {"error": "Gmail is not linked yet."}

    creds = Credentials.from_authorized_user_file(token_path, ["https://www.googleapis.com/auth/gmail.readonly"])
    service = build("gmail", "v1", credentials=creds)

    res = service.users().messages().list(userId="me", maxResults=20).execute()
    messages = res.get("messages", [])

    result = []
    for msg in messages:
        detail = service.users().messages().get(userId="me", id=msg["id"]).execute()
        snippet = detail.get("snippet", "")
        result.append({
            "id": msg["id"],
            "snippet": snippet
        })

    return {"messages": result}
