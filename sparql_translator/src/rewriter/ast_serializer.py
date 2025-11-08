import pprint, re

def split_sparql_before_prefix(query_string):
    
    # SELECT, CONSTRUCT, DESCRIBE, ASK のいずれかで分割する
    # (大文字小文字を区別しない)
    # \s* はキーワードの直前にある改行や空白も含めてクエリ本体(part2)に含めるため
    pattern = re.compile(r"(\s*(?:SELECT|CONSTRUCT|DESCRIBE|ASK)\b)", re.IGNORECASE)
    
    # search() を使って、最初に出現するキーワードを探す
    match = pattern.search(query_string)
    
    if match:
        # キーワードが見つかった位置（キーワード直前の空白も含む）
        split_index = match.start()
        
        # 0番目: キーワードの手前まで
        part1 = query_string[:split_index]
        # 1番目: キーワード以降
        part2 = query_string[split_index:]
        
        return [part1, part2]
    else:
        # SELECTなどが見つからなかった場合
        return [query_string, ""]

# クエリのトリプルの終わりを改行する
def format_triple_endings(sparql_query: str) -> str:
    lines = sparql_query.splitlines()
    formatted_lines = []
    for line in lines:
        stripped_line = line.rstrip()
        if stripped_line.endswith('.'):
            formatted_lines.append(stripped_line)
        elif '.' in stripped_line:
            # ドットが角括弧や引用符内にある場合は分割対象から除外する
            s = stripped_line
            out = []
            in_angle = in_dq = in_sq = False
            i = 0
            L = len(s)
            for i in range(L):
                c = s[i]
                # 状態遷移（角括弧、ダブルクオート、シングルクオート）
                if c == '<' and not (in_dq or in_sq):
                    in_angle = True
                elif c == '>' and in_angle:
                    in_angle = False
                elif c == '"' and not (in_angle or in_sq):
                    in_dq = not in_dq
                elif c == "'" and not (in_angle or in_dq):
                    in_sq = not in_sq
                # ドットで、かつ角括弧やクオート内でなければ分割候補
                if c == '.' and not (in_angle or in_dq or in_sq):
                    next_char = s[i + 1] if i + 1 < L else ''
                    # 次の文字が空白か行末であればトリプル終端と判断して改行を挿入
                    if next_char == '' or next_char.isspace():
                        out.append('.\n')
                        i += 1
                        continue
                out.append(c)
                i += 1

            reconstructed = ''.join(out)
            formatted_lines.extend([ln.rstrip() for ln in reconstructed.split('\n')])
        else:
            formatted_lines.append(stripped_line)
    return '\n'.join(formatted_lines)

class AstSerializer:
    def __init__(self):
        self.prefixes = {}
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
        # プレフィックスを書き換えクエリのトリプルのURIに統合する
        query_string = self.integrate_prefixes(query_string)
        return format_triple_endings(query_string)

    def _serialize_prefixes(self, prefixes: dict) -> str:
        for prefix, uri in prefixes.items():
            self.prefixes[prefix] = uri
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
    
    # --- 追加のノードタイプのシリアライズメソッドをここに実装していく ---
    # プレフィックスを書き換えクエリのトリプルのURIに統合する
    def integrate_prefixes(self, sparql_query: str) -> str:
    # --- 2. URIの「長さ」で降順ソート ---
        # (例: 'http://example.com/foo/bar/' を 'http://example.com/foo/' より先に処理する)
        # sorted() はタプルのリストを返す: [('prefix', 'long_uri'), ('prefix', 'short_uri')]
        sorted_prefixes = sorted(
            self.prefixes.items(), 
            key=lambda item: len(item[1]),  # item[1] はURI
            reverse=True
        )
        sparql_prefix, sparql_body = split_sparql_before_prefix(sparql_query)
        current_query_body = sparql_body

        # --- 3. ソートした順序で置換を実行 ---
        for prefix, uri in sorted_prefixes:
            # URIが正規表現の特殊文字（例: . ? +）を含んでいても安全に扱えるようエスケープ
            escaped_uri = re.escape(uri)

            # 正規表現パターン: <(エスケープしたURI)(>以外の任意の1文字以上)>
            # (例: <http://dbpedia.org/ontology/)(label)>
            #    グループ1: label
            pattern = re.compile(r"<" + escaped_uri + r"([^>]+)>")

            # 置換後の形式: prefix:(グループ1)
            # (例: dbo:label)
            replacement = prefix + r":\1"

            # re.sub() を使って、文字列内のすべての一致を置換
            current_query_body = pattern.sub(replacement, current_query_body)

        return sparql_prefix + current_query_body

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