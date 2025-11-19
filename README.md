# EDOAL SPARQL Rewriter - Compose & Union Support

## 概要

このプロジェクトは、EDOALアラインメント定義に基づいてSPARQLクエリを自動変換するシステムです

## 主要機能

### 対応パターン

**edoal:or (UNION)**: 複数の代替パスを SPARQL UNION 句に変換  
**edoal:compose (Property Chain)**: プロパティ連鎖を中間変数を使った複数トリプルに展開  
**edoal:inverse**: プロパティの逆方向パスをサポート  
**複合パターン**: or の中に compose がネストされた構造も処理可能

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
### 検証済みデータセット

- agronomic-voc (農学語彙)
- conference (学会データ)
- taxons (分類学)
- agro-db (農業データベース)

### テストの実行

```bash
# 全データセットでの実行
python3 main.py
```
