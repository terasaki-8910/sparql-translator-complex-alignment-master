import sys
from sparql_slurper import parse
from pprint import pprint

def investigate_slurper_ast(file_path):
    """
    Parses a SPARQL query file using sparql-slurper and prints its AST.
    """
    with open(file_path, 'r') as f:
        query_string = f.read()

    try:
        # SPARQLクエリをパース
        ast = parse(query_string)
        
        print("--- SPARQL Query ---")
        print(query_string)
        
        # パースされたAST (辞書オブジェクト) を出力
        print("\n--- Parsed AST (sparql-slurper) ---")
        pprint(ast)

    except Exception as e:
        print(f"\nError parsing SPARQL query: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        investigate_slurper_ast(sys.argv[1])
    else:
        print("Usage: python investigate_sparql_ast.py <path_to_sparql_file>")
