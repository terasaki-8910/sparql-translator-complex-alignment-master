# Dataフォルダ詳細構成と利用方法マニュアル

## 概要

本マニュアルでは、SPARQL翻訳システムEDOALアラインメントにおけるdataフォルダの詳細な構造、設定ファイルの記述ルール、利用方法、拡張方法について網羅的に解説します。

## 完全なフォルダ階層構造

```
data/
├── alignment/                              # アラインメントペアのルートディレクトリ
│   ├── agro-dbpedia/                       # エンドポイントベースのペア
│   │   ├── alignment/
│   │   │   └── alignment.edoal            # EDOALアラインメント定義ファイル
│   │   ├── alignment.json                  # ペア設定ファイル
│   │   └── queries/                        # SPARQLクエリ群（5ファイル）
│   │       ├── query_1.sparql
│   │       ├── query_2.sparql
│   │       ├── query_3.sparql
│   │       ├── query_4.sparql
│   │       └── query_5.sparql
│   │
│   ├── agronomic-voc/                      # 特殊ケース（未完）
│   │   ├── alignment/
│   │   │   └── alignment.edoal
│   │   ├── expected_outputs/               # 期待される出力クエリ（6ファイル）
│   │   │   ├── query_0.sparql 〜 query_5.sparql
│   │   └── queries/                        # 元のクエリ（6ファイル）
│   │       ├── query_0.sparql 〜 query_5.sparql
│   │
│   ├── cmt-confOf/                         # ファイルベースペアの典型例
│   │   ├── alignment/
│   │   │   └── cmt-confOf.edoal           # EDOALアラインメント
│   │   ├── alignment.json                  # ペア固有設定
│   │   ├── dataset/                        # ローカルRDFデータセット（6ファイル）
│   │   │   ├── cmt.schema.owl              # CMTオントロジー定義
│   │   │   ├── cmt_100.ttl                 # CMT実データ（100件）
│   │   │   ├── cmt_eswc.ttl                # CMT ESWC版データ
│   │   │   ├── confOf.schema.owl           # ConfOfオントロジー定義
│   │   │   ├── confOf_100.ttl              # ConfOf実データ（100件）
│   │   │   └── confOf_eswc.ttl             # ConfOf ESWC版データ
│   │   ├── queries/                        # CMT側クエリ（38ファイル）
│   │   │   ├── q_0.sparql, q_1.sparql, ..., q_39.sparql（一部欠番）
│   │   └── expected_output/                # ConfOf側変換クエリ（36ファイル）
│   │       ├── q_0.sparql, q_1.sparql, ..., q_42.sparql（一部欠番）
│   │
│   ├── cmt-conference/                     # CMT→Conferenceペア
│   │   ├── alignment/
│   │   │   └── cmt-conference.edoal
│   │   ├── alignment.json
│   │   ├── dataset/                        # CMT+Conferenceデータセット（6ファイル）
│   │   ├── queries/                        # CMTクエリ（38ファイル）
│   │   └── expected_output/                # Conference変換クエリ（71ファイル）
│   │
│   ├── cmt-edas/                          # CMT→EDASペア
│   │   ├── [同様の構造]
│   │
│   ├── cmt-ekaw/                          # CMT→EKAWペア
│   │   ├── [同様の構造]
│   │
│   ├── confOf-cmt/                        # ConfOf→CMTペア（逆方向）
│   │   ├── [同様の構造]
│   │
│   ├── confOf-conference/                 # ConfOf→Conferenceペア
│   │   ├── [同様の構造]
│   │
│   ├── confOf-edas/                       # ConfOf→EDASペア
│   │   ├── [同様の構造]
│   │
│   ├── confOf-ekaw/                       # ConfOf→EKAWペア
│   │   ├── [同様の構造]
│   │
│   ├── conference/                        # 単独Conferenceデータ
│   │   ├── alignment/
│   │   ├── queries/                        # Conferenceクエリ群
│   │   └── expected_outputs/               # 期待出力
│   │
│   ├── conference-cmt/                    # Conference→CMTペア
│   │   ├── [同様の構造]
│   │
│   ├── conference-confOf/                 # Conference→ConfOfペア
│   │   ├── [同様の構造]
│   │
│   ├── conference-edas/                   # Conference→EDASペア
│   │   ├── [同様の構造]
│   │
│   ├── conference-ekaw/                   # Conference→EKAWペア
│   │   ├── [同様の構造]
│   │
│   ├── edas-cmt/                          # EDAS→CMTペア
│   │   ├── [構造が簡略化 - expected_outputなし]
│   │
│   ├── edas-confOf/                       # EDAS→ConfOfペア
│   │   ├── [構造が簡略化 - expected_outputなし]
│   │
│   ├── edas-conference/                   # EDAS→Conferenceペア
│   │   ├── [構造が簡略化 - expected_outputなし]
│   │
│   ├── edas-ekaw/                         # EDAS→EKAWペア
│   │   ├── [構造が簡略化 - expected_outputなし]
│   │
│   ├── ekaw-cmt/                          # EKAW→CMTペア
│   │   ├── [構造が簡略化 - expected_outputなし]
│   │
│   ├── ekaw-confOf/                       # EKAW→ConfOfペア
│   │   ├── [構造が簡略化 - expected_outputなし]
│   │
│   ├── ekaw-conference/                   # EKAW→Conferenceペア
│   │   ├── [構造が簡略化 - expected_outputなし]
│   │
│   ├── ekaw-edas/                         # EKAW→EDASペア
│   │   ├── [構造が簡略化 - expected_outputなし]
│   │
│   ├── gbo-gmo/                           # GBO→GMOペア
│   │   ├── alignment/
│   │   │   └── gbo-gmo.edoal
│   │   ├── dataset/                        # GBO/GMOオントロジー（4ファイル）
│   │   │   ├── gbo.owl                     # GBOスキーマ
│   │   │   ├── gmo.owl                     # GMOスキーマ
│   │   │   ├── gboWithInstance.owl         # GBO実例付き
│   │   │   └── gmoWithInstance.owl         # GMO実例付き
│   │   └── queries/                        # GBOクエリ（20ファイル）
│   │
│   └── taxons/                            # デュアルエンドポイントペア
│       ├── alignment/
│       │   └── alignment.edoal
│       ├── alignment.json
│       ├── expected_outputs/               # DBpedia変換後クエリ
│       └── queries/                        # UniProt元クエリ
│
└── datasets/                              # 統合データセット格納場所
    ├── datasets_registry.json             # データセット統合管理ファイル
    │   # 15種類のローカルデータセット + 3つのエンドポイントを管理
    ├── cmt.schema.owl                     # CMTオントロジー定義
    ├── cmt_100.ttl                        # CMT実データ（100件）
    ├── cmt_eswc.ttl                       # CMT ESWC版データ
    ├── confOf.schema.owl                  # ConfOfオントロジー定義
    ├── confOf_100.ttl                     # ConfOf実データ（100件）
    ├── confOf_eswc.ttl                    # ConfOf ESWC版データ
    ├── conference.schema.owl              # Conferenceオントロジー定義
    ├── conference_100.ttl                 # Conference実データ（100件）
    ├── conference_eswc.ttl                # Conference ESWC版データ
    ├── edas.schema.owl                    # EDASオントロジー定義
    ├── edas_100.ttl                       # EDAS実データ（100件）
    ├── edas_eswc.ttl                      # EDAS ESWC版データ
    ├── ekaw.schema.owl                    # EKAWオントロジー定義
    ├── ekaw_100.ttl                       # EKAW実データ（100件）
    └── ekaw_eswc.ttl                      # EKAW ESWC版データ
```

