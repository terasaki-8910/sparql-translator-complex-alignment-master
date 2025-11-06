import requests
import json

API_KEY = "YOUR_API_KEY_HERE"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key=AIzaSyD3WNScnn-isW33gRgHSkN5uOrBZjVUH4o"

response = requests.get(url)
models = response.json()

print("利用可能なモデル:")
for model in models.get('models', []):
    if 'generateContent' in model.get('supportedGenerationMethods', []):
        print(f"- {model['name']}")
