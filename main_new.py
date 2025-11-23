#!/usr/bin/env python3
"""
main.py - SPARQL Translation System Entry Point

新規アーキテクチャによる実装
- 既存の sparql_translator パッケージを厳密にラップ
- ファイル/エンドポイントのハイブリッド対応
- 虚偽の成功報告を排除した実質的な検証

使用例:
    python3 main.py --pair agro-dbpedia
    python3 main.py --pair taxons
    python3 main.py --all
"""

import sys
import argparse
from pathlib import Path

# プロジェクトルートをPythonパスに追加
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.config_loader import ConfigLoader
from modules.data_loader import DataLoader
from modules.translator_adapter import TranslatorAdapter
from modules.evaluator import QueryEvaluator
from modules.logger import ResultLogger


def parse_arguments():
    """
    コマンドライン引数を解析
    
    Returns:
        argparse.Namespace: パースされた引数
    """
    parser = argparse.ArgumentParser(
        description="SPARQL Translation System - EDOALベースのクエリ変換と評価",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 main.py --pair agro-dbpedia
  python3 main.py --pair taxons
  python3 main.py --all
  python3 main.py --list
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--pair",
        type=str,
        help="処理するアラインメントペア名（例: agro-dbpedia, cmt-confOf）"
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="全てのアラインメントペアを処理"
    )
    group.add_argument(
        "--list",
        action="store_true",
        help="利用可能なアラインメントペアをリストアップ"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="出力ディレクトリ（デフォルト: output）"
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="変換後クエリをターゲットデータソースで実際に実行する（デフォルト: 実行しない）"
    )
    
    return parser.parse_args()


def initialize_system(project_root: str, enable_execution: bool = False):
    """
    システムの各コンポーネントを初期化
    
    Args:
        project_root: プロジェクトルートの絶対パス
        enable_execution: クエリ実行を有効にするかどうか
        
    Returns:
        tuple: (config_loader, data_loader, translator_adapter, evaluator, logger)
    """
    print("システムを初期化中...")
    
    # 設定ローダー
    config_loader = ConfigLoader(project_root)
    print(f"  - datasets_registry: {len(config_loader.datasets_registry.get('datasets', {}))} 件")
    
    # データローダー
    data_loader = DataLoader(config_loader)
    print("  - データローダー: 初期化完了")
    
    # トランスレータアダプタ
    translator_adapter = TranslatorAdapter(project_root)
    print("  - トランスレータアダプタ: 初期化完了")
    
    # 評価器
    evaluator = QueryEvaluator(translator_adapter, data_loader, config_loader, enable_execution=enable_execution)
    print(f"  - クエリ評価器: 初期化完了（実行モード: {'有効' if enable_execution else '無効'}）")
    
    # ロガー
    logger = ResultLogger()
    print("  - 結果ロガー: 初期化完了")
    
    print("初期化完了\n")
    
    return config_loader, data_loader, translator_adapter, evaluator, logger


def list_pairs(config_loader: ConfigLoader):
    """
    利用可能なアラインメントペアをリストアップ
    
    Args:
        config_loader: ConfigLoaderインスタンス
    """
    pairs = config_loader.list_all_pairs()
    
    print("=" * 60)
    print("利用可能なアラインメントペア")
    print("=" * 60)
    
    for pair_name in pairs:
        try:
            pair_type = config_loader.get_pair_type(pair_name)
            print(f"  - {pair_name:30s} [{pair_type}]")
        except Exception as e:
            print(f"  - {pair_name:30s} [エラー: {e}]")
    
    print("=" * 60)
    print(f"合計: {len(pairs)} ペア")


def process_single_pair(
    pair_name: str,
    evaluator: QueryEvaluator,
    logger: ResultLogger
):
    """
    単一のアラインメントペアを処理
    
    Args:
        pair_name: ペア名
        evaluator: QueryEvaluatorインスタンス
        logger: ResultLoggerインスタンス
    """
    try:
        # 評価実行
        results = evaluator.evaluate_pair(pair_name)
        
        # 結果を出力
        logger.write_translation_results(results, filename=f"translation_results_{pair_name}.csv")
        logger.write_evaluation_results(results, filename=f"evaluation_results_{pair_name}.csv")
        
        # サマリーを表示
        logger.print_summary(results)
    
    except Exception as e:
        print(f"\n【エラー】{pair_name} の処理中にエラーが発生しました:")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


def process_all_pairs(
    config_loader: ConfigLoader,
    evaluator: QueryEvaluator,
    logger: ResultLogger
):
    """
    全てのアラインメントペアを処理
    
    Args:
        config_loader: ConfigLoaderインスタンス
        evaluator: QueryEvaluatorインスタンス
        logger: ResultLoggerインスタンス
    """
    pairs = config_loader.list_all_pairs()
    total_pairs = len(pairs)
    
    print(f"全 {total_pairs} ペアの処理を開始します...\n")
    
    all_results = []
    
    for idx, pair_name in enumerate(pairs, start=1):
        print(f"\n[{idx}/{total_pairs}] {pair_name} を処理中...")
        
        try:
            results = evaluator.evaluate_pair(pair_name)
            all_results.extend(results)
        except Exception as e:
            print(f"  【エラー】{pair_name} の処理をスキップ: {e}")
    
    # 統合結果を出力
    if all_results:
        logger.write_translation_results(all_results, filename="translation_results_all.csv")
        logger.write_evaluation_results(all_results, filename="evaluation_results_all.csv")
        logger.print_summary(all_results)


def main():
    """
    メインエントリーポイント
    """
    args = parse_arguments()
    
    # システム初期化
    config_loader, data_loader, translator_adapter, evaluator, logger = initialize_system(
        str(PROJECT_ROOT),
        enable_execution=args.execute
    )
    
    # リストモード
    if args.list:
        list_pairs(config_loader)
        return
    
    # 単一ペア処理
    if args.pair:
        process_single_pair(args.pair, evaluator, logger)
        return
    
    # 全ペア処理
    if args.all:
        process_all_pairs(config_loader, evaluator, logger)
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n処理が中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"\n致命的なエラーが発生しました:")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