## 核心的なJSON設定ファイル群

### 1. datasets_registry.json - データセット統合管理

**設計目的**: 全データセットの一元的な管理、重複の排除、パス標準化

**完全な構造**:
```json
{
  "version": "1.0",
  "created_at": "2025-11-22 18:27:23",
  "datasets": {
    "cmt.schema.owl": {
      "type": "file",
      "path": "data/datasets/cmt.schema.owl",
      "format": "xml"
    },
    "cmt_100.ttl": {
      "type": "file",
      "path": "data/datasets/cmt_100.ttl",
      "format": "turtle"
    },
    "cmt_eswc.ttl": {
      "type": "file",
      "path": "data/datasets/cmt_eswc.ttl",
      "format": "turtle"
    },
    "confOf.schema.owl": {
      "type": "file",
      "path": "data/datasets/confOf.schema.owl",
      "format": "xml"
    },
    "confOf_100.ttl": {
      "type": "file",
      "path": "data/datasets/confOf_100.ttl",
      "format": "turtle"
    },
    "confOf_eswc.ttl": {
      "type": "file",
      "path": "data/datasets/confOf_eswc.ttl",
      "format": "turtle"
    },
    "conference.schema.owl": {
      "type": "file",
      "path": "data/datasets/conference.schema.owl",
      "format": "xml"
    },
    "conference_100.ttl": {
      "type": "file",
      "path": "data/datasets/conference_100.ttl",
      "format": "turtle"
    },
    "conference_eswc.ttl": {
      "type": "file",
      "path": "data/datasets/conference_eswc.ttl",
      "format": "turtle"
    },
    "edas.schema.owl": {
      "type": "file",
      "path": "data/datasets/edas.schema.owl",
      "format": "xml"
    },
    "edas_100.ttl": {
      "type": "file",
      "path": "data/datasets/edas_100.ttl",
      "format": "turtle"
    },
    "edas_eswc.ttl": {
      "type": "file",
      "path": "data/datasets/edas_eswc.ttl",
      "format": "turtle"
    },
    "ekaw.schema.owl": {
      "type": "file",
      "path": "data/datasets/ekaw.schema.owl",
      "format": "xml"
    },
    "ekaw_100.ttl": {
      "type": "file",
      "path": "data/datasets/ekaw_100.ttl",
      "format": "turtle"
    },
    "ekaw_eswc.ttl": {
      "type": "file",
      "path": "data/datasets/ekaw_eswc.ttl",
      "format": "turtle"
    },
    "endpoint_dbpedia": {
      "type": "endpoint",
      "url": "http://dbpedia.org/sparql",
      "format": "sparql"
    },
    "endpoint_uniprot": {
      "type": "endpoint",
      "url": "https://sparql.uniprot.org/sparql",
      "format": "sparql"
    }
  }
}
```

