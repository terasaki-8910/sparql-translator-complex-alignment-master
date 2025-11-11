from .ast_walker import AstWalker
from ..parser.edoal_parser import (
    Alignment, Cell, IdentifiedEntity, LogicalConstructor, PathConstructor,
    AttributeDomainRestriction, AttributeValueRestriction, AttributeOccurenceRestriction,
    RelationDomainRestriction, RelationCoDomainRestriction
)
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
        # 新しい変数を生成するためのカウンター
        self.temp_var_counter = 0

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

    def visit_group(self, node):
        """
        Group ノードを訪問し、パターンを処理する。
        子パターンがUNIONを返す場合、適切に統合する。
        """
        new_patterns = []
        
        for pattern in node.get('patterns', []):
            result = self._walk_node(pattern)
            
            # 結果がUNIONの場合、そのまま追加
            if isinstance(result, dict) and result.get('type') == 'union':
                new_patterns.append(result)
            elif isinstance(result, list):
                # リストの場合は展開
                new_patterns.extend(result)
            else:
                new_patterns.append(result)
        
        return {**node, 'patterns': new_patterns}

    def visit_bgp(self, node):
        """
        BGP (Basic Graph Pattern) ノードを訪問
        複数のトリプルが1つのトリプルから複数に展開される場合や、
        UNION構造やFILTERが生成される場合を処理する。
        """
        new_triples = []
        filters = []  # FILTERを別途収集
        has_union = False
        union_structure = None
        
        for triple in node.get('triples', []):
            result = self._walk_node(triple)
            
            # 結果がリストの場合（複数トリプルへの展開、またはトリプル+FILTER）
            if isinstance(result, list):
                # リスト内の各要素を処理
                for item in result:
                    if isinstance(item, dict):
                        if item.get('type') == 'union':
                            has_union = True
                            union_structure = item
                        elif item.get('type') == 'filter':
                            # FILTERは別途収集
                            filters.append(item)
                        elif item.get('type') == 'triple':
                            new_triples.append(item)
                        else:
                            # その他のノードタイプ
                            new_triples.append(item)
                    else:
                        new_triples.append(item)
            else:
                new_triples.append(result)
        
        # UNIONが含まれている場合、構造を再編成
        if has_union and union_structure:
            # UNIONの各パターンに既存のトリプルを追加
            for pattern in union_structure['patterns']:
                if pattern.get('type') == 'bgp':
                    # 既存のトリプルをこのパターンに追加
                    pattern['triples'].extend(new_triples)
            
            # FILTERがある場合、groupでラップして返す
            if filters:
                return {
                    'type': 'group',
                    'patterns': [union_structure] + filters
                }
            
            # UNION構造全体を返す（親のgroupパターンがこれを処理する）
            return union_structure
        
        # FILTERがある場合、groupでラップしてBGP+FILTERを返す
        if filters:
            return {
                'type': 'group',
                'patterns': [{'type': 'bgp', 'triples': new_triples}] + filters
            }
        
        # 通常のBGPを返す
        return {**node, 'triples': new_triples}

    def _generate_temp_var(self):
        """新しい一時変数を生成する"""
        var_name = f"variable_temp{self.temp_var_counter}"
        self.temp_var_counter += 1
        return {'type': 'variable', 'value': var_name}

    def visit_triple(self, node):
        """
        トリプルノードを訪問した際に、主語・述語・目的語のいずれかが
        複雑な書き換えルールを持つかチェックする。
        """
        # まず、各要素（主語、述語、目的語）を再帰的に書き換える
        s = self._walk_node(node['subject'])
        p = self._walk_node(node['predicate'])
        o = self._walk_node(node['object'])

        # 述語が書き換え対象のURIの場合（Relationのマッピング）
        if p.get('type') == 'uri' and p.get('value') in self.mapping:
            target_entity = self.mapping[p['value']]
            
            # ターゲットが複雑なRelation（LogicalConstructor含む）の場合
            if not isinstance(target_entity, IdentifiedEntity):
                print(f"  [Rewrite] Complex rewrite for predicate: {p['value']}")
                try:
                    self.logger.info(f"[Rewrite] Complex rewrite for predicate: {p['value']}")
                except Exception:
                    pass
                
                # 複雑なRelationを展開（ドメイン/コドメイン制約を処理）
                expanded_triples = self._expand_complex_relation(s, target_entity, o)
                
                if expanded_triples:
                    return expanded_triples

        # 目的語が書き換え対象のURIで、かつrdf:typeのトリプルの場合
        if (o.get('type') == 'uri' and 
            o.get('value') in self.mapping and
            p.get('type') == 'uri' and 
            'rdf-syntax-ns#type' in p.get('value', '')):
            
            target_entity = self.mapping[o['value']]
            
            # ターゲットが単純なURIでない場合（＝複雑なエンティティ）
            if not isinstance(target_entity, IdentifiedEntity):
                print(f"  [Rewrite] Complex rewrite for object: {o['value']}")
                try:
                    self.logger.info(f"[Rewrite] Complex rewrite for object: {o['value']}")
                except Exception:
                    pass
                
                # 複雑なエンティティを複数のトリプルに展開
                expanded_triples = self._expand_complex_entity(s, target_entity)
                
                if expanded_triples:
                    # 複数のトリプルを返す（リストとして返すことで、ast_walkerが展開する）
                    return expanded_triples

        # 新しいトリプルを構築して返す
        return {**node, 'subject': s, 'predicate': p, 'object': o}

    def _expand_complex_entity(self, subject_node, entity):
        """
        複雑なエンティティ（LogicalConstructor, AttributeDomainRestriction等）を
        複数のトリプルに展開する。
        
        :param subject_node: トリプルの主語ノード
        :param entity: 複雑なエンティティオブジェクト
        :return: トリプルのリスト
        """
        if isinstance(entity, LogicalConstructor):
            if entity.operator == 'and':
                # ANDの場合、すべてのoperandを展開して結合
                all_triples = []
                for operand in entity.operands:
                    triples = self._expand_complex_entity(subject_node, operand)
                    if triples:
                        all_triples.extend(triples)
                return all_triples
            
            elif entity.operator == 'or':
                # ORの場合は、UNION構造を生成する
                # 各operandに対して、rdf:typeトリプルを生成し、それらをUNIONで結合
                print(f"    [Info] Expanding OR operator with {len(entity.operands)} operands")
                
                # 各operandからトリプルを生成
                union_patterns = []
                for operand in entity.operands:
                    if isinstance(operand, IdentifiedEntity):
                        # 単純なクラスの場合
                        triple = {
                            'type': 'triple',
                            'subject': subject_node,
                            'predicate': {'type': 'uri', 'value': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                            'object': {'type': 'uri', 'value': operand.uri}
                        }
                        # 各トリプルをBGPで包む
                        union_patterns.append({
                            'type': 'bgp',
                            'triples': [triple]
                        })
                
                if union_patterns:
                    # UNION構造を返す
                    # 注意: この構造は親のBGP内に直接配置されるべきではない
                    # 代わりに、親のgroupパターンに挿入する必要がある
                    # 今のところ、特殊なマーカーを返す
                    return [{
                        'type': 'union',
                        'patterns': union_patterns
                    }]
                
                return []
        
        elif isinstance(entity, IdentifiedEntity):
            # 単純なクラスURIの場合、rdf:typeトリプルを生成
            return [{
                'type': 'triple',
                'subject': subject_node,
                'predicate': {'type': 'uri', 'value': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                'object': {'type': 'uri', 'value': entity.uri}
            }]
        
        elif isinstance(entity, AttributeDomainRestriction):
            # AttributeDomainRestriction の場合
            # 例: ?paper :hasDecision ?temp0. ?temp0 rdf:type :Acceptance.
            temp_var = self._generate_temp_var()
            
            triples = []
            
            # 1つ目のトリプル: subject -> onAttribute -> temp_var
            if hasattr(entity.on_attribute, 'uri'):
                triples.append({
                    'type': 'triple',
                    'subject': subject_node,
                    'predicate': {'type': 'uri', 'value': entity.on_attribute.uri},
                    'object': temp_var
                })
            
            # 2つ目のトリプル: temp_var rdf:type class_expression
            if hasattr(entity.class_expression, 'uri'):
                triples.append({
                    'type': 'triple',
                    'subject': temp_var,
                    'predicate': {'type': 'uri', 'value': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                    'object': {'type': 'uri', 'value': entity.class_expression.uri}
                })
            
            return triples
        
        elif isinstance(entity, AttributeValueRestriction):
            # AttributeValueRestriction の場合
            # 例: ?person :earlyRegistration ?temp0. FILTER(?temp0 = true)
            temp_var = self._generate_temp_var()
            
            triples = []
            filters = []
            
            # 1つ目のトリプル: subject -> onAttribute -> temp_var
            if hasattr(entity.on_attribute, 'uri'):
                triples.append({
                    'type': 'triple',
                    'subject': subject_node,
                    'predicate': {'type': 'uri', 'value': entity.on_attribute.uri},
                    'object': temp_var
                })
            
            # FILTER条件を生成
            filter_expr = self._create_filter_expression(temp_var, entity.comparator, entity.value)
            if filter_expr:
                filters.append({
                    'type': 'filter',
                    'expression': filter_expr
                })
            
            # トリプルとFILTERを結合して返す
            return triples + filters
        
        elif isinstance(entity, AttributeOccurenceRestriction):
            # AttributeOccurenceRestriction の場合
            # 例: "greater-than 0" は属性が存在することを意味する
            # SPARQLでは単にトリプルを追加することで表現（存在チェック）
            
            # comparatorが "greater-than" で value が 0 の場合は単純な存在チェック
            if 'greater-than' in entity.comparator and entity.value == 0:
                # 単にトリプルを生成（プロパティが存在することを確認）
                temp_var = self._generate_temp_var()
                
                if hasattr(entity.on_attribute, 'uri'):
                    # 単純なプロパティの場合
                    return [{
                        'type': 'triple',
                        'subject': subject_node,
                        'predicate': {'type': 'uri', 'value': entity.on_attribute.uri},
                        'object': temp_var
                    }]
                elif isinstance(entity.on_attribute, PathConstructor):
                    # PathConstructor（inverse等）の場合
                    if entity.on_attribute.operator == 'inverse' and len(entity.on_attribute.operands) > 0:
                        # inverse(P) の場合、トリプルの主語と目的語を入れ替える
                        operand = entity.on_attribute.operands[0]
                        if hasattr(operand, 'uri'):
                            return [{
                                'type': 'triple',
                                'subject': temp_var,
                                'predicate': {'type': 'uri', 'value': operand.uri},
                                'object': subject_node
                            }]
                    else:
                        # その他のPathConstructorは現在未対応
                        print(f"    [Warning] PathConstructor '{entity.on_attribute.operator}' in AttributeOccurenceRestriction not fully supported")
                        return []
                else:
                    print(f"    [Warning] Complex on_attribute in AttributeOccurenceRestriction not fully supported")
                    return []
            else:
                # その他の出現回数制約は現在未対応
                print(f"    [Warning] AttributeOccurenceRestriction with comparator {entity.comparator} and value {entity.value} not fully implemented")
                return []
        
        return []
    
    def _expand_complex_relation(self, subject_node, entity, object_node):
        """
        複雑なRelation（LogicalConstructor, RelationDomainRestriction等）を
        複数のトリプルに展開する。
        
        :param subject_node: トリプルの主語ノード
        :param entity: 複雑なRelationエンティティオブジェクト
        :param object_node: トリプルの目的語ノード
        :return: トリプルのリスト
        """
        if isinstance(entity, LogicalConstructor):
            if entity.operator == 'and':
                # ANDの場合、すべてのoperandを処理
                all_triples = []
                base_predicate = None
                domain_restrictions = []
                codomain_restrictions = []
                
                for operand in entity.operands:
                    if isinstance(operand, IdentifiedEntity):
                        # 単純なRelation（述語）の場合
                        base_predicate = operand
                    elif isinstance(operand, RelationDomainRestriction):
                        domain_restrictions.append(operand)
                    elif isinstance(operand, RelationCoDomainRestriction):
                        codomain_restrictions.append(operand)
                    else:
                        # その他の複雑な構造を再帰的に処理
                        nested_triples = self._expand_complex_relation(subject_node, operand, object_node)
                        if nested_triples:
                            all_triples.extend(nested_triples)
                
                # 基本のトリプルを生成
                if base_predicate and hasattr(base_predicate, 'uri'):
                    all_triples.append({
                        'type': 'triple',
                        'subject': subject_node,
                        'predicate': {'type': 'uri', 'value': base_predicate.uri},
                        'object': object_node
                    })
                
                # ドメイン制約を処理（主語に対する型制約）
                for restriction in domain_restrictions:
                    if restriction.class_expression:
                        triples = self._expand_complex_entity(subject_node, restriction.class_expression)
                        if triples:
                            all_triples.extend(triples)
                
                # コドメイン制約を処理（目的語に対する型制約）
                for restriction in codomain_restrictions:
                    if restriction.class_expression:
                        triples = self._expand_complex_entity(object_node, restriction.class_expression)
                        if triples:
                            all_triples.extend(triples)
                
                return all_triples
            
            elif entity.operator == 'or':
                # ORの場合、UNION構造を生成
                print(f"    [Info] Expanding OR operator for predicate with {len(entity.operands)} operands")
                
                union_patterns = []
                for operand in entity.operands:
                    if isinstance(operand, IdentifiedEntity):
                        triple = {
                            'type': 'triple',
                            'subject': subject_node,
                            'predicate': {'type': 'uri', 'value': operand.uri},
                            'object': object_node
                        }
                        union_patterns.append({
                            'type': 'bgp',
                            'triples': [triple]
                        })
                
                if union_patterns:
                    return [{
                        'type': 'union',
                        'patterns': union_patterns
                    }]
                
                return []
        
        elif isinstance(entity, IdentifiedEntity):
            # 単純なRelationの場合
            return [{
                'type': 'triple',
                'subject': subject_node,
                'predicate': {'type': 'uri', 'value': entity.uri},
                'object': object_node
            }]
        
        return []
    
    def _create_filter_expression(self, var_node, comparator, value):
        """FILTER式の文字列を生成する"""
        var_name = var_node['value']
        
        # 値の文字列表現を生成
        value_str = self._format_value(value)
        
        # 比較演算子に応じた式を生成
        if comparator == 'http://ns.inria.org/edoal/1.0/#equals':
            return f"?{var_name} = {value_str}"
        elif comparator == 'http://ns.inria.org/edoal/1.0/#contains':
            return f"CONTAINS(STR(?{var_name}), {value_str})"
        elif comparator == 'http://ns.inria.org/edoal/1.0/#greaterThan':
            return f"?{var_name} > {value_str}"
        elif comparator == 'http://ns.inria.org/edoal/1.0/#lessThan':
            return f"?{var_name} < {value_str}"
        elif comparator == 'http://ns.inria.org/edoal/1.0/#greaterThanOrEqual':
            return f"?{var_name} >= {value_str}"
        elif comparator == 'http://ns.inria.org/edoal/1.0/#lessThanOrEqual':
            return f"?{var_name} <= {value_str}"
        else:
            print(f"    [Warning] Unknown comparator: {comparator}")
            return None
    
    def _format_value(self, value):
        """EDOALの値をSPARQL形式の文字列に変換する"""
        if isinstance(value, dict):
            # Literalの場合
            if 'string' in value:
                value_str = value['string']
                value_type = value.get('type', '')
                
                # データ型に応じた処理
                if 'boolean' in value_type:
                    # ブール値: true/false（小文字、クォートなし）
                    return value_str.lower()
                elif 'integer' in value_type or 'int' in value_type or 'long' in value_type:
                    # 整数: クォートなし
                    return value_str
                elif 'decimal' in value_type or 'float' in value_type or 'double' in value_type:
                    # 小数: クォートなし
                    return value_str
                elif 'string' in value_type:
                    # 文字列: ダブルクォートで囲む
                    return f'"{value_str}"'
                else:
                    # その他のデータ型: データ型付きリテラルとして出力
                    return f'"{value_str}"^^<{value_type}>'
            elif 'uri' in value:
                # URIリファレンスの場合
                return f'<{value["uri"]}>'
        elif isinstance(value, str):
            # 単純な文字列の場合
            return f'"{value}"'
        elif isinstance(value, bool):
            # Pythonのブール値
            return str(value).lower()
        elif isinstance(value, (int, float)):
            # Pythonの数値
            return str(value)
        
        # デフォルト: 文字列として扱う
        return f'"{str(value)}"'

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