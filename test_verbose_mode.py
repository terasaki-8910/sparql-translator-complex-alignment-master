"""
verboseフラグの動作確認用テスト

verbose=False で実行し、ログが抑制されることを確認
"""

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from sparql_translator.src.parser.edoal_parser import EdoalParser
from sparql_translator.src.rewriter.sparql_rewriter import SparqlRewriter

def test_quiet_mode():
    """verboseフラグをオフにしてログが抑制されることを確認"""
    
    print("="*80)
    print("Verbose Mode Test: Testing with verbose=False")
    print("="*80)
    
    alignment_path = os.path.join(
        project_root,
        'sparql_translator/test_data/agronomic-voc/alignment/alignment.edoal'
    )
    
    print(f"\n1. Parsing alignment with verbose=False...")
    parser = EdoalParser(alignment_path, verbose=False)
    alignment = parser.parse()
    print(f"   ✓ Parsed {len(alignment.cells)} cells (no debug logs should appear above)")
    
    print(f"\n2. Creating rewriter with verbose=False...")
    rewriter = SparqlRewriter(alignment, verbose=False)
    print(f"   ✓ Rewriter created")
    
    # 簡単なテストAST
    test_ast = {
        'prefixes': {'agro': 'http://ontology.irstea.fr/agronomictaxon/core#'},
        'ast': {
            'type': 'group',
            'patterns': [{
                'type': 'bgp',
                'triples': [{
                    'type': 'triple',
                    'subject': {'type': 'variable', 'value': 'taxon'},
                    'predicate': {'type': 'uri', 'value': 'http://ontology.irstea.fr/agronomictaxon/core#prefScientificName'},
                    'object': {'type': 'variable', 'value': 'label'}
                }]
            }]
        },
        'queryType': 'SELECT',
        'selectVariables': ['label']
    }
    
    print(f"\n3. Rewriting AST with verbose=False...")
    rewritten_ast = rewriter.walk(test_ast)
    print(f"   ✓ AST rewritten (no debug logs should appear above)")
    
    # UNION構造が生成されたか確認
    def has_union(node):
        if isinstance(node, dict):
            if node.get('type') == 'union':
                return True
            for value in node.values():
                if has_union(value):
                    return True
        elif isinstance(node, list):
            for item in node:
                if has_union(item):
                    return True
        return False
    
    if has_union(rewritten_ast):
        print(f"\n   ✓ Verification: UNION structure found in rewritten AST")
    else:
        print(f"\n   ✗ Warning: UNION structure not found")
    
    print("\n" + "="*80)
    print("Test Complete: If no [DEBUG] or [Info] logs appeared above, verbose mode works correctly")
    print("="*80)

if __name__ == '__main__':
    test_quiet_mode()
