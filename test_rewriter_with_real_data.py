"""
実際のEDOALファイルとSPARQLクエリを使用してリライターをテストする。

このスクリプトは以下を実行します：
1. EDOALアラインメントファイルをパース
2. パース結果（特にorとcompose）の構造を検証
3. 実際のSPARQLクエリパターンを手動で構築してリライターに通す
4. リライト前後のASTを比較して出力
"""

import sys
import os
import pprint

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from sparql_translator.src.parser.edoal_parser import EdoalParser
from sparql_translator.src.rewriter.sparql_rewriter import SparqlRewriter

def test_alignment_parsing():
    """アラインメントファイルのパース結果を検証"""
    print("="*80)
    print("Step 1: アラインメントファイルのパースと検証")
    print("="*80)
    
    alignment_path = os.path.join(
        project_root,
        'sparql_translator/test_data/agronomic-voc/alignment/alignment.edoal'
    )
    
    print(f"\nParsing alignment file: {alignment_path}")
    # verbose=True でデバッグログを有効化
    parser = EdoalParser(alignment_path, verbose=True)
    alignment = parser.parse()
    
    print(f"\n✓ Successfully parsed alignment with {len(alignment.cells)} cells")
    print(f"  onto1: {alignment.onto1}")
    print(f"  onto2: {alignment.onto2}")
    
    # 特にorやcomposeを含むセルを探す
    print("\n" + "="*80)
    print("Searching for cells with 'or' or 'compose'...")
    print("="*80)
    
    for idx, cell in enumerate(alignment.cells):
        cell_info = f"Cell {idx}: {type(cell.entity1).__name__} -> {type(cell.entity2).__name__}"
        
        # entity2がLogicalConstructorまたはPathConstructorの場合
        from sparql_translator.src.parser.edoal_parser import LogicalConstructor, PathConstructor
        
        if isinstance(cell.entity2, LogicalConstructor):
            print(f"\n{cell_info}")
            print(f"  entity2 is LogicalConstructor: operator={cell.entity2.operator}")
            print(f"  operands count: {len(cell.entity2.operands)}")
            for op_idx, operand in enumerate(cell.entity2.operands):
                print(f"    Operand {op_idx}: {type(operand).__name__}")
                if hasattr(operand, 'uri'):
                    print(f"      URI: {operand.uri}")
                elif isinstance(operand, PathConstructor):
                    print(f"      PathConstructor: operator={operand.operator}")
                    print(f"      PathConstructor operands: {len(operand.operands)}")
                    for pc_idx, pc_op in enumerate(operand.operands):
                        print(f"        PC Operand {pc_idx}: {type(pc_op).__name__}")
                        if hasattr(pc_op, 'uri'):
                            print(f"          URI: {pc_op.uri}")
        
        elif isinstance(cell.entity2, PathConstructor):
            print(f"\n{cell_info}")
            print(f"  entity2 is PathConstructor: operator={cell.entity2.operator}")
            print(f"  operands count: {len(cell.entity2.operands)}")
    
    return alignment, parser


def test_case_1_query_1(alignment):
    """
    Test Case 1: query_1.sparql に基づくテスト
    
    元のクエリ:
    ?taxon agro:prefScientificName ?label.
    ?taxon a ?rank.
    FILTER (regex(?label, "^triticum$","i"))
    
    期待: agro:prefScientificName が書き換えられ、
          FILTER が正しい変数を参照すること
    """
    print("\n" + "="*80)
    print("Test Case 1: query_1.sparql (FILTER with regex)")
    print("="*80)
    
    # 手動でASTを構築
    test_ast = {
        'prefixes': {
            'agro': 'http://ontology.irstea.fr/agronomictaxon/core#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
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
                            'subject': {'type': 'variable', 'value': 'taxon'},
                            'predicate': {'type': 'uri', 'value': 'http://ontology.irstea.fr/agronomictaxon/core#prefScientificName'},
                            'object': {'type': 'variable', 'value': 'label'}
                        },
                        {
                            'type': 'triple',
                            'subject': {'type': 'variable', 'value': 'taxon'},
                            'predicate': {'type': 'uri', 'value': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                            'object': {'type': 'variable', 'value': 'rank'}
                        }
                    ]
                },
                {
                    'type': 'filter',
                    'expression': 'regex(?label, "^triticum$", "i")'
                }
            ]
        },
        'queryType': 'SELECT',
        'isDistinct': False,
        'selectVariables': ['rank']
    }
    
    print("\nOriginal AST:")
    pprint.pprint(test_ast, width=120)
    
    # リライト実行
    print("\n--- Executing rewrite ---")
    rewriter = SparqlRewriter(alignment, verbose=True)
    rewritten_ast = rewriter.walk(test_ast)
    
    print("\nRewritten AST:")
    pprint.pprint(rewritten_ast, width=120)
    
    # 検証
    print("\n--- Verification ---")
    # TODO: FILTERの変数が正しいか確認
    

