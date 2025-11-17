# EDOAL SPARQL Rewriter - Compose & Union Support

## 概要

このプロジェクトは、EDOALアラインメント定義に基づいてSPARQLクエリを自動変換するシステムです。本更新では、`edoal:or` (UNION) と `edoal:compose` (Property Chain) の複合パターンに対応しました。

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

- ✅ agronomic-voc (農学語彙)
- ✅ conference (学会データ)
- ✅ taxons (分類学)
- ✅ agro-db (農業データベース)

### テストの実行

```bash
# 実データを使った検証
python3 test_rewriter_with_real_data.py

# verboseモードのテスト
python3 test_verbose_mode.py

# 全データセットでの実行
python3 main.py
```

## 技術詳細

### アーキテクチャ

```
sparql_translator/
├── src/
│   ├── parser/
│   │   ├── edoal_parser.py       # EDOAL XML → Python オブジェクト
│   │   └── sparql_ast_parser.py  # SPARQL → JSON AST (Jena)
│   └── rewriter/
│       ├── ast_walker.py         # AST巡回の基底クラス
│       ├── sparql_rewriter.py    # アラインメントに基づく変換
│       └── ast_serializer.py     # JSON AST → SPARQL (Jena)
└── test_data/                    # テストデータセット
```

### 主要コンポーネント

#### EdoalParser
- EDOAL XML を Python dataclass にマッピング
- LogicalConstructor (and/or/not) とPathConstructor (compose/inverse/transitive) をサポート

#### SparqlRewriter
- AST を再帰的に巡回して書き換え
- `_expand_complex_relation`: or/and/inverse の処理
- `_expand_compose_path`: compose の連鎖展開（重要な改修ポイント）

### 設計原則

1. **変数スコープの保持**: compose 展開時、始点と終点は元のクエリ変数を使用
2. **一時変数の生成**: 中間ノードのみ `_generate_temp_var()` で生成
3. **構造の保持**: UNION の各ブランチは独立した BGP として構築

## ドキュメント

- [`COMPLETION_REPORT.md`](COMPLETION_REPORT.md) - 詳細な改修レポート
- [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) - 技術的な実装詳細
- [`EDOAL_manual.md`](EDOAL_manual.md) - EDOAL 仕様書

## 制限事項と今後の拡張

### 現在の制限
- `transitive` オペレーターは未実装（パース済み、展開は今後の課題）
- SPARQL 1.1 のプロパティパス構文には非対応（代わりに中間変数を使用）

### 将来の拡張
- [ ] `transitive` のサポート (`*` または `+` 演算子への対応)
- [ ] 最適化（重複する一時変数の統合）
- [ ] ユニットテストの充実
- [ ] エラーハンドリングの強化

## ライセンス

このプロジェクトのライセンスについては、[LICENSE](LICENSE) ファイルを参照してください。

## 貢献

バグ報告や機能要望は GitHub Issues までお願いします。

---

**最終更新**: 2025年11月17日  
**バージョン**: 1.1  
**メンテナー**: terasaki-8910
