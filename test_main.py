import os
import pprint
from sparql_translator.src.parser.edoal_parser import EdoalParser
from sparql_translator.src.parser.sparql_ast_parser import SparqlAstParser
from sparql_translator.src.rewriter.sparql_rewriter import SparqlRewriter
from sparql_translator.src.rewriter.ast_serializer import AstSerializer

def main():
    """
    クエリ変換システムのメイン処理を行う。
    """
    # --- 設定 ---
    project_root = os.path.dirname(os.path.abspath(__file__))
    alignment_file = os.path.join(project_root, 'jar utiles/data/agro-db/AgronomicTaxon-Dbpedia.edoal.xml')
    sparql_file = os.path.join(project_root, 'jar utiles/data/agro-db/IN1.sparql')

    print("--- 1. アラインメントファイルのパース ---")
    edoal_parser = EdoalParser(alignment_file)
    alignment_data = edoal_parser.parse()
    print(f"アラインメントセルを {len(alignment_data.cells)} 件読み込みました。")

    print("\n--- 2. SPARQLクエリのASTへのパース ---")
    sparql_parser = SparqlAstParser(project_root)
    source_ast = sparql_parser.parse(sparql_file)
    print("元のAST:")
    pprint.pprint(source_ast)

    print("\n--- 3. ASTの書き換え ---")
    rewriter = SparqlRewriter(alignment_data)
    rewritten_ast = rewriter.walk(source_ast)
    
    print("\n--- 4. 書き換え後のASTからSPARQL文字列への再構築 ---")
    serializer = AstSerializer()
    rewritten_query = serializer.serialize(rewritten_ast)
    
    print("書き換え後のSPARQLクエリ:")
    print("-" * 20)
    print(rewritten_query)
    print("-" * 20)

if __name__ == '__main__':
    main()