def test_case_2_query_4(alignment):
    """
    Test Case 2: query_4.sparql に基づくテスト
    
    元のクエリ:
    ?taxon agro:prefVernacularName ?commonName.
    FILTER (regex(?label, "^triticum$", "i") && lang(?commonName) ="en")
    
    期待: agro:prefVernacularName が or パターンで展開され、
          UNION構造が生成されること
    """
    print("\n" + "="*80)
    print("Test Case 2: query_4.sparql (OR/UNION pattern)")
    print("="*80)
    
    test_ast = {
        'prefixes': {
            'agro': 'http://ontology.irstea.fr/agronomictaxon/core#',
        },
        'ast': {
            'type': 'group',
            'patterns': [
                {
                    'type': 'bgp',
                    'triples': [
                        {
                            'type': 'triple',
                            'subject': {'type': 'variable', 'value': 'taxon'},
                            'predicate': {'type': 'uri', 'value': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                            'object': {'type': 'uri', 'value': 'http://ontology.irstea.fr/agronomictaxon/core#Taxon'}
                        },
                        {
                            'type': 'triple',
                            'subject': {'type': 'variable', 'value': 'taxon'},
                            'predicate': {'type': 'uri', 'value': 'http://ontology.irstea.fr/agronomictaxon/core#prefScientificName'},
                            'object': {'type': 'variable', 'value': 'label'}
                        },
                        {
                            'type': 'triple',
                            'subject': {'type': 'variable', 'value': 'taxon'},
                            'predicate': {'type': 'uri', 'value': 'http://ontology.irstea.fr/agronomictaxon/core#prefVernacularName'},
                            'object': {'type': 'variable', 'value': 'commonName'}
                        }
                    ]
                }
            ]
        },
        'queryType': 'SELECT',
        'selectVariables': ['commonName']
    }
    
    print("\nOriginal AST:")
    pprint.pprint(test_ast, width=120)
    
    print("\n--- Executing rewrite ---")
    rewriter = SparqlRewriter(alignment, verbose=True)
    rewritten_ast = rewriter.walk(test_ast)
    
    print("\nRewritten AST:")
    pprint.pprint(rewritten_ast, width=120)
    
    # 検証
    print("\n--- Verification ---")
    # UNIONが含まれているか確認
    def contains_union(node):
        if isinstance(node, dict):
            if node.get('type') == 'union':
                return True
            for value in node.values():
                if contains_union(value):
                    return True
        elif isinstance(node, list):
            for item in node:
                if contains_union(item):
                    return True
        return False
    
    if contains_union(rewritten_ast):
        print("✓ UNION structure found in rewritten AST")
    else:
        print("✗ UNION structure NOT found (expected)")


def test_case_3_query_5(alignment):
    """
    Test Case 3: query_5.sparql に基づくテスト
    
    元のクエリ:
    ?taxon agro:prefVernacularName ?label.
    ?taxon agro:hasLowerRank ?specy.
    ?specy a agro:SpecyRank.
    
    期待: compose パターンが展開され、中間変数が生成されること
    """
    print("\n" + "="*80)
    print("Test Case 3: query_5.sparql (Compose/Property Chain)")
    print("="*80)
    
    test_ast = {
        'prefixes': {
            'agro': 'http://ontology.irstea.fr/agronomictaxon/core#',
        },
        'ast': {
            'type': 'group',
            'patterns': [
                {
                    'type': 'bgp',
                    'triples': [
                        {
                            'type': 'triple',
                            'subject': {'type': 'variable', 'value': 'taxon'},
                            'predicate': {'type': 'uri', 'value': 'http://ontology.irstea.fr/agronomictaxon/core#prefVernacularName'},
                            'object': {'type': 'variable', 'value': 'label'}
                        },
                        {
                            'type': 'triple',
                            'subject': {'type': 'variable', 'value': 'taxon'},
                            'predicate': {'type': 'uri', 'value': 'http://ontology.irstea.fr/agronomictaxon/core#hasLowerRank'},
                            'object': {'type': 'variable', 'value': 'specy'}
                        },
                        {
                            'type': 'triple',
                            'subject': {'type': 'variable', 'value': 'specy'},
                            'predicate': {'type': 'uri', 'value': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                            'object': {'type': 'uri', 'value': 'http://ontology.irstea.fr/agronomictaxon/core#SpecyRank'}
                        }
                    ]
                }
            ]
        },
        'queryType': 'SELECT',
        'selectVariables': ['specy']
    }
    
    print("\nOriginal AST:")
    pprint.pprint(test_ast, width=120)
    
    print("\n--- Executing rewrite ---")
    rewriter = SparqlRewriter(alignment, verbose=True)
    rewritten_ast = rewriter.walk(test_ast)
    
    print("\nRewritten AST:")
    pprint.pprint(rewritten_ast, width=120)
    
    # 検証
    print("\n--- Verification ---")
    # 一時変数が生成されているか確認
    def find_temp_vars(node, temp_vars=None):
        if temp_vars is None:
            temp_vars = set()
        if isinstance(node, dict):
            if node.get('type') == 'variable' and 'temp' in node.get('value', '').lower():
                temp_vars.add(node.get('value'))
            for value in node.values():
                find_temp_vars(value, temp_vars)
        elif isinstance(node, list):
            for item in node:
                find_temp_vars(item, temp_vars)
        return temp_vars
    
    temp_vars = find_temp_vars(rewritten_ast)
    if temp_vars:
        print(f"✓ Temporary variables found: {temp_vars}")
    else:
        print("✗ No temporary variables found (may be expected depending on mapping)")


def main():
    """メインの検証フロー"""
    print("\n" + "="*80)
    print("Real Data Validation for SPARQL Rewriter")
    print("="*80)
    
    # Step 1: アラインメントのパースと検証
    alignment, parser = test_alignment_parsing()
    
    # Step 2: 各テストケースを実行
    test_case_1_query_1(alignment)
    test_case_2_query_4(alignment)
    test_case_3_query_5(alignment)
    
    print("\n" + "="*80)
    print("Validation Complete")
    print("="*80)


if __name__ == '__main__':
    main()