**設計思想**:
- **DRY原則の実践**: 同一データセットの重複配置を完全に排除
- **パスの標準化**: 絶対パス指定による一貫性の確保
- **フォーマットの明確化**: turtle, xml, sparql等の形式を明確に定義
- **バージョン管理**: 作成日時とバージョン情報の体系的な管理
- **種類の明確化**: ファイルとエンドポイントを明確に区別

### 2. alignment.json - 個別ペア設定

**設計目的**: 各アラインメントペアの個別設定と実行パラメータの定義

**ファイルベースペアの完全な例**:
```json
{
  "name": "cmt-confOf",
  "alignment_file": "data/alignment/cmt-confOf/alignment/cmt-confOf.edoal",
  "queries_dir": "data/alignment/cmt-confOf/queries/",
  "expected_output_dir": "data/alignment/cmt-confOf/expected_output/",
  "datasets": [
    {
      "type": "file",
      "path": "data/datasets/cmt_100.ttl",
      "format": "turtle"
    },
    {
      "type": "file",
      "path": "data/datasets/cmt_eswc.ttl",
      "format": "turtle"
    },
    {
      "type": "file",
      "path": "data/datasets/confOf_100.ttl",
      "format": "turtle"
    },
    {
      "type": "file",
      "path": "data/datasets/confOf_eswc.ttl",
      "format": "turtle"
    },
    {
      "type": "file",
      "path": "data/datasets/cmt.schema.owl",
      "format": "xml"
    },
    {
      "type": "file",
      "path": "data/datasets/confOf.schema.owl",
      "format": "xml"
    }
  ],
  "endpoints": {}
}
```

**エンドポイントベースペアの例**:
```json
{
  "name": "agro-dbpedia",
  "alignment_file": "data/alignment/agro-dbpedia/alignment/alignment.edoal",
  "queries_dir": "data/alignment/agro-dbpedia/queries/",
  "expected_output_dir": "",
  "datasets": [],
  "endpoints": {
    "dbpedia": "http://dbpedia.org/sparql"
  }
}
```

**設定フィールドの詳細**:
- `name`: ペアの一意な識別子
- `alignment_file`: EDOALアラインメントファイルへの絶対パス
- `queries_dir`: ソースクエリ格納ディレクトリへのパス
- `expected_output_dir`: 変換後期待クエリ格納ディレクトリへのパス（空の場合もあり）
- `datasets`: 使用するデータセットの配列
- `endpoints`: 使用するSPARQLエンドポイントのオブジェクト

