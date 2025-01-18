import os
import json
import random
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from llama_cpp import Llama
from typing import List
from google.cloud import storage
from google.oauth2 import service_account
from dotenv import load_dotenv
from supabase import create_client

# .env ファイルをロード
load_dotenv()

# FastAPI アプリケーションの初期化
app = FastAPI()

# GCP 設定
PROJECT_ID = "ogirin-prod"
BUCKET_NAME = "ogirin-model"
LOCAL_MODEL_DIR = "/tmp/models"

GCS_BASE_MODEL_PATH = "generator/base/base-odai.gguf"
LOCAL_BASE_MODEL_PATH = os.path.join(LOCAL_MODEL_DIR, "base.gguf")
GCS_LORA_MODEL_PATH = "generator/odai/lora-odai.gguf"
LOCAL_LORA_MODEL_PATH = os.path.join(LOCAL_MODEL_DIR, "lora.gguf")

GCP_SA_KEY = json.loads(os.getenv("GCP_SA_KEY"))

# Supabase 設定
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# モデル変数（後で初期化）
model = None

# プロンプトの準備
prompt = """

### 指示:
大喜利のお題を作成してください。

### 応答:
"""

# GCS からモデルをダウンロードする関数
def download_model_from_gcs():
    if not os.path.exists(LOCAL_MODEL_DIR):
        os.makedirs(LOCAL_MODEL_DIR)  # ディレクトリがなければ作成
        
    credential = service_account.Credentials.from_service_account_info(GCP_SA_KEY)
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
    # モデルをダウンロード
    download_model_from_gcs()

    # モデルをロード
    global model
    model = Llama(
        model_path=LOCAL_BASE_MODEL_PATH,
        lora_path=LOCAL_LORA_MODEL_PATH,
        n_ctx=200, 
        n_gpu_layers=-1,
    )
    print("Model loaded successfully.")

# リクエストボディのスキーマ定義
class Request(BaseModel):
    number: int # 生成する応答の数

# 応答取得関数
def generate_odai(number: int) -> str:
    formatted_messages = [{"role": "user", "content": prompt}] # モデル用の入力形式に変換

    odai_list = []
    while True:
        response = model.create_chat_completion(
            messages=formatted_messages, 
            max_tokens=100, 
            temperature=1.2,
        )
        content = response["choices"][0]["message"]["content"]
        if "大喜利" not in content:
            odai_list.append({"text": content})
        if len(odai_list) == number:
            break
    
    return odai_list

# supabase へのアップロード関数
def upload_to_supabase(data: List[str]) -> None:
    supabase.table("odai").insert(data).execute()

# 推論エンドポイント
@app.post("/reload_odai/", status_code=status.HTTP_201_CREATED)
def reload_odai(request: Request) -> dict:
    try:
        odai_list = generate_odai(request.number)
        upload_to_supabase(odai_list)
        return {"message": f"Successfully reloaded {request.number} odai to Supabase."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
