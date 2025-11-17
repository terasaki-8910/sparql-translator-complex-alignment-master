# EDOAL SPARQL Rewriter 改修完了報告

## 📋 実施概要

**実施日**: 2025年11月17日  
**対象コンポーネント**: 
- `sparql_translator/src/parser/edoal_parser.py`
- `sparql_translator/src/rewriter/sparql_rewriter.py`

## 🎯 目的

EDOALアラインメント定義に含まれる `edoal:or` (UNION) と `edoal:compose` (Property Chain) の複合パターンを正しくSPARQLクエリに変換できるようにする。

## 🐛 問題点

### 1. PathConstructor の無視
`_expand_complex_relation` メソッドが `edoal:or` のオペランドとして `IdentifiedEntity` しか処理せず、`PathConstructor` (特に `edoal:compose`) を無視していた。

```python
# 修正前（問題あり）
for operand in entity.operands:
    if isinstance(operand, IdentifiedEntity):
        # 処理する
    # PathConstructor は無視される！
```

### 2. 変数スコープの断絶
compose 展開時に中間変数を生成する際、最終的な目的語（Object）を元のクエリの変数に再結合させていなかった。これによりFILTER句が対象変数を失い、正しく機能しない。

## ✅ 実施内容

### Step 1: パーサーの検証強化

**ファイル**: `edoal_parser.py`

#### 変更内容
- `__init__` メソッドに `verbose` フラグを追加
- 論理演算子・パス構成子のパース時にデバッグログを追加
- operands リストの内容を検証可能にした

```python
def __init__(self, file_path, verbose=False):
    self.verbose = verbose
    # ...

# _parse_entity メソッド内
if self.verbose:
    print(f"[DEBUG EdoalParser] Parsed {tag} with {len(operands)} operands:")
    for idx, op in enumerate(operands):
        print(f"  Operand {idx}: {type(op).__name__} - {op}")
```

#### 検証結果
✅ `edoal:or` が 5 オペランド（2つの単純Property + 2つのcompose + 1つの重複）を正しくパース  
✅ `edoal:compose` が 2 プロパティ連鎖を正しくパース  
✅ ネスト構造 (or の中に compose) も正常に解析

### Step 2: リライターロジックの拡張

**ファイル**: `sparql_rewriter.py`

#### 変更1: `__init__` メソッドの拡張
```python
def __init__(self, alignment: Alignment, verbose=False):
    # ...
    self.verbose = verbose
```

#### 変更2: `_expand_complex_relation` メソッドの改修

**修正前の問題**:
```python
elif entity.operator == 'or':
    for operand in entity.operands:
        if isinstance(operand, IdentifiedEntity):
            # 単純なプロパティのみ処理
            triple = {...}
            union_patterns.append(...)
    # PathConstructor は処理されない！
```

**修正後**:
```python
elif entity.operator == 'or':
    for idx, operand in enumerate(entity.operands):
        if isinstance(operand, IdentifiedEntity):
            # 単純なプロパティ
            triple = {...}
            union_patterns.append({'type': 'bgp', 'triples': [triple]})
        
        elif isinstance(operand, PathConstructor):
            if operand.operator == 'compose':
                # 新規メソッドで連鎖を展開
                triples = self._expand_compose_path(subject_node, operand, object_node)
                union_patterns.append({'type': 'bgp', 'triples': triples})
            
            elif operand.operator == 'inverse':
                # 主語と目的語を入れ替え
                triple = {
                    'subject': object_node,  # 逆転
                    'predicate': {...},
                    'object': subject_node   # 逆転
                }
                union_patterns.append(...)
```

#### 変更3: 新規メソッド `_expand_compose_path` の実装

**設計原則**:
- **始点**: 必ず `subject_node` (元のクエリの主語)
- **終点**: 必ず `object_node` (元のクエリの目的語)
- **中間点**: 一時変数を生成