## EDOALアラインメントファイルの詳細

### 基本的な構成要素

EDOAL (Expressive and Declarative Ontology Alignment Language) は、オントロジー間のセマンティックマッピングを表現するためのXMLベースの高レベル言語。

**XMLヘッダー構造**:
```xml
<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<!DOCTYPE rdf:RDF [
<!ENTITY xsd "http://www.w3.org/2001/XMLSchema#">
<!ENTITY cmt "http://cmt#">
<!ENTITY confOf "http://confOf#">
<!ENTITY proton "http://proton.semanticweb.org/">
<!ENTITY edoal "http://ns.inria.org/edoal/1.0/#">
]>
```

**アラインメントのメタデータ**:
```xml
<rdf:RDF xmlns="http://knowledgeweb.semanticweb.org/heterogeneity/alignment#"
  xml:base="http://cmt-confof/alignment/"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
  xmlns:align="http://knowledgeweb.semanticweb.org/heterogeneity/alignment#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:cmt="http://cmt#"
  xmlns:confOf="http://confOf#"
  xmlns:proton="http://proton.semanticweb.org/"
  xmlns:edoal="http://ns.inria.org/edoal/1.0/#">

  <Alignment rdf:about="http://cmt-confof/alignment/">
    <xml>yes</xml>
    <dc:creator>http://www.irit.fr/recherches/MELODI/ontologies/contributors#thieblin</dc:creator>
    <dc:date>2017/07/11</dc:date>
    <method>manual</method>
    <purpose>matcher-evaluation</purpose>
    <level>2EDOAL</level>
    <type>**</type>
```

**オントロジー定義セクション**:
```xml
    <onto1>
      <Ontology rdf:about="&cmt;">
        <formalism>
          <Formalism align:uri="http://www.w3.org/TR/owl-guide/" align:name="owl" />
        </formalism>
      </Ontology>
    </onto1>
    <onto2>
      <Ontology rdf:about="&confOf;">
        <formalism>
          <Formalism align:uri="http://www.w3.org/TR/owl-guide/" align:name="owl" />
        </formalism>
      </Ontology>
    </onto2>
```

**エンドポイントベースの場合**:
```xml
    <onto2>
      <Ontology rdf:about="&dbo;">
        <location>http://dbpedia.org</location>  <!-- 実際のエンドポイントURL -->
        <formalism>
          <Formalism align:uri="http://www.w3.org/TR/owl-guide/" align:name="owl" />
        </formalism>
      </Ontology>
    </onto2>
```

### マッピングルールの分類と具体例

**1. 単純クラス間マッピング**:
```xml
    <map>
      <Cell rdf:about="ProgramCommitteeChair">
        <entity1>
          <edoal:Class rdf:about="&cmt;ProgramCommitteeChair" />
        </entity1>
        <entity2>
          <edoal:Class rdf:about="&confOf;ConferenceChair" />
        </entity2>
        <relation>≡</relation>
        <measure>1.0</measure>
      </Cell>
    </map>
```

**2. 単純プロパティ間マッピング**:
```xml
    <map>
      <Cell rdf:about="acceptPaper">
        <entity1>
          <edoal:Property rdf:about="&cmt;acceptPaper" />
        </entity1>
        <entity2>
          <edoal:Property rdf:about="&confOf;hasAcceptedPaper" />
        </entity2>
        <relation>≡</relation>
        <measure>1.0</measure>
      </Cell>
    </map>
```

**3. EDOALの強力な複合マッピング**:
```xml
    <map>
      <Cell rdf:about="ComplexMapping1">
        <entity1>
          <edoal:ComplexTransformation>
            <edoal:operator>
              <edoal:And>
                <edoal:leftOperand>
                  <edoal:Class rdf:about="&cmt;Paper" />
                </edoal:leftOperand>
                <edoal:rightOperand>
                  <edoal:PropertyRestriction>
                    <edoal:onProperty rdf:about="&cmt;hasDecision" />
                    <edoal:someValuesFrom rdf:resource="&cmt;Accept" />
                  </edoal:PropertyRestriction>
                </edoal:rightOperand>
              </edoal:And>
            </edoal:operator>
          </edoal:ComplexTransformation>
        </entity1>
        <entity2>
          <edoal:Class rdf:about="&confOf;AcceptedPaper" />
        </entity2>
        <relation>≡</relation>
        <measure>1.0</measure>
      </Cell>
    </map>
```

