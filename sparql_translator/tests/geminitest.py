import requests
import json
import os

# APIキーを環境変数から取得
API_KEY = os.getenv("GEMINI_API_KEY")

# テスト用に直接設定する場合（本番環境では推奨されません）
# API_KEY = "YOUR_API_KEY_HERE"

if not API_KEY:
    print("エラー: 環境変数 'GEMINI_API_KEY' が設定されていません。")
    exit()

# --- 解決策: Gemini 2.0以降のモデルを使用 ---
# 以下のいずれかを選択:
model_name = "gemini-2.5-flash"        # 推奨: 最新の高速モデル
# model_name = "gemini-2.5-pro"        # より高性能
# model_name = "gemini-2.0-flash"      # 安定版
# model_name = "gemini-flash-latest"   # 常に最新の安定版を使用
# -------------------------------------------

url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"

headers = {
    "Content-Type": "application/json"
}

data = {
    "contents": [
        {
            "parts": [
                {"text": "Hello, Gemini!"}
            ]
        }
    ]
}

params = {
    "key": API_KEY
}

try:
    response = requests.post(url, json=data, headers=headers, params=params)
    response.raise_for_status() 

    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

except requests.exceptions.HTTPError as err:
    print(f"HTTPエラーが発生しました: {err}")
    try:
        print(f"エラー詳細: {response.json()}")
    except json.JSONDecodeError:
        print(f"エラー詳細 (raw): {response.text}")
except requests.exceptions.RequestException as e:
    print(f"リクエスト中にエラーが発生しました: {e}")
