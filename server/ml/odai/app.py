import os
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_cpp import Llama
from typing import List
from google.cloud import storage
from google.oauth2 import service_account
from dotenv import load_dotenv

# .env ファイルをロード
load_dotenv()

# FastAPI アプリケーションの初期化
app = FastAPI()

# GCS 設定
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
LOCAL_MODEL_DIR = os.getenv("LOCAL_MODEL_DIR")

GCS_BASE_MODEL_PATH = os.getenv("GCS_BASE_MODEL_PATH")
LOCAL_BASE_MODEL_PATH = os.path.join(LOCAL_MODEL_DIR, "base.gguf")
GCS_LORA_MODEL_PATH = os.getenv("GCS_LORA_MODEL_PATH")
LOCAL_LORA_MODEL_PATH = os.path.join(LOCAL_MODEL_DIR, "lora.gguf")

KEY_PATH = os.getenv("GCS_KEY_PATH")

# モデル変数（後で初期化）
model = None

# GCS からモデルをダウンロードする関数
def download_model_from_gcs():
    if not os.path.exists(LOCAL_MODEL_DIR):
        os.makedirs(LOCAL_MODEL_DIR)  # ディレクトリがなければ作成
        
    credential = service_account.Credentials.from_service_account_file(KEY_PATH)
    client = storage.Client(project=PROJECT_ID, credentials=credential)
    bucket = client.bucket(BUCKET_NAME)
    
    if not os.path.exists(LOCAL_BASE_MODEL_PATH):  # ベースモデルがなければダウンロード
        blob = bucket.blob(GCS_BASE_MODEL_PATH)
        blob.download_to_filename(LOCAL_BASE_MODEL_PATH)
        print(f"Base Model downloaded to {LOCAL_BASE_MODEL_PATH}")
    else:
        print("Base Model already exists locally.")

    if not os.path.exists(LOCAL_LORA_MODEL_PATH):  # LoRAモデルがなければダウンロード
        blob = bucket.blob(GCS_LORA_MODEL_PATH)
        blob.download_to_filename(LOCAL_LORA_MODEL_PATH)
        print(f"LoRA Model downloaded to {LOCAL_LORA_MODEL_PATH}")
    else:
        print("LoRA Model already exists locally.")

# FastAPI のイベントでモデルをロード
@app.on_event("startup")
def load_model():
    global model
    # モデルをダウンロード
    download_model_from_gcs()

    # モデルをロード
    model = Llama(
        model_path=LOCAL_BASE_MODEL_PATH,
        lora_path=LOCAL_LORA_MODEL_PATH,
        n_ctx=200, 
        n_gpu_layers=-1,
    )
    print("Model loaded successfully.")

# リクエストボディのスキーマ定義
class Message(BaseModel):
    role: str  # "user" または "assistant"
    content: str

class MessageRequest(BaseModel):
    messages: List[Message]  # 会話履歴のリスト

# 応答取得関数
def get_response_from_llm(messages: List[Message]) -> str:
    # モデル用の入力形式に変換
    formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

    # モデルに渡す
    response = model.create_chat_completion(
        messages=formatted_messages, 
        max_tokens=100, 
        temperature=1.2,
    )
    return response["choices"][0]["message"]["content"]

# 推論エンドポイント
@app.post("/generate_by_llm")
def generate_by_llm(request: MessageRequest):
    try:
        response = get_response_from_llm(request.messages)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# uvicorn src.app_gcs:app --host 127.0.0.1 --port 8007
