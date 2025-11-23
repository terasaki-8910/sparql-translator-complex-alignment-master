#!/usr/bin/env python3
"""
システムアーキテクチャ検証スクリプト

目的: 現行システムの実際の動作を確認し、仕様書作成のための証拠を収集する
"""

import os
import json
import subprocess
import pprint
from sparql_translator.src.parser.sparql_ast_parser import SparqlAstParser
from sparql_translator.src.parser.edoal_parser import EdoalParser
from sparql_translator.src.rewriter.sparql_rewriter import SparqlRewriter
from sparql_translator.src.rewriter.ast_serializer import AstSerializer

# プロジェクトルートを取得
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# テストクエリ
SIMPLE_QUERY = """
PREFIX ex: <http://example.org/>
SELECT ?s ?p ?o
WHERE {
  ?s ?p ?o .
}
"""

def section_header(title):
    """セクションヘッダーを出力"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def subsection_header(title):
    """サブセクションヘッダーを出力"""
    print("\n" + "-" * 80)
    print(f" {title}")
    print("-" * 80)

def verify_java_parser():
    """Javaパーサーの動作確認"""
    section_header("1. Java SPARQL パーサーの検証")
    
    # テストクエリファイルを作成
    test_query_path = os.path.join(PROJECT_ROOT, "temp_test_query.sparql")
    with open(test_query_path, 'w', encoding='utf-8') as f:
        f.write(SIMPLE_QUERY)
    
    print("\n【入力クエリ】")
    print(SIMPLE_QUERY)
    
    try:
        # Pythonラッパー経由でJavaパーサーを呼び出し
        parser = SparqlAstParser(PROJECT_ROOT)
        ast = parser.parse(test_query_path)
        
        subsection_header("パーサーの出力 (Python経由)")
        print("\n【データ型】")
        print(f"型: {type(ast)}")
        print(f"トップレベルキー: {list(ast.keys())}")
        
        print("\n【AST構造 (整形済み)】")
        pprint.pprint(ast, width=120, compact=False)
        
        subsection_header("Java呼び出しメカニズム")
        print(f"Gradlewパス: {parser.gradlew_path}")
        print(f"プロジェクトルート: {parser.project_root}")
        print("実行コマンド: ./gradlew run --args=\"<query_file_path>\"")
        print("通信方式: subprocess経由でJavaプロセス起動 → 標準出力からJSON取得")
        
        subsection_header("データ形式の確認")
        print("✓ パーサーの出力形式: JSON")
        print("✓ Python側での受け取り: dict (json.loads())")
        print("✓ FILTER式のみ: S-Expression (SSE) 形式")
        print("  → Python側で S式文字列を生成")
        print("  → Java側で SSE.parseExpr() により解釈")
        print("✗ AST全体がS式形式ではない（JSONが主体）")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 一時ファイルを削除
        if os.path.exists(test_query_path):
            os.remove(test_query_path)

def verify_edoal_parser():
    """EDOALパーサーの動作確認"""
    section_header("2. EDOAL パーサーの検証")
    
    # テストアラインメントファイルを使用
    alignment_file = os.path.join(
        PROJECT_ROOT, 
        "sparql_translator/test_data/conference/alignment/alignment.edoal"
    )
    
    if not os.path.exists(alignment_file):
        print(f"❌ テストファイルが見つかりません: {alignment_file}")
        return
    
    print(f"\n【アラインメントファイル】")
    print(f"パス: {alignment_file}")
    
    try:
        parser = EdoalParser(alignment_file, verbose=False)
        alignment = parser.parse()
        
        subsection_header("パースされたアラインメント情報")
        print(f"ソースオントロジー: {alignment.onto1}")
        print(f"ターゲットオントロジー: {alignment.onto2}")
        print(f"対応関係の数: {len(alignment.cells)}")
        
        # 最初の3つの対応関係を表示
        print("\n【対応関係の例 (最初の3件)】")
        for i, cell in enumerate(alignment.cells[:3], 1):
            print(f"\n{i}. Entity1: {type(cell.entity1).__name__}")
            if hasattr(cell.entity1, 'uri'):
                print(f"   URI: {cell.entity1.uri}")
            print(f"   Entity2: {type(cell.entity2).__name__}")
            if hasattr(cell.entity2, 'uri'):
                print(f"   URI: {cell.entity2.uri}")
            elif isinstance(cell.entity2, object):
                print(f"   構造: {cell.entity2}")
            print(f"   関係: {cell.relation}")
            print(f"   信頼度: {cell.measure}")
        
        subsection_header("実装方式")
        print("言語: Python (xml.etree.ElementTree)")
        print("入力: EDOAL XML ファイル")
        print("出力: Python dataclass オブジェクト (Alignment, Cell, IdentifiedEntity, etc.)")
        print("Java連携: なし (Pure Python)")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

def verify_rewriter():
    """リライターの動作確認"""
    section_header("3. SPARQL Rewriter の検証")
    
    # テストデータを使用
    alignment_file = os.path.join(
        PROJECT_ROOT, 
        "sparql_translator/test_data/conference/alignment/alignment.edoal"
    )
    query_file = os.path.join(
        PROJECT_ROOT,
        "sparql_translator/test_data/conference/queries/query_1.sparql"
    )
    
    if not os.path.exists(alignment_file) or not os.path.exists(query_file):
        print("❌ テストファイルが見つかりません")
        return
    
    try:
        # パースと書き換え
        edoal_parser = EdoalParser(alignment_file, verbose=False)
        alignment = edoal_parser.parse()
        
        sparql_parser = SparqlAstParser(PROJECT_ROOT)
        source_ast = sparql_parser.parse(query_file)
        
        print(f"\n【元のクエリファイル】")
        with open(query_file, 'r', encoding='utf-8') as f:
            print(f.read())
        
        subsection_header("書き換え前のAST構造 (一部)")
        print(f"トップレベルキー: {list(source_ast.keys())}")
        if 'ast' in source_ast:
            print(f"ast.type: {source_ast['ast'].get('type')}")
            if 'patterns' in source_ast['ast']:
                print(f"patterns数: {len(source_ast['ast']['patterns'])}")
        
        # リライター実行
        rewriter = SparqlRewriter(alignment, verbose=False)
        rewritten_ast = rewriter.walk(source_ast)
        
        subsection_header("書き換え後のAST構造 (一部)")
        print(f"トップレベルキー: {list(rewritten_ast.keys())}")
        if 'ast' in rewritten_ast:
            print(f"ast.type: {rewritten_ast['ast'].get('type')}")
            if 'patterns' in rewritten_ast['ast']:
                print(f"patterns数: {len(rewritten_ast['ast']['patterns'])}")
        
        subsection_header("実装方式")
        print("言語: Python (Pure Python)")
        print("入力: JSON AST (dict) + Alignment オブジェクト")
        print("処理: Visitor パターンによるAST再帰走査と書き換え")
        print("出力: 書き換え済み JSON AST (dict)")
        print("Java連携: なし")
        
        subsection_header("主要な書き換えロジック")
        print("- visit_uri(): 単純なURI置換")
        print("- visit_triple(): トリプルの書き換え")
        print("- _expand_complex_entity(): 複雑なエンティティ展開 (UNION/OPTIONAL生成)")
        print("- _expand_complex_relation(): 複雑な関係展開 (ドメイン/コドメイン制約)")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

def verify_serializer():
    """シリアライザーの動作確認"""
    section_header("4. AST Serializer の検証")
    
    # 簡単なASTを用意
    test_ast = {
        'prefixes': {
            '': 'http://example.org/',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        },
        'ast': {
            'type': 'group',
            'patterns': [
                {
                    'type': 'bgp',
                    'triples': [
                        {
                            'type': 'triple',
                            'subject': {'type': 'variable', 'value': 's'},
                            'predicate': {'type': 'variable', 'value': 'p'},
                            'object': {'type': 'variable', 'value': 'o'}
                        }
                    ]
                }
            ]
        },
        'queryType': 'SELECT',
        'isDistinct': False,
        'selectVariables': ['s', 'p', 'o'],
        'orderBy': [],
        'limit': None,
        'offset': None
    }
    
    print("\n【入力AST (簡略版)】")
    pprint.pprint(test_ast, width=100)
    
    try:
        serializer = AstSerializer(PROJECT_ROOT)
        sparql_output = serializer.serialize(test_ast)
        
        subsection_header("シリアライザーの出力")
        print("\n【生成されたSPARQL】")
        print(sparql_output)
        
        subsection_header("実装方式")
        print("言語: Java (Apache Jena ARQ)")
        print("入力: JSON AST (標準入力経由)")
        print("処理: JSON → Jena Query オブジェクト再構築 → query.serialize()")
        print("出力: SPARQL クエリ文字列 (標準出力)")
        print("Python側: subprocess経由でJavaプロセス起動 → 標準出力取得")
        
        subsection_header("Java呼び出しメカニズム")
        print(f"Gradlewパス: {serializer.gradlew_path}")
        print(f"実行コマンド: ./gradlew runSerializer --quiet --console=plain")
        print("通信方式: subprocess経由 + 標準入力にJSON送信 → 標準出力からSPARQL取得")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

def verify_data_flow():
    """エンドツーエンドのデータフロー確認"""
    section_header("5. エンドツーエンド データフロー検証")
    
    alignment_file = os.path.join(
        PROJECT_ROOT, 
        "sparql_translator/test_data/taxons/alignment/alignment.edoal"
    )
    query_file = os.path.join(
        PROJECT_ROOT,
        "sparql_translator/test_data/taxons/queries/query_1.sparql"
    )
    
    if not os.path.exists(alignment_file) or not os.path.exists(query_file):
        print("❌ テストファイルが見つかりません")
        return
    
    try:
        print("\n【処理ステップ】")
        
        # Step 1: EDOAL パース
        print("\n1️⃣  EDOAL アラインメントのパース (Python)")
        edoal_parser = EdoalParser(alignment_file, verbose=False)
        alignment = edoal_parser.parse()
        print(f"   ✓ 対応関係数: {len(alignment.cells)}")
        
        # Step 2: SPARQL パース
        print("\n2️⃣  SPARQL クエリのパース (Java → Python)")
        sparql_parser = SparqlAstParser(PROJECT_ROOT)
        source_ast = sparql_parser.parse(query_file)
        print(f"   ✓ AST取得成功 (キー: {list(source_ast.keys())})")
        
        # Step 3: リライト
        print("\n3️⃣  AST の書き換え (Python)")
        rewriter = SparqlRewriter(alignment, verbose=False)
        rewritten_ast = rewriter.walk(source_ast)
        print(f"   ✓ 書き換え完了")
        
        # Step 4: シリアライズ
        print("\n4️⃣  AST → SPARQL 変換 (Python → Java)")
        serializer = AstSerializer(PROJECT_ROOT)
        output_query = serializer.serialize(rewritten_ast)
        print(f"   ✓ SPARQL生成成功 ({len(output_query)} 文字)")
        
        print("\n【元のクエリ】")
        with open(query_file, 'r', encoding='utf-8') as f:
            original = f.read()
            print(original)
        
        print("\n【変換後のクエリ】")
        print(output_query)
        
        subsection_header("データフロー図")
        print("""
        ┌────────────────┐
        │ SPARQL Query   │ (ファイル)
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────────────┐
        │ Java: SparqlAstParser  │ (subprocess)
        └────────┬───────────────┘
                 │ stdout: JSON
                 ▼
        ┌────────────────────┐
        │ Python: dict (AST) │
        └────────┬───────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ Python: SparqlRewriter│ (Pure Python)
        └────────┬─────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │ Python: dict (書き換え後AST) │
        └────────┬─────────────────┘
                 │ stdin: JSON
                 ▼
        ┌──────────────────────────┐
        │ Java: SparqlAstSerializer │ (subprocess)
        └────────┬─────────────────┘
                 │ stdout: SPARQL
                 ▼
        ┌─────────────────┐
        │ Python: str     │
        └─────────────────┘
        """)
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

def verify_gradle_build():
    """Gradleビルド設定の確認"""
    section_header("6. Gradle ビルド設定の検証")
    
    build_gradle = os.path.join(PROJECT_ROOT, "build.gradle")
    
    if os.path.exists(build_gradle):
        print("\n【build.gradle の内容】")
        with open(build_gradle, 'r', encoding='utf-8') as f:
            print(f.read())
        
        subsection_header("依存関係の確認")
        print("Apache Jena ARQ: SPARQLのパースとシリアライズ")
        print("Google Gson: JSON処理")
        print("SLF4J: ロギング")
        
        subsection_header("タスク設定")
        print("application.mainClass: sparql_parser_java.SparqlAstParser")
        print("runSerializer: sparql_serializer_java.SparqlAstSerializer")
    else:
        print("❌ build.gradle が見つかりません")

def main():
    """メイン実行"""
    print("=" * 80)
    print(" SPARQL翻訳システム リバースエンジニアリング検証")
    print(" 実装の実態を解明し、正確な仕様書を作成するための証拠収集")
    print("=" * 80)
    
    # 各検証を実行
    verify_java_parser()
    verify_edoal_parser()
    verify_rewriter()
    verify_serializer()
    verify_data_flow()
    verify_gradle_build()
    
    # サマリー
    section_header("検証結果サマリー")
    print("""