**4. インスタンス変換マッピング**:
```xml
    <map>
      <Cell rdf:about="InstanceTransform">
        <entity1>
          <edoal:InstanceTransformation>
            <edoal:expression>
              <edoal:Concat>
                <edoal:argument rdf:datatype="&xsd;string">PREFIX_</edoal:argument>
                <edoal:argument rdf:about="&cmt;id" />
              </edoal:Concat>
            </edoal:expression>
          </edoal:InstanceTransformation>
        </entity1>
        <entity2>
          <edoal:Property rdf:about="&confOf;identifier" />
        </entity2>
      </Cell>
    </map>
```

## SPARQLクエリファイルの構造と規約

### 命名規約の詳細

- **基本パターン**: `q_[連番].sparql` または `query_[連番].sparql`
- **連番**: 基本的に0から始まる連続番号（ただし欠番が多数存在）
- **拡張子**: 必ず `.sparql` を使用
- **特殊ケース**: `taxons`ペアでは `query_` 接頭辞を使用

### クエリ構造の実例

**1. シンプルなタイプ検索クエリ（CMT）**:
```sparql
SELECT distinct ?s WHERE {
  ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://cmt#ProgramCommittee> .
}
```

**2. UNIONを使用した複雑な変換クエリ（ConfOf→EDAS）**:
```sparql
SELECT distinct ?s ?o WHERE {
{
  ?s <http://edas#endDate> ?o .
}
union{
  ?s <http://edas#hasEndDateTime> ?o .
}
}
```

**3. エンドポイント向けのプレフィックス付きクエリ**:
```sparql
PREFIX agro: <http://ontology.irstea.fr/agronomictaxon/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX agronto: <http://aims.fao.org/aos/agrontology#>
PREFIX agrovoc: <http://aims.fao.org/aos/agrovoc/>
PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>

select ?rank where {
  ?taxon agro:prefScientificName ?label.
  ?taxon a ?rank.
  ?rank rdfs:subClassOf agro:Taxon.
  filter (regex(?label, "^triticum$","i")).
}
```

### SPARQLクエリ変換プロセスの詳細

1. **構文解析フェーズ**: JavaベースのSPARQL ASTパーサがクエリを抽象構文木に変換
2. **マッピング適用フェーズ**: EDOALルールに基づきASTノードを変換
3. **クエリ再構築フェーズ**: 変換されたASTから有効なSPARQLクエリを生成
4. **最適化フェーズ**: 対象エンドポイントに応じたクエリ最適化
5. **実行フェーズ**: 対象データセットまたはエンドポイントでのクエリ実行

## データセットの分類と詳細

### データの種類と特徴

**1. オントロジースキーマファイル**:
- **命名規則**: `[prefix].schema.owl`
- **形式**: OWL/XML
- **内容**: クラス、プロパティ、制約、公理の定義
- **例**: `cmt.schema.owl`, `confOf.schema.owl`

**2. 実データファイル**:
- **命名規則**:
  - `[prefix]_100.ttl`: 100件程度の小規模サンプルデータ
  - `[prefix]_eswc.ttl`: ESWC（Extended Semantic Web Conference）標準データ
- **形式**: Turtle（.ttl）
- **内容**: 実際のインスタンスデータと個体
- **例**: `cmt_100.ttl`, `cmt_eswc.ttl`

**3. SPARQLエンドポイント**:
- **DBpedia**: `http://dbpedia.org/sparql` - 一般知識データベース
- **UniProt**: `https://sparql.uniprot.org/sparql` - タンパク質情報データベース

### RDFデータ形式の具体例

