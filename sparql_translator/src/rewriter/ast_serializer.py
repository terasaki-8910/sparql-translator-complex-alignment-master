import pprint

class AstSerializer:
    """
    JSON ASTをSPARQLクエリ文字列に再構築（シリアライズ）する。
    """

    def serialize(self, ast: dict) -> str:
        """
        ASTのトップレベルからシリアライズを開始する。
        """
        # TODO: SELECT, CONSTRUCTなど、クエリタイプに応じて処理を分岐
        
        query_string = self._serialize_prefixes(ast.get('prefixes', {}))
        query_string += "\nSELECT ?rank WHERE {\n" # TODO: SELECT句を動的に構築
        query_string += self._serialize_node(ast.get('ast', {}))
        query_string += "}\n"
        
        return query_string

    def _serialize_prefixes(self, prefixes: dict) -> str:
        """PREFIX句を文字列に変換する。"""
        return "\n".join([f"PREFIX {prefix}: <{uri}>" for prefix, uri in prefixes.items()]) + "\n"

    def _serialize_node(self, node: dict) -> str:
        """
        ASTノードを再帰的にシリアライズする。
        """
        if not isinstance(node, dict):
            return str(node)

        node_type = node.get('type')
        
        if node_type == 'group':
            return " ".join([self._serialize_node(p) for p in node.get('patterns', [])])
        
        if node_type == 'bgp':
            return " ".join([self._serialize_node(t) for t in node.get('triples', [])]) + " "
            
        if node_type == 'triple':
            s = self._serialize_node(node.get('subject', {}))
            p = self._serialize_node(node.get('predicate', {}))
            o = self._serialize_node(node.get('object', {}))
            return f"{s} {p} {o}."
            
        if node_type == 'uri':
            # TODO: prefixesを使ってqnameに短縮する
            return f"<{node.get('value')}>"
            
        if node_type == 'variable':
            return f"?{node.get('value')}"
            
        if node_type == 'filter':
            return f"FILTER({node.get('expression')})"
            
        return "" # 未対応のノードタイプ

if __name__ == '__main__':
    # --- テスト用の書き換え済みAST ---
    rewritten_ast = {
        'ast': {'patterns': [{'triples': [{'object': {'type': 'variable', 'value': 'label'},
                                            'predicate': {'type': 'uri', 'value': 'http://dbpedia.org/ontology/label'},
                                            'subject': {'type': 'variable', 'value': 's'},
                                            'type': 'triple'}],
                               'type': 'bgp'}],
                 'type': 'group'},
        'prefixes': {'dbo': 'http://dbpedia.org/ontology/'}
    }

    print("--- Input AST ---")
    pprint.pprint(rewritten_ast)

    # シリアライザーを実行
    serializer = AstSerializer()
    sparql_query = serializer.serialize(rewritten_ast)

    print("\n--- Serialized SPARQL Query ---")
    print(sparql_query)