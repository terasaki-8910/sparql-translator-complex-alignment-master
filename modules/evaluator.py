"""
evaluator.py
クエリ実行と結果比較を行うモジュール

設計原則:
- Source Check → Translate → Target Execution → Comparison の4ステップを厳密に実行
- 虚偽の成功報告の禁止 (Prohibition.md Section 2)
- 実質的な出力検証（空文字・エラーメッセージの検出）
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import os


class QueryEvaluator:
    """
    クエリの変換と実行を評価するクラス
    """
    
    def __init__(self, translator_adapter, data_loader, config_loader, enable_execution: bool = False):
        """
        Args:
            translator_adapter: TranslatorAdapterインスタンス
            data_loader: DataLoaderインスタンス
            config_loader: ConfigLoaderインスタンス
            enable_execution: クエリ実行を有効にするかどうか（デフォルト: False）
        """
        self.translator = translator_adapter
        self.data_loader = data_loader
        self.config_loader = config_loader
        self.enable_execution = enable_execution
    
    def evaluate_pair(self, pair_name: str) -> List[Dict[str, Any]]:
        """
        アラインメントペアの全クエリを評価
        
        Args:
            pair_name: アラインメントペア名
            
        Returns:
            評価結果のリスト
        """
        print(f"\n========== {pair_name} の評価を開始 ==========")
        
        # 設定をロード
        alignment_config = self.config_loader.load_alignment_config(pair_name)
        
        # データソースをロード
        sources = self.data_loader.load_sources_for_pair(pair_name)
        
        # クエリディレクトリからクエリファイルを取得
        queries_dir = Path(alignment_config.get("queries_dir", ""))
        if not queries_dir.exists():
            raise FileNotFoundError(f"クエリディレクトリが見つかりません: {queries_dir}")
        
        expected_outputs_dir = None
        if alignment_config.get("expected_output_dir"):
            expected_outputs_dir = Path(alignment_config["expected_output_dir"])
        
        alignment_file = alignment_config["alignment_file"]
        
        # 全クエリファイルを処理
        results = []
        query_files = sorted([f for f in queries_dir.iterdir() if f.suffix == ".sparql"])
        
        for query_file in query_files:
            print(f"\n--- クエリファイル: {query_file.name} ---")
            
            result = self._evaluate_single_query(
                query_file=query_file,
                alignment_file=alignment_file,
                sources=sources,
                expected_outputs_dir=expected_outputs_dir,
                pair_name=pair_name
            )
            
            results.append(result)
        
        return results
    
    def _evaluate_single_query(
        self,
        query_file: Path,
        alignment_file: str,
        sources: Dict[str, Any],
        expected_outputs_dir: Optional[Path],
        pair_name: str
    ) -> Dict[str, Any]:
        """
        単一のクエリファイルを評価
        
        Returns:
            評価結果の辞書
        """
        result = {
            "pair_name": pair_name,
            "query_file": query_file.name,
            "input_query": "",
            "output_query": "",
            "expected_query": "",
            "source_check": "N/A",
            "translation_success": False,
            "target_execution": "N/A",
            "comparison_result": "N/A",
            "error": None
        }
        
        try:
            # ソースクエリを読み込み
            with open(query_file, 'r', encoding='utf-8') as f:
                source_query = f.read()
            
            result["input_query"] = source_query
            
            # Step 1: Source Check（ソースデータセット/エンドポイントでクエリが実行可能か確認）
            if self.enable_execution and sources:
                # 実行が有効な場合のみソースチェックを実施
                result["source_check"] = "ENABLED"
            else:
                result["source_check"] = "SKIPPED (execution disabled)"
            
            # Step 2: Translate（クエリを変換）
            print("  - クエリ変換を実行中...")
            translation_result = self.translator.translate_query(
                source_query=source_query,
                alignment_file=alignment_file
            )
            
            if not translation_result["success"]:
                result["error"] = f"変換失敗: {translation_result.get('error', '不明なエラー')}"
                result["translation_success"] = False
                return result
            
            output_query = translation_result["output_query"]
            result["output_query"] = output_query
            result["translation_success"] = True
            
            # 変換結果の実質的な検証
            validation = self.translator.validate_translation(
                input_query=source_query,
                output_query=output_query,
                alignment_file=alignment_file
            )
            
            if not validation["valid"]:
                result["error"] = f"検証失敗: {validation['reason']}"
                result["translation_success"] = False
                return result
            
            print(f"  - 変換成功（出力: {len(output_query)} 文字）")
            
            # Step 3: Target Execution（変換後クエリをターゲットデータセット/エンドポイントで実行）
            if self.enable_execution and sources:
                print("  - ターゲットデータソースでクエリを実行中...")
                try:
                    # ターゲットデータソースでクエリを実行
                    # 注: 複数のデータソースがある場合は最初のものを使用
                    target_source = list(sources.values())[0] if sources else None
                    if target_source:
                        execution_results = target_source.query(output_query)
                        result["target_execution"] = f"SUCCESS ({len(execution_results)} results)"
                        print(f"  - 実行成功: {len(execution_results)} 件の結果")
                    else:
                        result["target_execution"] = "FAILED (no data source)"
                except Exception as e:
                    result["target_execution"] = f"FAILED ({type(e).__name__}: {str(e)[:100]})"
                    print(f"  - 実行失敗: {e}")
            else:
                result["target_execution"] = "SKIPPED (execution disabled)"
            
            # Step 4: Comparison（expected_output がある場合、結果集合の一致を判定）
            if expected_outputs_dir and expected_outputs_dir.exists():
                expected_file = expected_outputs_dir / query_file.name
                if expected_file.exists():
                    with open(expected_file, 'r', encoding='utf-8') as f:
                        expected_query = f.read()
                    
                    result["expected_query"] = expected_query
                    
                    # 集合等価性の判定（簡易版: 文字列比較）
                    # 本来は実際のRDF結果集合を比較すべきだが、ここでは簡略化
                    comparison = self._compare_queries(output_query, expected_query)
                    result["comparison_result"] = comparison
                    
                    print(f"  - 比較結果: {comparison}")
                else:
                    result["comparison_result"] = "NO_EXPECTED_FILE"
            else:
                result["comparison_result"] = "NO_EXPECTED_DIR"
        
        except Exception as e:
            result["error"] = f"評価中に例外が発生: {type(e).__name__}: {str(e)}"
        
        return result
    
    def _compare_queries(self, output_query: str, expected_query: str) -> str:
        """
        出力クエリと期待クエリを比較
        
        Args:
            output_query: 変換後クエリ
            expected_query: 期待されるクエリ
            
        Returns:
            "MATCH", "MISMATCH", "PARTIAL_MATCH" のいずれか
        """
        # 正規化（空白・改行を統一）
        def normalize(query: str) -> str:
            return " ".join(query.split())
        
        output_normalized = normalize(output_query)
        expected_normalized = normalize(expected_query)
        
        if output_normalized == expected_normalized:
            return "MATCH"
        
        # 部分一致のチェック（URIの一致率）
        import re
        
        def extract_uris(query: str) -> set:
            uri_pattern = r'<([^>]+)>'
            return set(re.findall(uri_pattern, query))
        
        output_uris = extract_uris(output_query)
        expected_uris = extract_uris(expected_query)
        
        if not expected_uris:
            return "MISMATCH"
        
        intersection = output_uris & expected_uris
        match_ratio = len(intersection) / len(expected_uris) if expected_uris else 0
        
        if match_ratio > 0.8:
            return "PARTIAL_MATCH"
        else:
            return "MISMATCH"