```python
def _expand_compose_path(self, subject_node, path_constructor, object_node):
    """
    edoal:compose をトリプル連鎖に展開
    
    例: compose(p1, p2) + 主語 ?s, 目的語 ?o
    → ?s p1 ?temp0 . ?temp0 p2 ?o
    """
    properties = [op.uri for op in path_constructor.operands]
    triples = []
    current_subject = subject_node
    
    for i, prop_uri in enumerate(properties):
        if i == len(properties) - 1:
            current_object = object_node  # 最後は元の目的語
        else:
            current_object = self._generate_temp_var()
        
        triples.append({
            'type': 'triple',
            'subject': current_subject,
            'predicate': {'type': 'uri', 'value': prop_uri},
            'object': current_object
        })
        
        current_subject = current_object  # 次の主語は現在の目的語
    
    return triples
```

### Step 3: 実データ検証

**ファイル**: `test_rewriter_with_real_data.py`

実際のアラインメントファイル (`agronomic-voc/alignment/alignment.edoal`) とクエリパターンを使用した3つのテストケース:

#### ✅ Test Case 1: FILTER with regex (query_1.sparql)

**元のクエリ**:
```sparql
?taxon agro:prefScientificName ?label.
FILTER (regex(?label, "^triticum$","i"))
```

**検証項目**:
- UNION 構造が生成されたか
- compose が展開されたか
- FILTER が元の変数 `?label` を正しく参照しているか

**結果**: ✅ Pass  
- UNION 構造: ✅ 生成
- compose 展開: ✅ `?taxon --prefLabel--> ?temp0 --literalForm--> ?label`
- FILTER 変数追跡: ✅ `?label` が保持

#### ✅ Test Case 2: OR/UNION pattern (query_4.sparql)

**元のクエリ**:
```sparql
?taxon agro:prefVernacularName ?commonName.
```

**検証項目**:
- UNION構造が検出されたか
- 複数ブランチが生成されたか
- 変数の一貫性が保たれているか

**結果**: ✅ Pass  
- UNION 検出: ✅ 構造確認
- 複数ブランチ: ✅ 単純プロパティ + compose連鎖
- 変数一貫性: ✅ `?commonName` が全ブランチで一致

#### ✅ Test Case 3: Compose + Type checking (query_5.sparql)

**元のクエリ**:
```sparql
?taxon agro:hasLowerRank ?specy.
?specy a agro:SpecyRank.
```

**検証項目**:
- 一時変数が生成されたか
- compose 連鎖が展開されたか
- 制約が FILTER に変換されたか

**結果**: ✅ Pass  
- 一時変数生成: ✅ `variable_temp0`, `variable_temp1`
- compose 連鎖: ✅ 正しく展開
- 制約→FILTER: ✅ AttributeValueRestriction 変換成功

## 📊 変換例

### 入力 (Source Ontology)
```sparql
PREFIX agro: <http://ontology.irstea.fr/agronomictaxon/core#>

SELECT ?rank WHERE {
  ?taxon agro:prefScientificName ?label.
  ?taxon a ?rank.
  FILTER (regex(?label, "^triticum$","i"))
}
```

### EDOAL アラインメント (抜粋)
```xml
<Property>
  <or rdf:parseType="Collection">
    <!-- Branch 1: 単純なプロパティ -->
    <Property rdf:about="http://www.w3.org/2004/02/skos/core#prefLabel"/>
    
    <!-- Branch 2: プロパティ連鎖 (compose) -->
    <compose rdf:parseType="Collection">
      <Relation rdf:about="http://www.w3.org/2008/05/skos-xl#prefLabel"/>
      <Property rdf:about="http://www.w3.org/2008/05/skos-xl#literalForm"/>
    </compose>
  </or>
</Property>
```

### 出力 (Target Ontology)
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>

