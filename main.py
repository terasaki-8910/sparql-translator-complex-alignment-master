import os
import csv
import traceback
import re
import json
import time
from datetime import datetime
import google.generativeai as genai
from sparql_translator.src.parser.edoal_parser import EdoalParser
from sparql_translator.src.parser.sparql_ast_parser import SparqlAstParser
from sparql_translator.src.rewriter.sparql_rewriter import SparqlRewriter
from sparql_translator.src.rewriter.ast_serializer import AstSerializer
from sparql_translator.src.common.logger import get_logger
from dotenv import load_dotenv
"""
タスク
done: AST ➡︎ SPARQL をPythonで行うのではなく、Jenaを使って行い、その結果をPythonで受け取るように変更する。
インスタンス処理のアルゴリズム：現状パススルー
UNIONクエリの分割
Word2Vec等を使った曖昧マッチング
"""

# ============================================================
# ユーザー設定: ここを編集してデータセットを変更できます
# ============================================================

# geminiのAPIキー、無料版
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# LLM評価機能のオン/オフ
ENABLE_LLM_EVALUATION = False

# テストデータのルートディレクトリ（相対パスまたは絶対パス）
TEST_DATA_DIR = 'sparql_translator/test_data'

# 処理対象のデータセットリスト（空の場合は自動検出）
# 例: ['conference', 'taxons', 'agro-db', 'agronomic-voc']
DATASET_NAMES = []

# 出力CSVファイル名のプレフィックス
OUTPUT_CSV_PREFIX = 'translation_results'

# アラインメントファイルのディレクトリ名とファイル名
ALIGNMENT_DIR_NAME = 'alignment'
ALIGNMENT_FILE_NAME = 'alignment.edoal'

# クエリファイルのディレクトリ名
QUERIES_DIR_NAME = 'queries'

# 期待される出力ファイルのディレクトリ名
EXPECTED_OUTPUTS_DIR_NAME = 'expected_outputs'

# ============================================================


def extract_uris(query_text):
    """
    SPARQLクエリからURIを抽出する。
    <URI> 形式と、PREFIX定義から展開可能な短縮形の両方を抽出。
    """
    uris = set()
    
    # <URI> 形式のURIを抽出
    full_uri_pattern = r'<([^>]+)>'
    for match in re.finditer(full_uri_pattern, query_text):
        uri = match.group(1)
        # フィルタ: 標準的な名前空間は除外
        if not any(ns in uri for ns in ['www.w3.org', 'xmlns.com', 'purl.org/dc']):
            uris.add(uri)
    
    # PREFIX定義を解析
    prefixes = {}
    prefix_pattern = r'PREFIX\s+(\w+):\s*<([^>]+)>'
    for match in re.finditer(prefix_pattern, query_text, re.IGNORECASE):
        prefix = match.group(1)
        namespace = match.group(2)
        prefixes[prefix] = namespace
    
    # 短縮形URI（prefix:localName）を抽出して展開
    # ただし、rdf:type等の標準的なものは除外
    short_uri_pattern = r'\b(\w+):(\w+)\b'
    for match in re.finditer(short_uri_pattern, query_text):
        prefix = match.group(1)
        local_name = match.group(2)
        # 標準的なプレフィックスは除外
        if prefix in ['rdf', 'rdfs', 'owl', 'xsd', 'skos']:
            continue
        if prefix in prefixes:
            full_uri = prefixes[prefix] + local_name
            uris.add(full_uri)
    
    return uris


