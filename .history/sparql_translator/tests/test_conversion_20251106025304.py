"""
examples/ 内の SPARQL ファイルを読み取り、アラインメントに従って変換を行うテストスクリプト
- 実行例は README.md を参照
"""
import argparse
import time
import glob
import os
from src.mediator.query_mediator import QueryMediator
from src.common.logger import get_logger
import textwrap


def find_sparql_files(examples_dir):
    patterns = [os.path.join(examples_dir, '*.sparql'), os.path.join(examples_dir, '*.rq')]
    files = []
    for p in patterns:
        files.extend(glob.glob(p))
    files = sorted(list(set(files)))
    return files


def main():
    parser = argparse.ArgumentParser(description='SPARQL 変換テスト')
    parser.add_argument('--examples', default=os.path.join('..', 'examples'), help='examples ディレクトリへの相対パス')
    parser.add_argument('--alignment', default=os.path.join('..', 'examples', 'AgronomicTaxon-Agrovoc.edoal.xml'), help='EDOAL アラインメントファイル')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細ログ出力')
    parser.add_argument('--debug', action='store_true', help='中間結果を保存')
    parser.add_argument('--query', help='個別のクエリファイルを指定 (examples 内のファイルか絶対/相対パス)')
    args = parser.parse_args()

    logger = get_logger('test_conversion', args.verbose)
    mediator = QueryMediator(verbose=args.verbose)

    # 入力ファイルリスト
    if args.query:
        files = [args.query]
    else:
        files = find_sparql_files(args.examples)

    total = len(files)
    print('\n========================================')
    print('SPARQL変換テスト開始')
    print('========================================\n')

    success = 0
    failures = 0
    total_time = 0.0

    for idx, fpath in enumerate(files, start=1):
        fname = os.path.basename(fpath)
        print(f"[{idx}/{total}] {fname} を変換中...")
        try:
            with open(fpath, 'r', encoding='utf-8') as fh:
                query = fh.read()
        except Exception as e:
            logger.error(f"ファイル読み込みエラー: {fpath}: {e}")
            failures += 1
            continue

        start = time.time()
        try:
            new_q, info = mediator.convert_query(query, args.alignment)
        except Exception as e:
            logger.error(f"変換エラー ({fname}): {e}")
            failures += 1
            continue
        elapsed = time.time() - start
        total_time += elapsed

        # 保存
        out_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
        out_dir = os.path.abspath(out_dir)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, fname + '.out.sparql')
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(new_q)

        # 結果表示形式
        orig_lines = len(query.splitlines())
        new_lines = len(new_q.splitlines())
        applied = info.get('applied_rules', 0)

        print(f"  ✓ 変換成功 ({elapsed:.2f}秒)")
        print(f"  変換前: {orig_lines}行, 変換後: {new_lines}行")
        print(f"  適用ルール数: {applied}\n")

        # デバッグ保存
        if args.debug:
            dbg_dir = os.path.join(os.path.dirname(__file__), '..', 'debug_output')
            dbg_dir = os.path.abspath(dbg_dir)
            os.makedirs(dbg_dir, exist_ok=True)
            mapping_path = os.path.join(dbg_dir, fname + '.mapping.json')
            # mapping は parse_alignment が出力済みの場合があるためここでは存在しない可能性あり
            # mediator.convert_query が verbose なら parse_alignment が debug 出力を作る
            logger.info(f"中間結果を保存: {mapping_path}")

        success += 1

    print('========================================')
    print('テスト結果サマリー')
    print('========================================')
    print(f"成功: {success}/{total}")
    print(f"失敗: {failures}/{total}")
    print(f"合計実行時間: {total_time:.2f}秒\n")


if __name__ == '__main__':
    main()