**Turtle形式の例**:
```turtle
@prefix :      <http://cmt#> .
@prefix xsp:   <http://www.owl-ontologies.com/2005/08/07/xsp.owl#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix swrl:  <http://www.w3.org/2003/11/swrl#> .
@prefix protege: <http://protege.stanford.edu/plugins/owl/protege#> .
@prefix swrlb: <http://www.w3.org/2003/11/swrlb#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .

<http://cmt>  a  owl:Ontology .

xsd:date  a     rdfs:Datatype .

:acceptPaper  a        owl:ObjectProperty , owl:InverseFunctionalProperty ;
        rdfs:domain    :Administrator ;
        rdfs:range     :Paper ;
        owl:inverseOf  :acceptedBy .

:acceptedBy  a       owl:ObjectProperty , owl:FunctionalProperty ;
        rdfs:domain    :Paper ;
        rdfs:range     :Administrator .
```

## 新規データセット追加の詳細手順

### 1. データセットファイルの準備と配置

**基本手順**:
1. **RDFデータの準備**: 標準的なRDF形式（Turtle推奨、XMLも可）
2. **適切な命名**: 既存の命名規約に従ったファイル名
3. **配置**: `data/datasets/` ディレクトリへの配置
4. **フォーマット確認**: ファイル形式の正確な特定

**具体的な命名例**:
- `newontology.schema.owl` - 新オントロジーのスキーマ定義
- `newontology_100.ttl` - 新オントロジーのサンプルデータ（100件程度）
- `newontology_eswc.ttl` - 新オントロジーのESWC標準形式データ

### 2. datasets_registry.jsonの更新手順

**新規エントリの追加**:
```json
{
  "datasets": {
    "newontology.schema.owl": {
      "type": "file",
      "path": "data/datasets/newontology.schema.owl",
      "format": "xml"
    },
    "newontology_100.ttl": {
      "type": "file",
      "path": "data/datasets/newontology_100.ttl",
      "format": "turtle"
    },
    "newontology_eswc.ttl": {
      "type": "file",
      "path": "data/datasets/newontology_eswc.ttl",
      "format": "turtle"
    }
  }
}
```

**重要な注意点**:
- 既存のエントリを削除しないこと
- パスの正確性を二重確認すること
- フォーマット指定（turtle/xml）を正確に記述すること

### 3. 環境設定の再実行と検証

```bash
# 環境設定の強制再実行
python3 setup_env.py --force

# 設定の正確性検証
cat data/datasets/datasets_registry.json | jq .
```

## 新規アラインメントペア追加の詳細手順

### 1. ディレクトリ構造の作成

**基本的なディレクトリ作成**:
```bash
# ペア名を "source-target" とした場合
mkdir -p data/alignment/source-target/{alignment,queries,expected_output,dataset}
```

**結果のディレクトリ構造**:
```
data/alignment/source-target/
├── alignment/
├── queries/
├── expected_output/
└── dataset/
```

### 2. EDOALアラインメントファイルの作成

**ファイルパス**: `data/alignment/source-target/alignment/source-target.edoal`

**必須要素**:
- ソースオントロジーの完全な定義
- ターゲットオントロジーの完全な定義
- セマンティックマッピングルール
- メタ情報（作成者、作成日、目的、手法）

**基本テンプレート**:
```xml
<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<!DOCTYPE rdf:RDF [
<!ENTITY xsd "http://www.w3.org/2001/XMLSchema#">
<!ENTITY source "http://source#">
<!ENTITY target "http://target#">
<!ENTITY edoal "http://ns.inria.org/edoal/1.0/#">
]>

<rdf:RDF xmlns="http://knowledgeweb.semanticweb.org/heterogeneity/alignment#"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:align="http://knowledgeweb.semanticweb.org/heterogeneity/alignment#"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:source="http://source#"
  xmlns:target="http://target#"
  xmlns:edoal="http://ns.inria.org/edoal/1.0/#">

  <Alignment rdf:about="http://source-target/alignment/">
    <xml>yes</xml>
    <dc:creator>あなたの名前</dc:creator>
    <dc:date>2025-11-23</dc:date>
    <method>manual</method>
    <purpose>query-rewriting</purpose>
    <level>2EDOAL</level>
    <type>**</type>

    <onto1>
      <Ontology rdf:about="&source;">
        <formalism>
          <Formalism align:uri="http://www.w3.org/TR/owl-guide/" align:name="owl" />
        </formalism>
      </Ontology>
    </onto1>

    <onto2>
      <Ontology rdf:about="&target;">
        <formalism>
          <Formalism align:uri="http://www.w3.org/TR/owl-guide/" align:name="owl" />
        </formalism>
      </Ontology>
    </onto2>

    <!-- マッピングルールをここに記述 -->

  </Alignment>
</rdf:RDF>
```

