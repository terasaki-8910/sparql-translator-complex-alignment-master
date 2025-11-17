#!/usr/bin/env python3
"""
query_5の失敗原因を詳細分析
"""
import csv

csv_path = 'translation_results_20251117_130507.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if row['dataset'] == 'agronomic-voc' and row['query_file'] == 'query_5.sparql':
            print("=" * 80)
            print("query_5.sparql 失敗原因分析")
            print("=" * 80)
            
            print(f"\nステータス: {row['status']}")
            print(f"\n出力クエリ: {row['output_query']}")
            print(f"\nエラー情報: {row['error_info']}")
            break
