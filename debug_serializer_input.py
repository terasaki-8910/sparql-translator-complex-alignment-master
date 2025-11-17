#!/usr/bin/env python3
"""
書き換え後のASTをJSONで出力して、シリアライザーへの入力を確認する
"""
import sys
import json

from sparql_translator.src.parser.edoal_parser import EdoalParser
from sparql_translator.src.parser.sparql_ast_parser import SparqlAstParser
from sparql_translator.src.rewriter.sparql_rewriter import SparqlRewriter
from sparql_translator.src.rewriter.ast_serializer import AstSerializer

# テストケース1: query_1.sparql
alignment_file = 'sparql_translator/test_data/agronomic-voc/alignment/alignment.edoal'
query_file = 'sparql_translator/test_data/agronomic-voc/queries/query_1.sparql'

print("=" * 80)
print("シリアライザー入力確認")
print("=" * 80)

# 1. アラインメントとクエリをパース
parser = EdoalParser(alignment_file, verbose=False)
alignment = parser.parse()

import os
project_root = os.getcwd()
ast_parser = SparqlAstParser(project_root)
ast = ast_parser.parse(query_file)

# 2. リライターを実行
rewriter = SparqlRewriter(alignment, verbose=False)
rewritten_ast = rewriter.walk(ast)

# 3. 書き換え後のASTをJSON出力
print("\n書き換え後のAST:")
print(json.dumps(rewritten_ast, indent=2))

# 4. シリアライザーを実行
print("\n" + "=" * 80)
print("シリアライザー実行")
print("=" * 80)

serializer = AstSerializer(project_root)
sparql_output = serializer.serialize(rewritten_ast)

print("\n生成されたSPARQL:")
print(sparql_output)