def evaluate_results_with_llm(results):
    """
    Google Gemini APIを使用して、変換結果を評価する。
    
    Args:
        results: 変換結果のリスト（各要素は辞書）
    
    Returns:
        評価情報が追加されたresultsリスト
    """
    # Gemini APIの設定
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    total = len(results)
    print(f"Total results to evaluate: {total}")
    
    for idx, result in enumerate(results, start=1):
        print(f"  [{idx}/{total}] Evaluating {result['query_file']}...", end=" ")
        
        # スキップ条件: output_queryが空または明白なエラー
        if not result['output_query'] or len(result['output_query'].strip()) < 10:
            result['llm_judgment'] = "Failure"
            result['llm_reason'] = "Output query is empty or too short."
            print("Skipped (empty output)")
            continue
        
        if result['error_info']:
            result['llm_judgment'] = "Failure"
            result['llm_reason'] = f"Translation error: {result['error_info'].splitlines()[-1]}"
            print("Skipped (error)")
            continue
        
        # 評価プロンプトの作成
        prompt = f"""You are an expert in SPARQL and Ontology Alignment.
Evaluate the quality of the "Actual Output Query" by comparing it with the "Expected Output Query".

Criteria:
1. **Success**: 
   - Logically equivalent to the Expected Query.
   - OR, strict adherence to EDOAL alignment rules (e.g., complex UNION structures) is considered CORRECT, even if the Expected Query is simplified.
   - Variable bindings are consistent.
   - Property paths (e.g., `+`, `*`) are handled correctly.
2. **Partial Success**: 
   - Mostly correct but missing minor features (e.g., missing transitive `+`) or redundant structure.
3. **Failure**: 
   - Syntax errors, missing variable definitions, or untranslated URIs.

Input Query:
{result['input_query']}

Expected Output Query:
{result['expected_query'] if result['expected_query'] else 'Not provided'}

Actual Output Query:
{result['output_query']}

Respond ONLY in JSON format:
{{
  "judgment": "Success" | "Partial Success" | "Failure",
  "reason": "Brief explanation"
}}"""
        
        # APIコール
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # JSON解析
            # マークダウンのコードブロックを除去
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            evaluation = json.loads(response_text)
            result['llm_judgment'] = evaluation.get('judgment', 'Error')
            result['llm_reason'] = evaluation.get('reason', 'No reason provided')
            print(f"✓ {result['llm_judgment']}")
            
        except json.JSONDecodeError as e:
            result['llm_judgment'] = "Error"
            result['llm_reason'] = f"JSON parse error: {str(e)}"
            print(f"✗ JSON error")
        except Exception as e:
            result['llm_judgment'] = "Error"
            result['llm_reason'] = f"API error: {str(e)}"
            print(f"✗ API error")
        
        # レート制限対策
        time.sleep(2)
    
    return results


def check_translation_quality(input_query, output_query, expected_query, alignment_file):
    """
    URIベースで変換の品質を判定する。
    
    判定基準:
    1. output_queryが空でない
    2. input_query固有のURIがoutput_queryに残存していない（変換が行われた）
    3. (オプション) expected_queryのターゲットURIがoutput_queryに含まれている
    
    :return: "Success" or "Failure"
    """
    # 基本チェック: output_queryが存在する
    if not output_query or len(output_query.strip()) < 10:
        return "Failure"
    
    # input_queryとoutput_queryからURIを抽出
    input_uris = extract_uris(input_query)
    output_uris = extract_uris(output_query)
    
    # アラインメントファイルから変換対象のURIを取得
    try:
        parser = EdoalParser(alignment_file)
        alignment = parser.parse()
        source_uris = set()
        target_uris = set()
        
        for cell in alignment.cells:
            # entity1（ソース）のURIを収集
            if hasattr(cell.entity1, 'uri'):
                source_uris.add(cell.entity1.uri)
            # entity2（ターゲット）のURIを収集
            if hasattr(cell.entity2, 'uri'):
                target_uris.add(cell.entity2.uri)
    except Exception:
        # アラインメント解析に失敗した場合は、単純な比較のみ
        source_uris = set()
        target_uris = set()
    
    # 判定1: 変換対象のソースURIがoutput_queryに残っていないか
    remaining_source_uris = input_uris & source_uris & output_uris
    if remaining_source_uris:
        # まだソースURIが残っている = 変換が不完全
        # ただし、すべてのソースURIが残っている場合は変換が行われていないとみなす
        if len(remaining_source_uris) == len(input_uris & source_uris):
            return "Failure"
    
    # 判定2: 何らかの変換が行われたか（URIの変化があるか）
    if input_uris == output_uris and len(input_uris) > 0:
        # URIがまったく変化していない = 変換が行われていない
        return "Failure"
    
    # 判定3: expected_queryが存在する場合、ターゲットURIの含有をチェック
    if expected_query and len(expected_query.strip()) > 10:
        expected_uris = extract_uris(expected_query)
        # ターゲットURIの多くがoutput_queryに含まれていることを確認
        if target_uris and expected_uris:
            common_target_uris = target_uris & expected_uris & output_uris
            # 少なくとも一部のターゲットURIが含まれていればOK
            if len(common_target_uris) > 0 or len(output_uris & expected_uris) > 0:
                return "Success"
    
    # デフォルト: 変換が行われた形跡があればSuccess
    return "Success"


