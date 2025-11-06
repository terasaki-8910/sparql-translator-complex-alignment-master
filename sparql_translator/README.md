# SPARQL Translator (EDOAL-based)

このプロジェクトは、EDOAL形式のアラインメントを用いてソースSPARQLクエリをターゲットSPARQLクエリへ変換する簡易バックエンドです。

## 目標
- EDOALアラインメントをパースしてエンティティ対応関係を抽出
- 対応関係を用いてSPARQLクエリを書き換え
- テストスクリプトで examples/ ディレクトリ内のクエリを一括変換して結果を出力

## 構成 (抜粋)
```
sparql_translator/
├── README.md
├── requirements.txt
├── log/
├── debug_output/
├── output/
├── src/
│   ├── mediator/
│   ├── parser/
│   └── rewriter/
├── tests/
└── examples/ (既存の examples を利用)
```

## 実行例
```
# 全クエリの変換テスト (標準モード)
python3 tests/test_conversion.py

# 詳細ログ付きで実行
python3 tests/test_conversion.py --verbose

# デバッグモード (中間結果を保存)
python3 tests/test_conversion.py --debug

# 特定のクエリのみテスト
python3 tests/test_conversion.py --query ../examples/IN1.sparql

# 詳細ログ + デバッグモード
python3 tests/test_conversion.py -v --debug
```

## 注意
- 本実装は簡易的なパーサ／リライタで、角括弧で囲まれたURI（<...>）の置換を中心に行います。
- より堅牢な変換にはSPARQLパーサやRDFlib等の利用を推奨します。

## 開発者向けメモ
- ログは `log/YYYY-MM-DD.log` に出力されます
- 中間データは `debug_output/` に保存されます
- 変換結果は `output/` に保存されます