SELECT ?rank WHERE {
  {
    # Branch 1: 単純なプロパティ
    ?taxon skos:prefLabel ?label.
    ?taxon a ?rank.
  }
  UNION
  {
    # Branch 2: プロパティ連鎖 (compose)
    ?taxon skosxl:prefLabel ?variable_temp0.
    ?variable_temp0 skosxl:literalForm ?label.
    ?taxon a ?rank.
  }
  
  FILTER (regex(?label, "^triticum$", "i"))
}
```

## 🎉 達成事項

### 解決した問題

| 問題 | 状態 | 解決方法 |
|------|-----|---------|
| PathConstructor の無視 | ✅ 解決 | `or` オペレーター内で `IdentifiedEntity` と `PathConstructor` を明示的に分岐処理 |
| 変数スコープの断絶 | ✅ 解決 | compose 連鎖の始点と終点を元のクエリ変数に固定 |
| 情報の欠落 | ✅ 解決 | すべてのオペランドタイプを処理可能に |

### 実装パターン

1. **分岐処理**: `IdentifiedEntity` と `PathConstructor` を型チェックで分岐
2. **変数伝播**: 始点 (`subject_node`) と終点 (`object_node`) を保持、中間のみ一時変数
3. **構造保持**: UNION の各ブランチを独立した BGP として構築

### 拡張性

- ✅ `inverse`: 実装済み（主語・目的語の入れ替え）
- ✅ `compose`: 実装済み（プロパティ連鎖）
- 🔄 `transitive`: 将来実装可能（同様のパターンで対応可能）
- ✅ `and` との組み合わせ: 対応済み
- ✅ FILTER との併用: 変数の一貫性を維持

## 🔧 追加機能

### Verbose Mode

デバッグログを制御可能な `verbose` フラグを追加:

```python
# デバッグログを有効化
parser = EdoalParser(alignment_path, verbose=True)
rewriter = SparqlRewriter(alignment, verbose=True)

# 本番環境（ログ抑制）
parser = EdoalParser(alignment_path, verbose=False)
rewriter = SparqlRewriter(alignment, verbose=False)
```

## 📝 テスト結果サマリ

| テストケース | 検証項目 | 結果 |
|------------|---------|-----|
| query_1.sparql | UNION生成 | ✅ Pass |
| | compose展開 | ✅ Pass |
| | FILTER変数追跡 | ✅ Pass |
| query_4.sparql | UNION検出 | ✅ Pass |
| | 複数ブランチ生成 | ✅ Pass |
| | 変数一貫性 | ✅ Pass |
| query_5.sparql | 一時変数生成 | ✅ Pass |
| | compose連鎖 | ✅ Pass |
| | 制約→FILTER変換 | ✅ Pass |
| main.py全体 | 複数データセット | ✅ Pass |
| verbose mode | ログ制御 | ✅ Pass |

## 📚 修正ファイル一覧

1. **`sparql_translator/src/parser/edoal_parser.py`**
   - `__init__` に verbose フラグ追加
   - デバッグログ追加

2. **`sparql_translator/src/rewriter/sparql_rewriter.py`**
   - `__init__` に verbose フラグ追加
   - `_expand_complex_relation` メソッド改修
   - `_expand_compose_path` メソッド新規追加
   - デバッグログ制御

3. **`test_rewriter_with_real_data.py`** (新規作成)
   - 実データを使った検証スクリプト

4. **`test_verbose_mode.py`** (新規作成)
   - verbose フラグの動作確認スクリプト

5. **`IMPLEMENTATION_SUMMARY.md`** (新規作成)
   - 改修内容の詳細ドキュメント

## 🚀 今後の拡張可能性

### 優先度: 高
- [ ] `transitive` オペレーターのサポート (プロパティパスの `*` または `+` に対応)
- [ ] エラーハンドリングの強化（operands が空の場合のガード処理）

### 優先度: 中
- [ ] パフォーマンス最適化（同一の一時変数が重複生成される場合の統合）
- [ ] 複雑なネスト構造（`and` と `or` の多重ネスト）のテスト強化

### 優先度: 低
- [ ] ユニットテストの追加（pytest フレームワーク）
- [ ] CI/CD パイプラインへの統合

## ✅ 結論

**状態**: 🎉 完了

- ✅ `edoal:or` と `edoal:compose` の複合パターンを正しく SPARQL UNION + プロパティ連鎖に変換可能
- ✅ 実際のアラインメントファイルとクエリを使用したテストで動作確認完了
- ✅ 拡張性の高い設計により、他の PathConstructor オペレーターにも適用可能
- ✅ verbose モードによりデバッグと本番環境の両方をサポート

---

**作成日**: 2025年11月17日  
**作成者**: GitHub Copilot  
**対応バージョン**: sparql-translator-complex-alignment v1.1
