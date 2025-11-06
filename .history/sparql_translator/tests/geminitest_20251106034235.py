
# APIキー
API_KEY = "AIzaSyD3WNScnn-isW33gRgHSkN5uOrBZjVUH4o"

import requests
import json
import os # osモジュールをインポート

# APIキーを環境変数から取得
# 安全性のため、キーをコードに直接書き込まないでください
# API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("エラー: 環境変数 'GEMINI_API_KEY' が設定されていません。")
    # ここでプログラムを終了するか、デフォルトの処理を行う
    exit()

# 正しいエンドポイントURL (例: gemini-1.5-flashモデルの場合)
# :generateContent がメソッド名です
model_name = "gemini-1.5-flash"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"

# リクエストヘッダー (Content-TypeのみでOK)
headers = {
    "Content-Type": "application/json"
}

# リクエストデータ (Gemini APIの仕様に合わせた形式)
data = {
    "contents": [
        {
            "parts": [
                {"text": "Hello, Gemini!"}
            ]
        }
    ]
}

# URLにAPIキーをクエリパラメータとして追加
params = {
    "key": API_KEY
}

try:
    # POSTリクエストを送信 (params引数を追加)
    response = requests.post(url, json=data, headers=headers, params=params)

    # レスポンスのステータスコードをチェック
    response.raise_for_status() # エラーがあれば例外を発生させる

    # レスポンスを表示
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

except requests.exceptions.HTTPError as err:
    print(f"HTTPエラーが発生しました: {err}")
    # エラーの詳細（APIからのレスポンス本文）を表示
    try:
        print(f"エラー詳細: {response.json()}")
    except json.JSONDecodeError:
        print(f"エラー詳細 (raw): {response.text}")
except requests.exceptions.RequestException as e:
    print(f"リクエスト中にエラーが発生しました: {e}")