### 3. alignment.json設定ファイルの作成

**ファイルパス**: `data/alignment/source-target/alignment.json`

**完全な設定例**:
```json
{
  "name": "source-target",
  "alignment_file": "data/alignment/source-target/alignment/source-target.edoal",
  "queries_dir": "data/alignment/source-target/queries/",
  "expected_output_dir": "data/alignment/source-target/expected_output/",
  "datasets": [
    {
      "type": "file",
      "path": "data/datasets/source_100.ttl",
      "format": "turtle"
    },
    {
      "type": "file",
      "path": "data/datasets/source_eswc.ttl",
      "format": "turtle"
    },
    {
      "type": "file",
      "path": "data/datasets/target_100.ttl",
      "format": "turtle"
    },
    {
      "type": "file",
      "path": "data/datasets/target_eswc.ttl",
      "format": "turtle"
    },
    {
      "type": "file",
      "path": "data/datasets/source.schema.owl",
      "format": "xml"
    },
    {
      "type": "file",
      "path": "data/datasets/target.schema.owl",
      "format": "xml"
    }
  ],
  "endpoints": {}
}
```

### 4. alignment_pairs_summary.mdへの登録

**登録形式の例**:
```markdown
- **ペアXX: source-target**
  - alignment: `data/alignment/source-target/alignment/source-target.edoal`
  - dataset:
    - `data/datasets/source_100.ttl` (data_100)
    - `data/datasets/source_eswc.ttl` (eswc)
    - `data/datasets/target_100.ttl` (data_100)
    - `data/datasets/target_eswc.ttl` (eswc)
    - `data/datasets/source.schema.owl` (schema)
    - `data/datasets/target.schema.owl` (schema)
  - queries: `data/alignment/source-target/queries/` (sourceのクエリ XX個)
  - expected_output: `data/alignment/source-target/expected_output/` (targetのクエリ XX個)
```

### 5. SPARQLクエリの準備

**queries/ディレクトリの内容**:
- ソースオントロジーに対するテストクエリ
- 命名規則: `q_0.sparql`, `q_1.sparql`, `q_2.sparql`, ...
- 数の目安: 10-50クエリ程度

**expected_output/ディレクトリの内容**:
- ターゲットオントロジーで記述された期待出力クエリ
- EDOAL変換後の正しいクエリ形式
- ソースクエリと対応する番号付け

### 6. 環境設定の再実行と動作確認

```bash
# 環境設定の再実行
python3 setup_env.py --force

# 新ペアのテスト実行
python3 main.py --pair source-target --dry-run

# 個別クエリのテスト（必要に応じて）
python3 main.py --pair source-target --query q_0
```

## JSON設定ルールと設計哲学の詳細

### 基本設計原則

