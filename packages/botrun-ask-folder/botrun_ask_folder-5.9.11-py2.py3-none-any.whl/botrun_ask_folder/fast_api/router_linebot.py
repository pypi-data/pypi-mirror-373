from math import e
from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel
import httpx
import os
import hmac
import hashlib
import base64
import json
from dotenv import load_dotenv
from google.cloud import firestore
from google.oauth2 import service_account
from botrun_ask_folder.models.line_bot_user_setting import LineBotUserSetting
from botrun_ask_folder.botrun_reader import read_botrun_content
from litellm import completion

load_dotenv()

linebot_router = APIRouter(prefix="/botrun_ask_folder", tags=["botrun_ask_folder"])

CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# Firestore setup
google_service_account_key_path = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI",
    "/app/keys/scoop-386004-d22d99a7afd9.json",
)
credentials = service_account.Credentials.from_service_account_file(
    google_service_account_key_path,
    scopes=["https://www.googleapis.com/auth/datastore"],
)
db = firestore.Client(credentials=credentials)
user_settings_collection = db.collection("line_bot_user_settings")


class LineMessage(BaseModel):
    events: list


@linebot_router.post("/linebot/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    body_str = body.decode("utf-8")

    # Verify the signature
    hash = hmac.new(CHANNEL_SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    signature = base64.b64encode(hash).decode("utf-8")

    if signature != x_line_signature:
        raise HTTPException(status_code=400, detail="Invalid signature")

    data = json.loads(body_str)
    await handle_events(data["events"])

    return "OK"


async def handle_events(events):
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_id = event["source"]["userId"]
            message_text = event["message"]["text"]

            user_setting = await get_or_create_user_setting(user_id)
            if user_setting.model_name == "":
                if check_model_exists(message_text):
                    user_setting.model_name = message_text
                    await update_user_setting(user_setting)
                    response_message = f"😚 已更新為使用：{message_text}"
                else:
                    response_message = (
                        "🫠 找不到你輸入的波通鑑名稱耶，請重新輸入我再找找看唷~~"
                    )
            elif message_text == "重置波通鑑":
                user_setting.model_name = ""
                user_setting.chat_history = []
                await update_user_setting(user_setting)
                response_message = "🙂 請輸入您想使用的波通鑑名稱："
            else:
                response_message = query_response(message_text, user_setting)
                user_setting.add_chat_entry(message_text, response_message)
                await update_user_setting(user_setting)

            await reply_message(event["replyToken"], response_message)


def query_response(message_text: str, user_setting: LineBotUserSetting) -> str:
    api_base = "http://dev.botrun.ai:4000"
    try:
        messages = []
        for entry in user_setting.chat_history:
            messages.append({"content": entry["user"], "role": "user"})
            messages.append({"content": entry["assistant"], "role": "assistant"})
        messages.append({"content": message_text, "role": "user"})

        response = completion(
            model=f"botrun/botrun-{user_setting.model_name}",
            custom_llm_provider="openai",
            messages=messages,
            base_url=api_base,
            api_key=os.getenv("BOTRUN_API_KEY"),
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"🙇‍♂️ 不知道發生了什麼問題，請告訴我們，我們會盡快修正 {e}"


async def get_or_create_user_setting(user_id: str) -> LineBotUserSetting:
    doc_ref = user_settings_collection.document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return LineBotUserSetting(**doc.to_dict())
    else:
        new_setting = LineBotUserSetting(user_id=user_id)
        doc_ref.set(new_setting.model_dump())
        return new_setting


async def update_user_setting(user_setting: LineBotUserSetting):
    user_setting.refresh_timestamp()
    doc_ref = user_settings_collection.document(user_setting.user_id)
    doc_ref.set(user_setting.model_dump())


async def reply_message(reply_token, message):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    data = {"replyToken": reply_token, "messages": [{"type": "text", "text": message}]}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)

    if response.status_code != 200:
        print(f"Error sending message: {response.text}")


def check_model_exists(model_name: str) -> bool:
    # 這裡是一個模擬檢查模型是否存在的函數
    # 在實際應用中，你需要實現真正的檢查邏輯
    try:
        folder_id = os.environ.get("GOOGLE_DRIVE_BOTS_FOLDER_ID")
        file_content = read_botrun_content(model_name, folder_id)
        return True
    except Exception as e:
        print(f"Error: linebot mock_check_model_exists error: {e}")
        return False
