# EDOAL SPARQL Rewriter - Compose & Union Support

## 概要

このプロジェクトは、EDOALアラインメント定義に基づいてSPARQLクエリを自動変換するシステムです

## 主要機能

### 対応パターン

✅ **edoal:or (UNION)**: 複数の代替パスを SPARQL UNION 句に変換  
✅ **edoal:compose (Property Chain)**: プロパティ連鎖を中間変数を使った複数トリプルに展開  
✅ **edoal:inverse**: プロパティの逆方向パスをサポート  
✅ **複合パターン**: or の中に compose がネストされた構造も処理可能

### 変換例

**入力 (Source Ontology)**:
```sparql
?taxon agro:prefScientificName ?label.
FILTER (regex(?label, "^triticum$", "i"))
```

**EDOAL アラインメント**:
```xml
<or>
  <Property rdf:about="skos:prefLabel"/>
  <compose>
    <Relation rdf:about="skosxl:prefLabel"/>
    <Property rdf:about="skosxl:literalForm"/>
  </compose>
</or>
```

**出力 (Target Ontology)**:
```sparql
{
  ?taxon skos:prefLabel ?label.
}
UNION
{
  ?taxon skosxl:prefLabel ?temp0.
  ?temp0 skosxl:literalForm ?label.
}
FILTER (regex(?label, "^triticum$", "i"))
```

## 使用方法

### 基本的な使用

```python
from sparql_translator.src.parser.edoal_parser import EdoalParser
from sparql_translator.src.rewriter.sparql_rewriter import SparqlRewriter

# アラインメントをパース
parser = EdoalParser('alignment.edoal')
alignment = parser.parse()

# リライターを作成
rewriter = SparqlRewriter(alignment)

# ASTを変換
rewritten_ast = rewriter.walk(original_ast)
```

### デバッグモード

```python
# デバッグログを有効化
parser = EdoalParser('alignment.edoal', verbose=True)
rewriter = SparqlRewriter(alignment, verbose=True)
```

## テスト

### 検証済みデータセット

- agronomic-voc (農学語彙)
- conference (学会データ)
- taxons (分類学)
- agro-db (農業データベース)

### テストの実行

```bash
# 実データを使った検証
python3 test_rewriter_with_real_data.py

# verboseモードのテスト
python3 test_verbose_mode.py

# 全データセットでの実行
python3 main.py
```
