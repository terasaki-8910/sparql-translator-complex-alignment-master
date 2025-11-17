#!/usr/bin/env python3
"""
CSVからagronomic-vocの全クエリのFILTERを確認
"""
import csv
import re

csv_path = 'translation_results_20251117_131017.csv'

print("=" * 80)
print("agronomic-voc データセット - FILTER検証")
print("=" * 80)

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if row['dataset'] != 'agronomic-voc':
            continue
        
        query_file = row['query_file']
        status = row['status']
        actual = row['output_query']
        
        print(f"\n{'='*80}")
        print(f"クエリ: {query_file} ({status})")
        print(f"{'='*80}")
        
        # 変数を抽出
        vars_in_output = set(re.findall(r'\?(\w+)', actual))
        print(f"クエリ内の変数: {sorted(vars_in_output)}")
        
        # FILTERを抽出
        filter_matches = re.findall(r'FILTER\s+([^\n]+)', actual, re.IGNORECASE)
        
        if filter_matches:
            print(f"\nFILTER句: {len(filter_matches)}個")
            for i, f in enumerate(filter_matches, 1):
                print(f"  {i}. {f.strip()}")
                
                # FILTERで使われている変数を抽出
                filter_vars = set(re.findall(r'\?(\w+)', f))
                print(f"     使用変数: {sorted(filter_vars)}")
                
                # 存在しない変数をチェック
                undefined_vars = filter_vars - vars_in_output
                if undefined_vars:
                    print(f"     ❌ 未定義変数: {sorted(undefined_vars)}")
                else:
                    print(f"     ✅ すべての変数が定義されています")
        else:
            print("\nFILTER句: なし")
        
        # UNIONの有無
        has_union = 'UNION' in actual
        print(f"\nUNION構造: {'あり' if has_union else 'なし'}")
