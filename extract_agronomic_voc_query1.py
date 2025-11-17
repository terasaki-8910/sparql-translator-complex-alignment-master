#!/usr/bin/env python3
"""
CSVからagronomic-vocのquery_1を抽出してFILTERを確認
"""
import csv

csv_path = 'translation_results_20251117_130507.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if row['dataset'] == 'agronomic-voc' and row['query_file'] == 'query_1.sparql':
            print("=" * 80)
            print("agronomic-voc / query_1.sparql")
            print("=" * 80)
            print("\n【元のクエリ】")
            print(row['input_query'][:300] + "...")
            
            print("\n【期待される出力（一部）】")
            expected = row['expected_query']
            # FILTERを含む部分を抽出
            if 'filter' in expected.lower() or 'FILTER' in expected:
                filter_idx = expected.lower().find('filter')
                print(expected[max(0, filter_idx-50):filter_idx+100])
            
            print("\n【実際の出力】")
            actual = row['output_query']
            print(actual)
            
            print("\n【FILTER検索】")
            if 'FILTER' in actual:
                filter_lines = [line.strip() for line in actual.split('\n') if 'FILTER' in line]
                for line in filter_lines:
                    print(f"  {line}")
            else:
                print("  ❌ FILTERが見つかりません")
            
            break
