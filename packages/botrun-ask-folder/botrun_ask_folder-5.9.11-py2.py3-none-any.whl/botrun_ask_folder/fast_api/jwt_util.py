from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN = os.getenv("BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN")


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    tokens = os.getenv("BOTRUN_API_TOKENS").strip().strip('"').split("\n")
    if credentials.credentials in tokens:
        return True
    if credentials.credentials != BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True
