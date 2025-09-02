import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()


def get_google_drive_service():
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    service_account_file = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        "/app/keys/google_service_account_key.json",
    )
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=credentials)
    return service
