"""
クエリ仲介層: parser と rewriter をつなげるシンプルな仲介クラス
"""
from src.parser.alignment_parser import parse_alignment
from src.rewriter.query_rewriter import rewrite_query
from src.common.logger import get_logger
import os


class QueryMediator:
    """クエリ仲介クラス

    使い方:
        mediator = QueryMediator(verbose=True)
        new_q, info = mediator.convert_query(sparql_text, alignment_path)
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = get_logger('query_mediator', verbose)

    def convert_query(self, sparql_query: str, alignment_path: str):
        """SPARQL クエリをアラインメントに基づき変換する

        Args:
            sparql_query (str): 変換元 SPARQL
            alignment_path (str): EDOAL アラインメントファイルパス

        Returns:
            tuple: (new_query: str, info: dict)
        """
        try:
            mapping = parse_alignment(alignment_path, verbose=self.verbose)
        except Exception as e:
            self.logger.error(f"アラインメントのパースに失敗: {e}")
            raise

        result = rewrite_query(sparql_query, mapping, verbose=self.verbose)

        info = {
            'applied_rules': result.applied_rules,
            'matches': result.matches,
            'rules_count': len(mapping.rules)
        }

        return result.new_query, info


if __name__ == '__main__':
    # 簡易デモ
    mediator = QueryMediator(verbose=True)
    example_q = """
    SELECT * WHERE { <http://example.org/A> <http://example.org/prop> ?o . }
    """
    # alignment_path を指定して試す
    print('Demo finished')
