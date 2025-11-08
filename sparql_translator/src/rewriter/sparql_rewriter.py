from .ast_walker import AstWalker
from ..parser.edoal_parser import Alignment, Cell, IdentifiedEntity
from ..common.logger import get_logger

class SparqlRewriter(AstWalker):
    """
    アラインメント情報に基づいてSPARQL ASTを書き換える。
    """

    def __init__(self, alignment: Alignment):
        # URIのマッピングを効率的に検索できるよう、辞書に変換しておく
        self.mapping = self._create_mapping(alignment)
        # ロガーを初期化（append モードでファイルに出力される設定）
        self.logger = get_logger('sparql_rewriter', verbose=False)

    def _create_mapping(self, alignment: Alignment) -> dict:
        """
        EDOALパーサーの出力から、書き換えのためのマッピング辞書を作成する。
        { "source_uri": <target_entity_object> }
        """
        mapping = {}
        for cell in alignment.cells:
            # ソースエンティティが単純なURIである対応関係をマッピング対象とする
            if isinstance(cell.entity1, IdentifiedEntity):
                source_uri = cell.entity1.uri
                # ターゲットエンティティ（単純な場合も複雑な場合もある）をマッピングする
                mapping[source_uri] = cell.entity2
        return mapping

    def visit_uri(self, node):
        """
        URIノードを訪問した際に、マッピングに基づいて置換を行う。
        """
        uri_to_check = node.get('value')
        target_entity = self.mapping.get(uri_to_check)

        if isinstance(target_entity, IdentifiedEntity):
            print(f"  [Rewrite] Simple URI rewrite: {uri_to_check} -> {target_entity.uri}")
            # print は残しつつログにも出力（append）
            try:
                self.logger.info(f"[Rewrite] Simple URI rewrite: {uri_to_check} -> {target_entity.uri}")
            except Exception:
                # ログ出力に失敗しても処理を継続する
                pass
            return {**node, 'value': target_entity.uri}
        
        return node

    def visit_triple(self, node):
        """
        トリプルノードを訪問した際に、主語・述語・目的語のいずれかが
        複雑な書き換えルールを持つかチェックする。
        """
        # まず、各要素（主語、述語、目的語）を再帰的に書き換える
        s = self._walk_node(node['subject'])
        p = self._walk_node(node['predicate'])
        o = self._walk_node(node['object'])

        # 目的語が書き換え対象のURIだった場合
        if o.get('type') == 'uri' and o.get('value') in self.mapping:
            target_entity = self.mapping[o['value']]
            
            # ターゲットが単純なURIでない場合（＝複雑なエンティティ）
            if not isinstance(target_entity, IdentifiedEntity):
                print(f"  [Rewrite] Complex rewrite for object: {o['value']}")
                try:
                    self.logger.info(f"[Rewrite] Complex rewrite for object: {o['value']}")
                except Exception:
                    pass
                # TODO: ここで target_entity の内容に基づいて
                # 新しいグラフパターン（複数のトリプルなど）を生成するロジックを実装
                # 今回はプレースホルダーとして元のトリプルを返す
                pass

        # 新しいトリプルを構築して返す
        return {**node, 'subject': s, 'predicate': p, 'object': o}

if __name__ == '__main__':
    # --- テスト用のダミーアラインメントデータ ---
    dummy_alignment = Alignment(
        onto1="http://example.com/source",
        onto2="http://example.com/target",
        cells=[
            Cell(
                entity1=IdentifiedEntity(uri="http://example.com/old_predicate"),
                entity2=IdentifiedEntity(uri="http://dbpedia.org/ontology/new_predicate"),
                relation="Equivalence",
                measure=1.0
            )
        ]
    )

    # --- テスト用のサンプルAST ---
    sample_ast = {
        'ast': {
            'patterns': [
                {'triples': [
                    {'object': {'type': 'variable', 'value': 'label'},
                     'predicate': {'type': 'uri', 'value': 'http://example.com/old_predicate'},
                     'subject': {'type': 'variable', 'value': 's'},
                     'type': 'triple'}
                ],
                'type': 'bgp'}
            ],
            'type': 'group'
        }
    }
    
    import pprint
    print("--- Original AST ---")
    pprint.pprint(sample_ast)

    # リライターを実行
    rewriter = SparqlRewriter(dummy_alignment)
    rewritten_ast = rewriter.walk(sample_ast)

    print("\n--- Rewritten AST ---")
    pprint.pprint(rewritten_ast)