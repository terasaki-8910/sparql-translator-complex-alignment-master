#!/usr/bin/env python3
"""
FILTERの書き換えをデバッグする
"""
import sys
import json

from sparql_translator.src.parser.edoal_parser import EdoalParser
from sparql_translator.src.parser.sparql_ast_parser import SparqlAstParser
from sparql_translator.src.rewriter.sparql_rewriter import SparqlRewriter

# テストケース1: query_1.sparql
alignment_file = 'sparql_translator/test_data/agronomic-voc/alignment/alignment.edoal'
query_file = 'sparql_translator/test_data/agronomic-voc/queries/query_1.sparql'

print("=" * 80)
print("デバッグ: FILTER書き換えトレース")
print("=" * 80)

# 1. アラインメントをパース
print("\n[Step 1] アラインメントをパース")
parser = EdoalParser(alignment_file, verbose=False)
alignment = parser.parse()
print(f"✓ パースされたCell数: {len(alignment.cells)}")

# 2. クエリをASTにパース
print("\n[Step 2] SPARQLクエリをASTにパース")
with open(query_file, 'r') as f:
    original_query = f.read()
print(f"元のクエリ:\n{original_query}\n")

import os
project_root = os.getcwd()
ast_parser = SparqlAstParser(project_root)
ast = ast_parser.parse(query_file)

# ASTの中のFILTERを探す
def find_filters(node, path="root"):
    """ASTからFILTERノードを再帰的に探す"""
    filters = []
    
    if isinstance(node, dict):
        if node.get('type') == 'filter':
            filters.append((path, node))
            print(f"  [Found Filter] パス: {path}")
            print(f"    式: {json.dumps(node.get('expression'), indent=2)}")
        
        for key, value in node.items():
            filters.extend(find_filters(value, f"{path}.{key}"))
    
    elif isinstance(node, list):
        for i, item in enumerate(node):
            filters.extend(find_filters(item, f"{path}[{i}]"))
    
    return filters

print("\n[Step 3] 元のASTの中のFILTERを検索")
original_filters = find_filters(ast)
print(f"✓ 検出されたFILTER数: {len(original_filters)}")

# 3. リライターを実行
print("\n[Step 4] リライターを実行（verbose=True）")
rewriter = SparqlRewriter(alignment, verbose=True)
rewritten_ast = rewriter.walk(ast)

# 4. 書き換え後のFILTERを探す
print("\n[Step 5] 書き換え後のASTの中のFILTERを検索")
rewritten_filters = find_filters(rewritten_ast)
print(f"✓ 検出されたFILTER数: {len(rewritten_filters)}")

# 5. 比較
print("\n[Step 6] FILTERの比較")
print("=" * 80)
for i, ((orig_path, orig_filter), (new_path, new_filter)) in enumerate(zip(original_filters, rewritten_filters), 1):
    print(f"\nFILTER #{i}:")
    print(f"  元のパス:   {orig_path}")
    print(f"  新しいパス: {new_path}")
    print(f"\n  元の式:")
    print(f"    {json.dumps(orig_filter.get('expression'), indent=4)}")
    print(f"\n  新しい式:")
    print(f"    {json.dumps(new_filter.get('expression'), indent=4)}")
    
    # 式が変わったかチェック
    if orig_filter.get('expression') == new_filter.get('expression'):
        print(f"  ✅ 式は保持されています")
    else:
        print(f"  ❌ 式が変更されました！")

print("\n" + "=" * 80)