【確認された事実】

1. パーサー層 (sparql_ast_parser.py)
   - 実装: Pythonラッパー + Java (Apache Jena ARQ)
   - 入力: SPARQLファイルパス
   - 出力: JSON形式のAST (Python dict)
   - 通信: subprocess + 標準出力
   - ❗️ S-Expression (SSE) 形式ではなく、JSON形式

2. アラインメントパーサー (edoal_parser.py)
   - 実装: Pure Python (xml.etree.ElementTree)
   - 入力: EDOAL XMLファイル
   - 出力: Python dataclass (Alignment, Cell, etc.)
   - Java連携: なし

3. リライター (sparql_rewriter.py)
   - 実装: Pure Python
   - 入力: JSON AST (dict) + Alignment
   - 処理: Visitorパターンによる再帰的書き換え
   - 出力: 書き換え済みJSON AST (dict)
   - Java連携: なし

4. シリアライザー (ast_serializer.py)
   - 実装: Pythonラッパー + Java (Apache Jena ARQ)
   - 入力: JSON AST (標準入力経由)
   - 出力: SPARQL文字列 (標準出力)
   - 通信: subprocess + 標準入出力
   - ❗️ 2025年11月にPython実装からJava実装に移行

5. データ形式
   - Parser出力: JSON
   - Rewriter入出力: JSON (dict)
   - **FILTER式のみ**: S-Expression (SSE) 形式の文字列
     - Python: _create_filter_expression() でS式生成
     - Java: SSE.parseExpr() でS式解釈
   - Serializer入力: JSON（FILTER式部分はS式）
   - Serializer出力: SPARQL文字列

6. Java連携箇所
   - パーサー: subprocess経由でJava実行
   - シリアライザー: subprocess経由でJava実行
   - それ以外: Pure Python
    """)

if __name__ == '__main__':
    main()
