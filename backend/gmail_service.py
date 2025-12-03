import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(__file__)
CREDENTIAL_DIR = os.path.join(BASE_DIR, "gmail_credentials")

TOKEN_PATH = os.path.join(CREDENTIAL_DIR, "token.json")
CLIENT_SECRET_PATH = os.path.join(CREDENTIAL_DIR, "client_secret.json")

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    service = build("gmail", "v1", credentials=creds)
    return service


def fetch_inbox_messages(max_results=20):
    service = get_gmail_service()

    res = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        labelIds=["INBOX"]
    ).execute()

    messages = res.get("messages", [])
    result = []

    for msg in messages:
        detail = service.users().messages().get(userId="me", id=msg["id"]).execute()
        payload = detail.get("payload", {})
        headers = payload.get("headers", [])

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")
        snippet = detail.get("snippet", "")

        result.append({
            "id": msg["id"],
            "from": sender,
            "subject": subject,
            "snippet": snippet,
        })

    return result