def process_dataset(dataset_path, sparql_parser, project_root, 
                    alignment_dir_name=ALIGNMENT_DIR_NAME,
                    alignment_file_name=ALIGNMENT_FILE_NAME,
                    queries_dir_name=QUERIES_DIR_NAME,
                    expected_outputs_dir_name=EXPECTED_OUTPUTS_DIR_NAME):
    """
    単一のデータセットに対する変換処理を行う。
    
    Args:
        dataset_path: データセットのルートパス
        sparql_parser: SPARQLパーサーインスタンス
        project_root: プロジェクトのルートパス
        alignment_dir_name: アラインメントディレクトリ名
        alignment_file_name: アラインメントファイル名
        queries_dir_name: クエリディレクトリ名
        expected_outputs_dir_name: 期待される出力ディレクトリ名
    
    Returns:
        変換結果のリスト
    """
    alignment_file = os.path.join(dataset_path, alignment_dir_name, alignment_file_name)
    queries_dir = os.path.join(dataset_path, queries_dir_name)
    expected_outputs_dir = os.path.join(dataset_path, expected_outputs_dir_name)

    if not os.path.exists(alignment_file) or not os.path.exists(queries_dir):
        return []

    print(f"\n--- Processing dataset: {os.path.basename(dataset_path)} ---")
    
    try:
        edoal_parser = EdoalParser(alignment_file)
        alignment_data = edoal_parser.parse()
        print(f"Loaded {len(alignment_data.cells)} alignment cells.")
        rewriter = SparqlRewriter(alignment_data)
        serializer = AstSerializer(project_root)
    except Exception as e:
        print(f"Error parsing alignment file {alignment_file}: {e}")
        return []

    results = []
    for query_filename in sorted(os.listdir(queries_dir)):
        query_filepath = os.path.join(queries_dir, query_filename)
        if not query_filepath.endswith(".sparql"):
            continue

        # 画面表示はそのまま残す（ユーザー指示）。加えてログにも書き込む。
        print(f"  - Processing query: {query_filename}")
        try:
            # ログは append モードになるよう logger を利用
            logger = get_logger('main', verbose=False)
            logger.info(f"Processing query: {query_filename}")
        except Exception:
            # ログ失敗でも処理は継続
            pass
        
        with open(query_filepath, 'r', encoding='utf-8') as f:
            input_query = f.read()

        expected_query = ""
        expected_output_filepath = os.path.join(expected_outputs_dir, query_filename)
        if os.path.exists(expected_output_filepath):
            with open(expected_output_filepath, 'r', encoding='utf-8') as f:
                expected_query = f.read()
        
        status = "Failure"
        output_query = ""
        error_info = ""

        try:
            source_ast = sparql_parser.parse(query_filepath)
            rewritten_ast = rewriter.walk(source_ast)
            output_query = serializer.serialize(rewritten_ast)
            
            # URIベースの成功判定ロジック
            status = check_translation_quality(input_query, output_query, expected_query, alignment_file)
            
        except Exception:
            error_info = traceback.format_exc()
            print(f"    -> Failed to translate: {error_info.splitlines()[-1]}")

        results.append({
            "dataset": os.path.basename(dataset_path),
            "alignment_file": os.path.basename(alignment_file),
            "query_file": query_filename,
            "status": status,
            "input_query": input_query,
            "output_query": output_query,
            "expected_query": expected_query,
            "error_info": error_info,
        })
    return results


def find_datasets(test_data_dir, alignment_dir_name=ALIGNMENT_DIR_NAME, queries_dir_name=QUERIES_DIR_NAME):
    """
    テストデータディレクトリから処理可能なデータセットを自動検出する。
    
    Args:
        test_data_dir: テストデータのルートディレクトリ
        alignment_dir_name: アラインメントディレクトリ名
        queries_dir_name: クエリディレクトリ名
    
    Returns:
        データセットパスのリスト
    """
    datasets = []
    for dirpath, dirnames, _ in os.walk(test_data_dir):
        # alignment と queries ディレクトリを持つものをデータセットのルートと判断
        if alignment_dir_name in dirnames and queries_dir_name in dirnames:
            datasets.append(dirpath)
            # サブディレクトリをこれ以上探索しないようにする
            dirnames[:] = []
    return datasets