**1. DRY (Don't Repeat Yourself) の徹底**:
- データセット重複の完全排除
- 一元管理による保守性と一貫性の向上
- 設定の再利用性最大化

**2. 高い柔軟性の確保**:
- ファイルベースとエンドポイントベースの両対応
- ハイブリッド構成の完全サポート
- 特殊ケースへの柔軟な対応

**3. 透明性の確保**:
- 明示的で一貫したパス指定
- ファイル形式の明確な定義
- バージョン情報と変更履歴の保持

**4. 拡張性の重視**:
- 新規データセットの容易な追加
- 新規アラインメントペアの標準化された手順
- スケーラビリティの確保

### 階層的な設定構造

```
alignment_pairs_summary.md（マスター定義ファイル）
    ↓ [setup_env.pyによる自動生成]
datasets_registry.json（データセットの一元管理）
    ↓ [各ペア設定の基礎として利用]
各ペアのalignment.json（個別設定ファイル）
    ↓ [システム実行時の参照]
実行時パラメータとデータパスの解決
```

### 特殊ケースへの対応戦略

**1. エンドポイント専用ペアの処理**:
- `agro-dbpedia`: agro → dbpedia（単一エンドポイント）
- `taxons`: uniprot → dbpedia（デュアルエンドポイント）
- `datasets`配列は空配列に設定
- `endpoints`オブジェクトにエンドポイントURLを記述

**2. ハイブリッドペアの処理**:
- ローカルデータセット + リモートエンドポイントの組み合わせ
- `datasets`と`endpoints`の両方を適切に設定
- 複合的なデータソースへの対応

**3. 不完全なペアの処理**:
- `agronomic-voc`: expected_outputのみ存在
- `conference`: expected_outputが欠落
- `edas-*`, `ekaw-*`シリーズ: expected_outputの省略
- 柔軟な構成で例外ケースに対応

## トラブルシューティングとデバッギング

### 一般的な問題と解決策

**1. パス解決エラー**:
```bash
# 症状: File not found エラー
# 原因: 相対パスと絶対パスの混在、ファイルの存在確認
# 解決策:
ls -la data/alignment/[pair]/alignment/[file].edoal
cat data/datasets/datasets_registry.json | jq '.datasets.cmt_100.ttl.path'
```

**2. JSONフォーマットの不一致**:
```bash
# 症状: JSONパースエラー
# 原因: シンタックスエラー、型の不一致
# 解決策:
python3 -m json.tool data/alignment/[pair]/alignment.json
jq . data/datasets/datasets_registry.json
```

**3. EDOALパースエラー**:
```bash
# 症状: XMLパースエラー、エンティティ参照エラー
# 原因: 名前空間宣言の欠落、エンティティ定義の不一致
# 解決策:
xmllint --noout data/alignment/[pair]/alignment/[file].edoal
```

**4. SPARQLクエリ実行エラー**:
```bash
# 症状: クエリ実行エラー、エンドポイント接続エラー
# 原因: プレフィックス宣言の欠落、無効なURI
# 解決策:
# クエリのシンタックスチェック
# エンドポイントの接続確認
python3 main.py --test
```

### 系統的なデバッグ方法

**1. 設定ファイルの検証**:
```bash
# データセット登録の確認
cat data/datasets/datasets_registry.json | jq '.datasets | keys[]'

# 個別ペア設定の確認
cat data/alignment/cmt-confOf/alignment.json | jq .

# パスの存在確認
find data -name "*.edoal" | sort
find data -name "*.sparql" | wc -l
```

**2. システムの接続テスト**:
```bash
# エンドポイント接続確認
python3 main.py --test

# 特定ペアのドライラン
python3 main.py --pair cmt-confOf --dry-run

# 詳細なログ出力
python3 main.py --pair cmt-confOf --verbose
```

## ベストプラクティスと推奨事項

### 1. 命名規則の一貫性
- **小文字使用**: 全てのファイル名は小文字で統一
- **ハイフン区切り**: 単語の区切りにはハイフンを使用
- **意味のある名前**: 内容が推測できる意味のある命名
- **一貫した接頭辞**: 同じオントロジーには同じ接頭辞を使用

### 2. 包括的なドキュメンテーション
- **EDOALファイル**: コメントによるマッピングの説明
- **メタ情報**: 作成者、作成日、目的、手法の明記
- **変更履歴**: バージョンごとの変更点の記録
- **技術的決定**: 設計判断の理由の文書化

### 3. 系統的なバージョン管理
- **datasets_registry.json**: バージョン情報と更新日時
- **アラインメントファイル**: 作成日と更新日の管理
- **クエリファイル**: 変更履歴とバージョン管理
- **設定ファイル**: 変更点の追跡と記録

### 4. 品質保証の手法
- **SPARQLクエリ**: 構文チェックと意味的妥当性の検証
- **EDOALマッピング**: 論理的な正しさと完全性の確認
- **期待出力比較**: 実際の出力との一致検証
- **包括的テスト**: 全ペア、全クエリの網羅的テスト

## まとめと今後の展望

本システムは高度にモジュール化され、スケーラブルなアーキテクチャを採用しており、dataフォルダはその中核的な役割を担っています。適切な設定ファイル管理と標準化された手順に従うことで、新規データセットやアラインメントペアの追加が容易かつ体系的に行えます。

設計哲学の核心は**一元管理**、**柔軟性**、**透明性**の3原則にあり、これにより大規模なオントロジーマッピングプロジェクトの効率的な運用と保守が可能となっています。今後の拡張においても、この基本的な設計原則を維持しながら、さらに高度な機能の追加が期待されます。