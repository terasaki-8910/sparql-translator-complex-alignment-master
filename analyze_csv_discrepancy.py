#!/usr/bin/env python3
"""
CSVの期待値と実際の出力の差分を詳細に分析する
"""
import csv
import re

def extract_variables(sparql_text):
    """SPARQLクエリから変数を抽出"""
    # ?variable_name 形式の変数を抽出
    return set(re.findall(r'\?(\w+)', sparql_text))

def extract_triples(sparql_text):
    """トリプルパターンを抽出（簡易版）"""
    # WHERE { ... } の中身を抽出
    where_match = re.search(r'WHERE\s*\{(.*)\}', sparql_text, re.DOTALL | re.IGNORECASE)
    if not where_match:
        return []
    
    content = where_match.group(1)
    # FILTER を除外
    content = re.sub(r'FILTER\s*\([^)]+\)', '', content, flags=re.IGNORECASE)
    
    # トリプルパターンを抽出（簡易版）
    triples = []
    lines = content.split('.')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('UNION') and not line.startswith('{') and not line.startswith('}'):
            triples.append(line)
    
    return triples

def analyze_csv(csv_path):
    """CSVを読み込んで差分を分析"""
    print("=" * 80)
    print("CSV差分分析レポート")
    print("=" * 80)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader, 1):
            query_file = row['query_file']
            status = row['status']
            expected = row['expected_query']
            actual = row['output_query']
            
            print(f"\n{'=' * 80}")
            print(f"クエリ {i}: {query_file}")
            print(f"ステータス: {status}")
            print('=' * 80)
            
            # 変数の比較
            expected_vars = extract_variables(expected)
            actual_vars = extract_variables(actual)
            
            print(f"\n【変数の比較】")
            print(f"期待される変数: {sorted(expected_vars)}")
            print(f"実際の変数:     {sorted(actual_vars)}")
            
            missing_vars = expected_vars - actual_vars
            extra_vars = actual_vars - expected_vars
            
            if missing_vars:
                print(f"❌ 欠落している変数: {sorted(missing_vars)}")
            if extra_vars:
                print(f"⚠️  余分な変数:       {sorted(extra_vars)}")
            
            # FILTERの比較
            expected_filters = re.findall(r'FILTER\s*\([^)]+\)', expected, re.IGNORECASE)
            actual_filters = re.findall(r'FILTER\s*\([^)]+\)', actual, re.IGNORECASE)
            
            print(f"\n【FILTERの比較】")
            print(f"期待されるFILTER数: {len(expected_filters)}")
            print(f"実際のFILTER数:     {len(actual_filters)}")
            
            if expected_filters:
                print("\n期待されるFILTER:")
                for f in expected_filters:
                    print(f"  {f}")
                    # FILTERで参照している変数を抽出
                    filter_vars = extract_variables(f)
                    print(f"    → 参照変数: {sorted(filter_vars)}")
            
            if actual_filters:
                print("\n実際のFILTER:")
                for f in actual_filters:
                    print(f"  {f}")
                    # FILTERで参照している変数を抽出
                    filter_vars = extract_variables(f)
                    print(f"    → 参照変数: {sorted(filter_vars)}")
                    
                    # 存在しない変数を参照していないかチェック
                    for var in filter_vars:
                        if var not in actual_vars:
                            print(f"    ❌ 致命的エラー: FILTER が存在しない変数 ?{var} を参照")
            
            # UNIONの比較
            expected_union = 'UNION' in expected
            actual_union = 'UNION' in actual
            
            print(f"\n【UNION構造】")
            print(f"期待される: {'あり' if expected_union else 'なし'}")
            print(f"実際:       {'あり' if actual_union else 'なし'}")
            
            # トリプルの比較（簡易版）
            print(f"\n【トリプルパターン】")
            expected_triples = extract_triples(expected)
            actual_triples = extract_triples(actual)
            
            print(f"期待されるトリプル数: {len(expected_triples)}")
            print(f"実際のトリプル数:     {len(actual_triples)}")
            
            # 問題点のサマリー
            print(f"\n【問題点サマリー】")
            issues = []
            
            if missing_vars:
                issues.append(f"❌ 変数欠落: {', '.join(sorted(missing_vars))}")
            
            if actual_filters:
                for f in actual_filters:
                    filter_vars = extract_variables(f)
                    for var in filter_vars:
                        if var not in actual_vars:
                            issues.append(f"❌ FILTER変数不整合: ?{var} が定義されていない")
            
            if '?dummy' in actual:
                issues.append("❌ ダミー変数 ?dummy が残存")
            
            if not issues:
                print("✅ 明らかな問題は検出されませんでした")
            else:
                for issue in issues:
                    print(issue)

if __name__ == '__main__':
    csv_path = 'translation_results_20251117_130507.csv'
    analyze_csv(csv_path)
