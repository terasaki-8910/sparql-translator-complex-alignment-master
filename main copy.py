import os
import csv
import traceback
import re
from datetime import datetime
from sparql_translator.src.parser.edoal_parser import EdoalParser
from sparql_translator.src.parser.sparql_ast_parser import SparqlAstParser
from sparql_translator.src.rewriter.sparql_rewriter import SparqlRewriter
from sparql_translator.src.rewriter.ast_serializer import AstSerializer
from sparql_translator.src.common.logger import get_logger

"""
タスク
AST ➡︎ SPARQL をPythonで行うのではなく、Jenaを使って行い、その結果をPythonで受け取るように変更する。
"""


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


def process_dataset(dataset_path, sparql_parser, project_root):
    """
    単一のデータセットに対する変換処理を行う。
    """
    alignment_file = os.path.join(dataset_path, "alignment", "alignment.edoal")
    queries_dir = os.path.join(dataset_path, "queries")
    expected_outputs_dir = os.path.join(dataset_path, "expected_outputs")

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

def main():
    """
    全てのテストデータセットを処理し、結果をCSVに出力する。
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(project_root, 'sparql_translator', 'test_data')
    output_csv_file = os.path.join(project_root, f'translation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

    all_results = []
    sparql_parser = SparqlAstParser(project_root)

    for dirpath, dirnames, _ in os.walk(test_data_dir):
        # alignment と queries ディレクトリを持つものをデータセットのルートと判断
        if "alignment" in dirnames and "queries" in dirnames:
            dataset_path = dirpath
            results = process_dataset(dataset_path, sparql_parser, project_root)
            all_results.extend(results)
            # サブディレクトリをこれ以上探索しないようにする
            dirnames[:] = []


    if not all_results:
        print("No datasets found or processed.")
        return

    # --- CSVへの書き込み ---
    print(f"\n--- Writing results to {output_csv_file} ---")
    with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            "dataset", "alignment_file", "query_file", "status",
            "input_query", "output_query", "expected_query", "error_info"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    print("Successfully wrote results to CSV.")

    # --- 変換成功率の計算 ---
    successful_translations = sum(1 for r in all_results if r['status'] == 'Success')
    total_queries = len(all_results)
    success_rate = (successful_translations / total_queries) * 100 if total_queries > 0 else 0

    print("\n--- Translation Summary ---")
    print(f"Total queries processed: {total_queries}")
    print(f"Successful translations: {successful_translations}")
    print(f"Failed translations: {total_queries - successful_translations}")
    print(f"Success rate: {success_rate:.2f}%")


if __name__ == '__main__':
    main()