def get_dataset_paths(project_root, test_data_dir, dataset_names, 
                      alignment_dir_name=ALIGNMENT_DIR_NAME,
                      queries_dir_name=QUERIES_DIR_NAME):
    """
    処理対象のデータセットパスを取得する。
    
    Args:
        project_root: プロジェクトのルートパス
        test_data_dir: テストデータのディレクトリ（相対パスまたは絶対パス）
        dataset_names: データセット名のリスト（空の場合は自動検出）
        alignment_dir_name: アラインメントディレクトリ名
        queries_dir_name: クエリディレクトリ名
    
    Returns:
        データセットパスのリスト
    """
    # テストデータディレクトリの絶対パスを取得
    if os.path.isabs(test_data_dir):
        abs_test_data_dir = test_data_dir
    else:
        abs_test_data_dir = os.path.join(project_root, test_data_dir)
    
    if not os.path.exists(abs_test_data_dir):
        print(f"Warning: Test data directory not found: {abs_test_data_dir}")
        return []
    
    # データセット名が指定されている場合
    if dataset_names:
        dataset_paths = []
        for name in dataset_names:
            path = os.path.join(abs_test_data_dir, name)
            if os.path.exists(path):
                dataset_paths.append(path)
            else:
                print(f"Warning: Dataset not found: {path}")
        return dataset_paths
    
    # データセット名が指定されていない場合は自動検出
    return find_datasets(abs_test_data_dir, alignment_dir_name, queries_dir_name)


def write_results_to_csv(results, output_csv_file):
    """
    変換結果をCSVファイルに書き込む。
    
    Args:
        results: 変換結果のリスト
        output_csv_file: 出力CSVファイルのパス
    """
    if not results:
        print("No results to write.")
        return
    
    print(f"\n--- Writing results to {output_csv_file} ---")
    with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            "dataset", "alignment_file", "query_file", "status",
            "input_query", "output_query", "expected_query", "error_info",
            "llm_judgment", "llm_reason"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print("Successfully wrote results to CSV.")


def print_summary(results):
    """
    変換結果のサマリーを表示する。
    
    Args:
        results: 変換結果のリスト
    """
    if not results:
        print("No results to summarize.")
        return
    
    successful_translations = sum(1 for r in results if r['status'] == 'Success')
    total_queries = len(results)
    success_rate = (successful_translations / total_queries) * 100 if total_queries > 0 else 0

    print("\n--- Translation Summary ---")
    print(f"Total queries processed: {total_queries}")
    print(f"Successful translations: {successful_translations}")
    print(f"Failed translations: {total_queries - successful_translations}")
    print(f"Success rate: {success_rate:.2f}%")


def main():
    """
    全てのテストデータセットを処理し、結果をCSVに出力する。
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 出力CSVファイル名の生成
    output_csv_file = os.path.join(
        project_root, 
        f'{OUTPUT_CSV_PREFIX}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

    # データセットパスの取得
    dataset_paths = get_dataset_paths(
        project_root, 
        TEST_DATA_DIR, 
        DATASET_NAMES,
        ALIGNMENT_DIR_NAME,
        QUERIES_DIR_NAME
    )
    
    if not dataset_paths:
        print("No datasets found or processed.")
        return

    # SPARQLパーサーの初期化
    sparql_parser = SparqlAstParser(project_root)
    
    # 各データセットを処理
    all_results = []
    for dataset_path in dataset_paths:
        results = process_dataset(
            dataset_path, 
            sparql_parser, 
            project_root,
            ALIGNMENT_DIR_NAME,
            ALIGNMENT_FILE_NAME,
            QUERIES_DIR_NAME,
            EXPECTED_OUTPUTS_DIR_NAME
        )
        all_results.extend(results)

    # LLM評価の実行（オプション）
    if ENABLE_LLM_EVALUATION:
        print("\n--- Starting LLM Evaluation (Gemini API) ---")
        all_results = evaluate_results_with_llm(all_results)

    # 結果の出力
    write_results_to_csv(all_results, output_csv_file)
    print_summary(all_results)


if __name__ == '__main__':
    main()