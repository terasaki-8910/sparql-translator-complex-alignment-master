import os
import csv
import traceback
from sparql_translator.src.parser.edoal_parser import EdoalParser
from sparql_translator.src.parser.sparql_ast_parser import SparqlAstParser
from sparql_translator.src.rewriter.sparql_rewriter import SparqlRewriter
from sparql_translator.src.rewriter.ast_serializer import AstSerializer

def process_dataset(dataset_path, sparql_parser):
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
        serializer = AstSerializer()
    except Exception as e:
        print(f"Error parsing alignment file {alignment_file}: {e}")
        return []

    results = []
    for query_filename in sorted(os.listdir(queries_dir)):
        query_filepath = os.path.join(queries_dir, query_filename)
        if not query_filepath.endswith(".sparql"):
            continue

        print(f"  - Processing query: {query_filename}")
        
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
            status = "Success"
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
    output_csv_file = os.path.join(project_root, 'translation_results.csv')

    all_results = []
    sparql_parser = SparqlAstParser(project_root)

    for dirpath, dirnames, _ in os.walk(test_data_dir):
        # alignment と queries ディレクトリを持つものをデータセットのルートと判断
        if "alignment" in dirnames and "queries" in dirnames:
            dataset_path = dirpath
            results = process_dataset(dataset_path, sparql_parser)
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