import requests

# APIキー
API_KEY = "AIzaSyD3WNScnn-isW33gRgHSkN5uOrBZjVUH4o"

# エンドポイントURL
url = "https://gemini.googleapis.com/v1/some_endpoint"

# リクエストヘッダー
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# リクエストデータ（例）
data = {
    "input": "Hello, Gemini!"
}

response = requests.post(url, json=data, headers=headers)

# レスポンスを表示
print(response.json())