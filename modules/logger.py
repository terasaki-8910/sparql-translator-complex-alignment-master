"""
logger.py
評価結果をCSV形式で出力するモジュール

設計原則:
- translation_results.csv: 変換の詳細（クエリ全文を含む）
- evaluation_results.csv: 実行結果の正誤判定
- 既存仕様の破壊禁止 (Prohibition.md Section 4)
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class ResultLogger:
    """
    評価結果をCSVファイルに出力するクラス
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Args:
            output_dir: 出力ディレクトリのパス
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_translation_results(self, results: List[Dict[str, Any]], filename: str = None):
        """
        translation_results.csv を出力
        
        Args:
            results: 評価結果のリスト
            filename: 出力ファイル名（省略時はタイムスタンプ付き）
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"translation_results_{timestamp}.csv"
        
        output_path = self.output_dir / filename
        
        # カラム定義（既存仕様を維持）
        fieldnames = [
            "pair_name",
            "query_file",
            "input_query",
            "output_query",
            "expected_query",
            "source_check",
            "translation_success",
            "target_execution",
            "comparison_result",
            "error"
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # 長いクエリ文字列も完全に出力
                row = {
                    "pair_name": result.get("pair_name", ""),
                    "query_file": result.get("query_file", ""),
                    "input_query": result.get("input_query", ""),
                    "output_query": result.get("output_query", ""),
                    "expected_query": result.get("expected_query", ""),
                    "source_check": result.get("source_check", "N/A"),
                    "translation_success": result.get("translation_success", False),
                    "target_execution": result.get("target_execution", "N/A"),
                    "comparison_result": result.get("comparison_result", "N/A"),
                    "error": result.get("error", "")
                }
                writer.writerow(row)
        
        print(f"\n変換結果を出力しました: {output_path}")
    
    def write_evaluation_results(self, results: List[Dict[str, Any]], filename: str = None):
        """
        evaluation_results.csv を出力
        
        Args:
            results: 評価結果のリスト
            filename: 出力ファイル名（省略時はタイムスタンプ付き）
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_results_{timestamp}.csv"
        
        output_path = self.output_dir / filename
        
        # カラム定義
        fieldnames = [
            "pair_name",
            "query_file",
            "translation_success",
            "comparison_result",
            "overall_status"
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # 総合判定
                overall_status = self._determine_overall_status(result)
                
                row = {
                    "pair_name": result.get("pair_name", ""),
                    "query_file": result.get("query_file", ""),
                    "translation_success": result.get("translation_success", False),
                    "comparison_result": result.get("comparison_result", "N/A"),
                    "overall_status": overall_status
                }
                writer.writerow(row)
        
        print(f"評価結果を出力しました: {output_path}")
    
    def _determine_overall_status(self, result: Dict[str, Any]) -> str:
        """
        総合的なステータスを判定
        
        Args:
            result: 評価結果
            
        Returns:
            "SUCCESS", "PARTIAL_SUCCESS", "FAILURE"
        """
        translation_success = result.get("translation_success", False)
        comparison_result = result.get("comparison_result", "N/A")
        error = result.get("error")
        
        if error:
            return "FAILURE"
        
        if not translation_success:
            return "FAILURE"
        
        if comparison_result == "MATCH":
            return "SUCCESS"
        elif comparison_result == "PARTIAL_MATCH":
            return "PARTIAL_SUCCESS"
        elif comparison_result in ["N/A", "NO_EXPECTED_FILE", "NO_EXPECTED_DIR"]:
            # 期待値がない場合、変換が成功していれば成功とみなす
            return "SUCCESS" if translation_success else "FAILURE"
        else:
            return "FAILURE"
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """
        評価結果のサマリーをコンソールに出力
        
        Args:
            results: 評価結果のリスト
        """
        total = len(results)
        success = sum(1 for r in results if r.get("translation_success", False))
        failure = total - success
        
        print("\n" + "=" * 60)
        print("評価サマリー")
        print("=" * 60)
        print(f"総クエリ数:        {total}")
        print(f"変換成功:          {success}")
        print(f"変換失敗:          {failure}")
        
        if total > 0:
            success_rate = (success / total) * 100
            print(f"成功率:            {success_rate:.1f}%")
        
        # 比較結果の集計
        comparison_counts = {}
        for result in results:
            comp = result.get("comparison_result", "N/A")
            comparison_counts[comp] = comparison_counts.get(comp, 0) + 1
        
        if comparison_counts:
            print("\n比較結果:")
            for comp, count in sorted(comparison_counts.items()):
                print(f"  {comp}: {count}")
        
        # エラーの集計
        errors = [r for r in results if r.get("error")]
        if errors:
            print(f"\nエラー発生数: {len(errors)}")
            print("主なエラー:")
            for err_result in errors[:5]:  # 最初の5件のみ表示
                print(f"  - {err_result['query_file']}: {err_result['error'][:100]}")
        
        print("=" * 60)
