"""
簡易 SPARQL クエリ書き換えモジュール
- 現状はテキストベースの置換を行う（<...> 中の URI を主に置換）
- mapping.entity_map の key が出現するたびに置換し、適用ルール数をカウント

注意: 本実装は教育/プロトタイプ用途のための簡易リライタです。
より厳密には SPARQL 構文木を解析して置換する必要があります。
"""
from typing import Tuple, List
import re
from src.common.logger import get_logger


class RewriteResult:
    """書き換え結果を保持するデータクラス

    Attributes:
        new_query (str): 変換後クエリ
        applied_rules (int): 適用されたルール数
        matches (List[Tuple[str,str,int]]): (source, target, count) のリスト
    """

    def __init__(self, new_query: str, applied_rules: int, matches: List[Tuple[str, str, int]]):
        self.new_query = new_query
        self.applied_rules = applied_rules
        self.matches = matches


def rewrite_query(query: str, mapping, verbose: bool = False) -> RewriteResult:
    """提供された mapping に基づいて query を書き換える

    Args:
        query (str): ソースSPARQLクエリ
        mapping (AlignmentMapping): parser が作るマッピングオブジェクト
        verbose (bool): 詳細ログ

    Returns:
        RewriteResult
    """
    logger = get_logger('query_rewriter', verbose)
    new_q = query
    matches = []
    applied_rules = 0

    # 置換戦略: mapping.entity_map のキーを、角括弧で囲まれた URI (<...>) の中で検索して置換
    # また単純な全体文字列マッチでも置換を試みる
    for src, tgt in mapping.entity_map.items():
        count = 0
        # 1) <...> の中の完全一致
        pattern = re.escape(f"<{src}>")
        repl = f"<{tgt}>"
        new_q, count1 = re.subn(pattern, repl, new_q)
        count += count1

        # 2) 生の URI がそのまま出ている場合（稀）
        if count == 0:
            pattern2 = re.escape(src)
            new_q, count2 = re.subn(pattern2, tgt, new_q)
            count += count2

        if count > 0:
            applied_rules += 1
            matches.append((src, tgt, count))
            logger.debug(f"ルール適用: {src} -> {tgt} ({count} 回)")

    logger.info(f"適用されたルール総数: {applied_rules}")
    if verbose:
        logger.debug('変換後クエリ:\n' + new_q)
    return RewriteResult(new_q, applied_rules, matches)
