#!/usr/bin/env python3
"""
Gemini API接続テストプログラム

このスクリプトは以下をテストします:
1. APIキーの有効性
2. 基本的なテキスト生成
3. JSON形式での応答
4. エラーメッセージの詳細表示
"""

import json
import google.generativeai as genai

# APIキー

def test_api_configuration():
    """APIの設定をテスト"""
    print("=" * 60)
    print("テスト1: API設定")
    print("=" * 60)
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✓ API設定成功")
        return True
    except Exception as e:
        print(f"✗ API設定失敗: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        return False


def test_basic_generation():
    """基本的なテキスト生成をテスト"""
    print("\n" + "=" * 60)
    print("テスト2: 基本的なテキスト生成")
    print("=" * 60)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Hello, how are you?")
        print(f"✓ 生成成功")
        print(f"応答: {response.text[:100]}...")
        return True
    except Exception as e:
        print(f"✗ 生成失敗: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        print(f"エラー詳細: {str(e)}")
        return False


def test_json_generation():
    """JSON形式での応答をテスト"""
    print("\n" + "=" * 60)
    print("テスト3: JSON形式の応答")
    print("=" * 60)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = """Respond ONLY in JSON format:
{
  "status": "success",
  "message": "This is a test"
}"""
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        print(f"生のレスポンス:\n{response_text}\n")
        
        # マークダウンコードブロックを除去
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        parsed = json.loads(response_text)
        print(f"✓ JSON解析成功")
        print(f"解析結果: {parsed}")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ JSON解析失敗: {e}")
        print(f"レスポンステキスト: {response_text}")
        return False
    except Exception as e:
        print(f"✗ 生成失敗: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        print(f"エラー詳細: {str(e)}")
        return False


def test_sparql_evaluation():
    """SPARQL評価プロンプトをテスト"""
    print("\n" + "=" * 60)
    print("テスト4: SPARQL評価プロンプト")
    print("=" * 60)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = """You are an expert in SPARQL and Ontology Alignment.
Evaluate the quality of the "Actual Output Query" by comparing it with the "Expected Output Query".

Criteria:
1. **Success**: Logically equivalent to the Expected Query.
2. **Partial Success**: Mostly correct but missing minor features.
3. **Failure**: Syntax errors or missing definitions.

Input Query:
SELECT ?x WHERE { ?x rdf:type ex:Person }

Expected Output Query:
SELECT ?x WHERE { ?x rdf:type foaf:Person }

Actual Output Query:
SELECT ?x WHERE { ?x rdf:type foaf:Person }

Respond ONLY in JSON format:
{
  "judgment": "Success" | "Partial Success" | "Failure",
  "reason": "Brief explanation"
}"""
        
        print("プロンプト送信中...")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        print(f"\n生のレスポンス:\n{response_text}\n")
        
        # マークダウンコードブロックを除去
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        parsed = json.loads(response_text)
        print(f"✓ SPARQL評価成功")
        print(f"判定: {parsed.get('judgment')}")
        print(f"理由: {parsed.get('reason')}")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ JSON解析失敗: {e}")
        print(f"レスポンステキスト: {response_text}")
        return False
    except Exception as e:
        print(f"✗ 評価失敗: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        print(f"エラー詳細: {str(e)}")
        
        # より詳細なエラー情報を表示
        if hasattr(e, 'args'):
            print(f"エラー引数: {e.args}")
        if hasattr(e, '__dict__'):
            print(f"エラー属性: {e.__dict__}")
        
        return False


def test_available_models():
    """利用可能なモデルを確認"""
    print("\n" + "=" * 60)
    print("テスト5: 利用可能なモデル一覧")
    print("=" * 60)
    try:
        models = genai.list_models()
        print("利用可能なモデル:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
        return True
    except Exception as e:
        print(f"✗ モデル一覧取得失敗: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        return False


def main():
    """全テストを実行"""
    print("\n🔍 Gemini API テストプログラム\n")
    
    results = []
    
    # テスト1: API設定
    results.append(("API設定", test_api_configuration()))
    
    if not results[0][1]:
        print("\n❌ API設定に失敗したため、以降のテストをスキップします。")
        print("\n考えられる原因:")
        print("  1. APIキーが無効または期限切れ")
        print("  2. インターネット接続の問題")
        print("  3. google-generativeai パッケージの問題")
        return
    
    # テスト2-5
    results.append(("基本生成", test_basic_generation()))
    results.append(("JSON生成", test_json_generation()))
    results.append(("SPARQL評価", test_sparql_evaluation()))
    results.append(("モデル一覧", test_available_models()))
    
    # サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    for name, result in results:
        status = "✓ 成功" if result else "✗ 失敗"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    print(f"\n合計: {passed}/{total} 成功")
    
    if passed == total:
        print("\n✅ すべてのテストが成功しました！")
    else:
        print("\n⚠️ 一部のテストが失敗しました。上記のエラーメッセージを確認してください。")
        print("\n推奨される対処法:")
        print("  1. APIキーが正しいか確認")
        print("  2. Gemini APIの利用制限を確認（https://makersuite.google.com/app/apikey）")
        print("  3. インターネット接続を確認")
        print("  4. google-generativeai パッケージを再インストール: pip install --upgrade google-generativeai")


if __name__ == '__main__':
    main()
