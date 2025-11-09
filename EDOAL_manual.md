

# **EDOAL 1.0: 厳密な技術仕様書**

## **1\. 序論と名前空間**

### **1.1. EDOALの目的と位置づけ**

EDOAL (Expressive and Declarative Ontology Alignment Language) は、オントロジー間の対応関係 (Correspondence) を表現するための、表現力豊かで宣言的な語彙を提供する言語です 1。これは、INRIA Alignment API 1.0 の標準アライメントフォーマットを拡張するものです 2。

EDOALの主な目的は、単純な等価関係 ($owl:sameAs$) やサブサンプション ($rdfs:subClassOf$) では表現できない、より複雑な対応関係を記述することです 1。これには、構造的な不一致（例：一方のプロパティが、もう一方のクラスと関係の連鎖に相当する）や、データ型レベルでの変換（例：単位変換、文字列操作）を伴う対応関係が含まれます 1。

本仕様書は、EDOAL 1.0 の構文とセマンティクスを、後続のパーサーやトランスレーター実装のために厳密に定義します。

### **1.2. 準拠する標準**

本仕様は、以下の権威ある情報源に厳密に基づいています。

1. **EDOAL 1.0 公式仕様:** https://ns.inria.fr/edoal/1.0/ 1。  
2. **主要な技術レポート:** "D2.2.10: Expressive alignment language and implementation" (Euzenat, Scharffe, Zimmermann) 5。  
3. **基盤となる標準:** W3C RDF 3 および Alignment API 1.0 7。

本仕様書は、これらの情報源から導出不可能な一切の推測や曖昧な解釈を排除します。

### **1.3. 名前空間の定義**

本仕様書およびコード例で使用されるXML名前空間プレフィックスは、以下の通りに定義されます。

* rdf:: http://www.w3.org/1999/02/22-rdf-syntax-ns\#  
* owl:: http://www.w3.org/2002/07/owl\#  
* xsd:: http://www.w3.org/2001/XMLSchema\#  
* align:: http://knowledgeweb.semanticweb.org/heterogeneity/alignment\# (Alignment API 1.0 標準フォーマット)  
* edoal:: http://ns.inria.org/edoal/1.0/\# (EDOAL 拡張)

## **2\. Alignment API 基礎構造 (Base Structure)**

EDOALは、Alignment API の基本構造を拡張します。したがって、EDOAL文書はまず align:Alignment および align:Cell の定義に従う必要があります 1。

### **2.1. align:Alignment**

align:Alignment は、EDOALアライメント文書のルート要素です。これは、アライメント全体をカプセル化するコンテナとして機能します。

* **align:onto1**: ソースオントロジーのURIを指定する要素。  
* **align:onto2**: ターゲットオントロジーのURIを指定する要素。  
* **align:map**: 0個以上の align:Cell を含むコンテナ。  
* **align:level**: アライメントの表現レベルを示します。EDOALを使用する場合、2EDOAL と記述されることが推奨されます。

### **2.2. align:Cell**

align:Cell は、2つのエンティティ間の単一の対応関係を定義する中心的な要素です 1。EDOALの表現力は、この Cell の内部、特に entity1 と entity2 の内部で発揮されます。

* **align:entity1**: ソースオントロジー（onto1）のエンティティを記述します。単純なURIまたは複雑なEDOALエンティティ式（セクション 3-6）のいずれかをとります。  
* **align:entity2**: ターゲットオントロジー（onto2）のエンティティを記述します。entity1 と同様に、単純なURIまたは複雑なEDOALエンティティ式をとります。  
* **align:relation**: 2つのエンティティ間の関係のセマンティクスを示す記号です（例: \=, \<, \>, %）。  
* **align:measure**: この対応関係の信頼度を示す尺度で、通常は xsd:float 型の $0.0$ から $1.0$ の値をとります 7。

#### **記述例 (基礎構造スケルトン)**

XML

\<rdf:RDF   
    xmlns:rdf\="http://www.w3.org/1999/02/22-rdf-syntax-ns\#"  
    xmlns:align\="http://knowledgeweb.semanticweb.org/heterogeneity/alignment\#"  
    xmlns:edoal\="http://ns.inria.org/edoal/1.0/\#"  
    xmlns\="http://knowledgeweb.semanticweb.org/heterogeneity/alignment\#"\>

  \<Alignment\>  
    \<xml\>yes\</xml\>  
    \<level\>2EDOAL\</level\>  
    \<onto1\>  
      \<Ontology rdf:about\="http://source.ontology/example"/\>  
    \</onto1\>  
    \<onto2\>  
      \<Ontology rdf:about\="http://target.ontology/example"/\>  
    \</onto2\>  
      
    \<map\>  
      \<Cell rdf:about\="\#cell-example-1"\>  
        \<entity1\>  
          \</entity1\>  
        \<entity2\>  
          \</entity2\>  
        \<relation\>\=\</relation\>  
        \<measure rdf:datatype\="\&xsd;float"\>1.0\</measure\>  
      \</Cell\>  
    \</map\>  
  \</Alignment\>  
\</rdf:RDF\>

## **3\. 【コア仕様】エンティティ表現 (Entity Expressions)**

EDOALは、アライメントの対象となるエンティティを4つのカテゴリに分類します：Class, Property, Relation, Instance 1。これらの各エンティティは、URIによって直接識別されるか、またはコンストラクタ（セクション 4-6）によってその場で構築されます。

### **3.1. クラス (edoal:Class)**

オントロジーのクラス（$owl:Class$ に相当）を表現します 1。

#### **3.1.1. 識別されるクラス (Identified Class)**

URIによって一意に識別されるクラスをrdf:about属性で指定します。

* **構文:** \<edoal:Class rdf:about=""/\> 1  
* **記述例:** 1  
  XML  
  \<entity1\>  
    \<edoal:Class rdf:about\="\&ekaw;Accepted\_Paper"/\>  
  \</entity1\>

#### **3.1.2. 構築されるクラス (Class Construction)**

論理コンストラクタ（セクション 4）または制約（セクション 6）を用いて匿名クラスを構築します。

* **構文:** \<edoal:Class\> \[コンストラクタまたは制約\] \</edoal:Class\> 1  
* **記述例 (論理和):** 1  
  XML  
  \<entity1\>  
    \<edoal:Class\>  
      \<edoal:or rdf:parseType\="Collection"\>  
        \<edoal:Class rdf:about\="\&vin;Acidite" /\>  
        \<edoal:Class rdf:about\="\&vin;Astreingence" /\>  
      \</edoal:or\>  
    \</edoal:Class\>  
  \</entity1\>

### **3.2. プロパティ (edoal:Property)**

オントロジーのデータ型プロパティ（$owl:DatatypeProperty$ に相当）を表現します 1。

#### **3.2.1. 識別されるプロパティ (Identified Property)**

URIによって一意に識別されるプロパティをrdf:about属性で指定します。

* **構文:** \<edoal:Property rdf:about=""/\> 1  
* **記述例:** 1  
  XML  
  \<entity1\>  
    \<edoal:Property rdf:about\="\&wine;hasVintageYear" /\>  
  \</entity1\>

#### **3.2.2. 構築されるプロパティ (Property Construction)**

論理コンストラクタ（セクション 4）またはパスコンストラクタ（セクション 5.1）を用いて構築されます。

* **構文:** \<edoal:Property\> \[コンストラクタ\] \</edoal:Property\>  
* **記述例 (パス合成):** 1  
  XML  
  \<edoal:Property\>  
    \<edoal:compose rdf:parseType\="Collection"\>  
      \<edoal:Relation rdf:about\="\&gbo;hasEndDate" /\>  
      \<edoal:Property rdf:about\="\&time;inXSDDate" /\>  
    \</edoal:compose\>  
  \</edoal:Property\>

### **3.3. 関係 (edoal:Relation)**

オントロジーのオブジェクトプロパティ（$owl:ObjectProperty$ に相当）を表現します 1。

#### **3.3.1. 識別される関係 (Identified Relation)**

URIによって一意に識別される関係をrdf:about属性で指定します。

* **構文:** \<edoal:Relation rdf:about=""/\> 8  
* **記述例:** 8  
  XML  
  \<entity1\>  
    \<edoal:Relation rdf:about\="\&ekaw;authorOf"/\>  
  \</entity1\>

#### **3.3.2. 構築される関係 (Relation Construction)**

論理コンストラクタ（セクション 4）またはパスコンストラクタ（セクション 5.2）を用いて構築されます。

* **構文:** \[コンストラクタ\] (注：edoal:Relation タグで囲まない場合があります)  
* **記述例 (逆関係):** 8  
  XML  
  \<entity2\>  
    \<edoal:inverse\>  
      \<edoal:Relation rdf:about\="\&cmt;hasAuthor"/\>  
    \</edoal:inverse\>  
  \</entity2\>

### **3.4. インスタンス (edoal:Instance)**

オントロジーの個体（$owl:Individual$ に相当）を表現します 1。

#### **3.4.1. 識別されるインスタンス (Identified Instance)**

URIによって一意に識別されるインスタンスをrdf:about属性で指定します。

* **構文:** \<edoal:Instance rdf:about=""/\> 1  
* **記述例:** 1  
  XML  
  \<entity1\>  
    \<edoal:Instance rdf:about\="\&vin;Bordelais" /\>  
  \</entity1\>

## **4\. 【コア仕様】論理コンストラクタ (Logical Constructors)**

EDOALは、クラス、プロパティ、関係の各エンティティ式を構築するために、3つのブール演算子を提供します。これらはOWLにおけるクラスコンストラクタと類似のセマンティクスを持ちます 1。

### **4.1. edoal:and (論理積 / Intersection)**

複数のエンティティ式の論理積（積集合）を表します 1。

* **引数:** rdf:parseType="Collection" 内に、0個以上のエンティティ式をとります。  
* **セマンティクス (引数なし):** 引数が0個の場合 (\<edoal:and rdf:parseType="Collection"/\>)、その式は $owl:Thing$（トップ概念）と同等と解釈されます 1。  
* **記述例 (クラスの論理積):** 1  
  XML  
  \<edoal:Class\>  
    \<edoal:and rdf:parseType\="Collection"\>  
      \<edoal:Class rdf:about\="\&cmt;Paper"/\>  
      \<edoal:AttributeDomainRestriction\>  
        \<edoal:onAttribute\>  
          \<edoal:Relation rdf:about\="\&cmt;hasDecision"/\>  
        \</edoal:onAttribute\>  
        \<edoal:class\>  
          \<edoal:Class rdf:about\="\&cmt;Acceptance"/\>  
        \</edoal:class\>  
      \</edoal:AttributeDomainRestriction\>  
    \</edoal:and\>  
  \</edoal:Class\>

### **4.2. edoal:or (論理和 / Union)**

複数のエンティティ式の論理和（和集合）を表します 1。

* **引数:** rdf:parseType="Collection" 内に、0個以上のエンティティ式をとります。  
* **セマンティクス (引数なし):** 引数が0個の場合 (\<edoal:or rdf:parseType="Collection"/\>)、その式は $owl:Nothing$（ボトム概念）と同等と解釈されます 1。  
* **記述例 (クラスの論理和):** 1  
  XML  
  \<edoal:Class\>  
    \<edoal:or rdf:parseType\="Collection"\>  
      \<edoal:Class rdf:about\="\&ekaw;Demo\_Chair"/\>  
      \<edoal:Class rdf:about\="\&ekaw;Poster\_Chair"/\>  
      \<edoal:Class rdf:about\="\&ekaw;Tutorial\_Chair"/\>  
    \</edoal:or\>  
  \</edoal:Class\>

### **4.3. edoal:not (論理否定 / Negation)**

単一のエンティティ式の論理否定（補集合）を表します 1。

* **引数:** 1個のエンティティ式をとります。  
* **記述例 (クラスの否定):** 1  
  XML  
  \<edoal:Class\>  
    \<edoal:not\>  
      \<edoal:Class rdf:about\="\&vin;RedWine" /\>  
    \</edoal:not\>  
  \</edoal:Class\>

## **5\. 【コア仕様】パスコンストラクタ (Path Constructors)**

プロパティ式 ($edoal:Property$) および関係式 ($edoal:Relation$) に特有のコンストラクタであり、オントロジー間の構造的異質性を吸収するために使用されます。

### **5.1. edoal:compose (合成 / Composition)**

複数のプロパティまたは関係を連鎖させ、単一のパス式を構築します 1。

* **引数:** rdf:parseType="Collection" 内に、2個以上のプロパティ式または関係式を順序付きでとります。  
* **セマンティクス:** $P1 \\circ P2$（プロパティの連鎖）のセマンティクスを持ちます。  
* **構造的ブリッジ:** edoal:compose は、関係 ($edoal:Relation$) とプロパティ ($edoal:Property$) を混合して連鎖させることができます。これにより、関係の終端にあるノードのデータ型プロパティ値を抽出するような、複雑なパス式を定義できます 8。  
* **記述例 (Relation と Property の合成):** 1  
  XML  
  \<edoal:Property\>  
    \<edoal:compose rdf:parseType\="Collection"\>  
      \<edoal:Relation rdf:about\="\&gbo;hasEndDate" /\>   
      \<edoal:Property rdf:about\="\&time;inXSDDate" /\>  
    \</edoal:compose\>  
  \</edoal:Property\>

### **5.2. edoal:inverse (逆 / Inverse)**

単一の関係 ($edoal:Relation$) の逆関係（$owl:inverseOf$ に相当）を表現します 8。

* **引数:** 1個の $edoal:Relation$ 式をとります。  
* **記述例:** 8  
  XML  
  \<entity2\>  
    \<edoal:inverse\>  
      \<edoal:Relation rdf:about\="\&cmt;hasAuthor"/\>  
    \</edoal:inverse\>  
  \</entity2\>

### **5.3. その他のコンストラクタ (仕様範囲外)**

技術レポート（D2.2.10など）では、symmetric, transitive, reflexive 閉包などの抽象構文が議論されていますが 5、EDOAL 1.0 の公式XML仕様 (ns.inria.fr/edoal/1.0/) および参照アライメントファイルにはこれらの具象構文は定義されていません。したがって、本仕様書ではこれらを EDOAL 1.0 の標準構文として定義しません。

## **6\. 【コア仕様】制約 (Restrictions)**

制約 (Restriction) は、エンティティ式（主に $edoal:Class$）を、その属性や関係に基づいて限定的に定義するための構文です。これらはOWLにおける量化制限やカーディナリティ制限に類似した機能を提供します 1。

### **6.1. 共通の制約要素**

制約構文は、以下の共通の子要素を使用して定義されます 1。

#### **6.1.1. edoal:onAttribute**

制約の対象となる属性（$edoal:Property$ または $edoal:Relation$ の式）を指定します。

* **記述例:** 1  
  XML  
  \<edoal:onAttribute\>  
    \<edoal:Property rdf:about\="\&vin;hasVintageYear" /\>  
  \</edoal:onAttribute\>

#### **6.1.2. edoal:comparator**

AttributeValueRestriction および AttributeOccurenceRestriction で使用され、値またはカーディナリティの比較演算子（述語）のURIを指定します。

* **記述例:** 1  
  XML  
  \<edoal:comparator rdf:resource\="\&edoal;equals" /\>

#### **6.1.3. edoal:value**

AttributeValueRestriction および AttributeOccurenceRestriction で使用され、比較対象となる値（リテラルまたはインスタンス）を指定します。

* **記述例 (リテラル):** 1  
  XML  
  \<edoal:value\>  
    \<edoal:Literal edoal:type\="\&xsd;integer" edoal:string\="1" /\>  
  \</edoal:value\>

### **6.2. 制約の種類**

EDOAL 1.0 は、主に4種類の属性制約と2種類の関係制約を定義します。

#### **6.2.1. edoal:AttributeValueRestriction (属性値制約)**

属性の値を特定の値に制約します（$owl:hasValue$ に類似）。onAttribute, comparator, value を使用します 1。

* **記述例:** 1  
  XML  
  \<edoal:AttributeValueRestriction\>  
    \<edoal:onAttribute\>  
      \<edoal:Property\>  
        \<edoal:compose rdf:parseType\="Collection"\>  
          \<edoal:Relation rdf:about\="\&vin;hasTerroir" /\>  
          \<edoal:Property rdf:about\="\&proton;name" /\>  
        \</edoal:compose\>  
      \</edoal:Property\>  
    \</edoal:onAttribute\>  
    \<edoal:comparator rdf:resource\="\&edoal;equals" /\>  
    \<edoal:value edoal:type\="\&xsd;string"\>Acquitaine\</edoal:value\>  
  \</edoal:AttributeValueRestriction\>

#### **6.2.2. edoal:AttributeOccurenceRestriction (属性カーディナリティ制約)**

属性のカーディナリティ（出現回数）を制約します（$owl:cardinality$, $owl:minCardinality$, $owl:maxCardinality$ に類似）。onAttribute, comparator, value（$xsd:integer$ リテラル）を使用します 1。

* **記述例:** 1  
  XML  
  \<edoal:AttributeOccurenceRestriction\>  
    \<edoal:onAttribute\>  
      \<edoal:Relation rdf:about\="\&vin;hasMaker" /\>  
    \</edoal:onAttribute\>  
    \<edoal:comparator rdf:resource\="\&edoal;greater-than" /\>  
    \<edoal:value\>  
      \<edoal:Literal edoal:type\="\&xsd;integer" edoal:string\="0" /\>  
    \</edoal:value\>  
  \</edoal:AttributeOccurenceRestriction\>

#### **6.2.3. edoal:AttributeDomainRestriction (属性ドメイン制約)**

属性（関係）のドメイン（値域）を特定のクラス式に制約します（$owl:someValuesFrom$ に類似）。onAttribute と class を使用します 1。この構文は、「\[属性\] が \[クラス\] であるようなすべてのもの」という強力なクラス表現を可能にします 8。

* **記述例:** 1  
  XML  
  \<edoal:AttributeDomainRestriction\>  
    \<edoal:onAttribute\>  
      \<edoal:Relation rdf:about\="\&cmt;hasDecision"/\>  
    \</edoal:onAttribute\>  
    \<edoal:class\>  
      \<edoal:Class rdf:about\="\&cmt;Acceptance"/\>  
    \</edoal:class\>  
  \</edoal:AttributeDomainRestriction\>

#### **6.2.4. edoal:AttributeTypeRestriction (属性タイプ制約)**

属性（プロパティ）のレンジ（値域）を特定のデータ型（XSDなど）に制約します（$owl:allValuesFrom$ のデータ型版に類似）。onAttribute と datatype を使用します 1。

* **記述例:** 1  
  XML  
  \<edoal:AttributeTypeRestriction\>  
    \<edoal:onAttribute\>  
      \<edoal:Property rdf:about\="\&vin;year" /\>  
    \</edoal:onAttribute\>  
    \<edoal:datatype\>  
      \<edoal:Datatype rdf:about\="\&xsd;gYear" /\>  
    \</edoal:datatype\>  
  \</edoal:AttributeTypeRestriction\>

#### **6.2.5. edoal:RelationDomainRestriction / edoal:RelationCoDomainRestriction**

$edoal:Relation$ 式に特化した制約です。RelationDomainRestriction は関係のドメイン（$rdfs:domain$）を、RelationCoDomainRestriction は関係のコドメイン（$rdfs:range$）を制約します 1。

* **記述例 (Domain制約):** 1  
  XML  
  \<edoal:Relation\>  
    \<edoal:RelationDomainRestriction\>  
      \<edoal:onAttribute\>  
        \<edoal:Relation rdf:about\="\&conf;reviewOfPaper" /\>  
      \</edoal:onAttribute\>  
      \<edoal:class\>  
        \<edoal:Class rdf:about\="\&conf;Reviewer" /\>  
      \</edoal:class\>  
    \</edoal:RelationDomainRestriction\>  
  \</edoal:Relation\>

### **6.3. 比較演算子 (Comparator) ライブラリ**

edoal:comparator の rdf:resource として使用されるURIは、述語として機能します。公式仕様 1 は equals, lower-than, greater-than の3つのみを例示していますが、これは不完全です。技術レポート D2.2.10 6 には、EDOALセマンティクスで想定される包括的な比較演算子ライブラリ（Table B.2）が記載されています。

本仕様書は、Table 1 に示す演算子を EDOAL 1.0 の標準比較演算子ライブラリとして定義します。

**Table 1: EDOAL 比較演算子 (Comparators) 仕様** (D2.2.10, Table B.2 に基づく) 6

| 演算子 (推奨URIプレフィックス: edoal:) | 参照 (Origin) | 定義 (セマンティクス) |
| :---- | :---- | :---- |
| all-equal | XQuery | 第1引数と第2引数が（型と値を考慮して）等しい場合に satisfied。edoal:equals と同義。 |
| all-not-equal | SWRL | all-equal の否定。 |
| ordered-less-than | XQuery | 第1引数と第2引数が順序付け可能な型であり、第1引数が第2引数より小さい場合に satisfied。edoal:lower-than と同義。 |
| ordered-less-than-or-equal | SWRL | 第1引数が第2引数以下の場合に satisfied。 |
| ordered-greater-than | XQuery | 第1引数が第2引数より大きい場合に satisfied。edoal:greater-than と同義。 |
| ordered-greater-than-or-equal | SWRL | 第1引数が第2引数以上の場合に satisfied。 |
| string-contains | XQuery | 第1引数（文字列）が第2引数（文字列）を含む場合に satisfied（大文字小文字を区別）。 |
| string-starts-with | XQuery | 第1引数が第2引数で始まる場合に satisfied。 |
| string-ends-with | XQuery | 第1引数が第2引数で終わる場合に satisfied。 |
| string-matches | XQuery | 第1引数が第2引数（正規表現）にマッチする場合に satisfied。 |
| collection-contains | XQuery | 第1引数（コレクション）が第2引数（要素）を含む場合に satisfied。 |
| collection-includes | XQuery | 第1引数（コレクション）が第2引数（コレクション）の全ての要素を含む場合に satisfied。 |
| collection-includes-strictly | XQuery | 第1引数が第2引数の全ての要素を含み、かつ第1引数がより多くの要素を持つ場合に satisfied。 |
| collection-empty | \- | 第1引数（コレクション）が空である場合に satisfied。 |

## **7\. 【拡張仕様】値表現と変換 (Value Expressions & Transformation)**

エンティティ式（Class, Property等）とは異なり、インスタンスやリテラル値、またはそれらを変換した結果の値を表現するための構文です。これらは主に AttributeValueRestriction の value 要素や Apply の arguments 内で使用されます。

### **7.1. リテラル (edoal:Literal)**

型付きリテラル値を表現します 1。

* **属性:**  
  * edoal:type: リテラルのデータ型をURIで指定します（例: \&xsd;string, \&xsd;integer）。  
  * edoal:string: リテラルの字句表現（文字列値）。  
* **記述例 (標準構文):** 1  
  XML  
  \<edoal:value\>  
    \<edoal:Literal edoal:type\="\&xsd;integer" edoal:string\="123" /\>  
  \</edoal:value\>

* 記述例 (簡易構文):  
  edoal:value 要素に edoal:type 属性とテキストノードを直接記述する簡易構文も許容されます 1。  
  XML  
  \<edoal:value edoal:type\="\&xsd;string"\>Acquitaine\</edoal:value\>

### **7.2. 関数適用 (edoal:Apply)**

1つ以上の引数（値表現）に演算子（関数）を適用し、新たな値を生成します 1。これは、データ変換（Transformation）の核となる構文です。

* **要素と属性:**  
  * \<edoal:Apply edoal:operator=""\>: 適用する関数（変換演算子または述語演算子）のURIを指定します 1。  
  * \<edoal:arguments rdf:parseType="Collection"\>: 関数に渡す引数の順序付きリスト。引数には $edoal:Literal$, $edoal:Instance$, $edoal:Property$（パス式）、またはネストされた $edoal:Apply$ などの値表現を使用できます 1。  
* **記述例 (文字列結合):** 1  
  XML  
  \<entity2\>  
    \<edoal:Apply edoal:operator\="\&fn;concat"\>  
      \<edoal:arguments rdf:parseType\="Collection"\>  
        \<edoal:Property rdf:about\="\&vcard;firstname" /\>  
        \<edoal:Literal edoal:type\="\&xsd;string" edoal:string\=" " /\>  
        \<edoal:Property rdf:about\="\&vcard;lastname" /\>  
      \</edoal:arguments\>  
    \</edoal:Apply\>  
  \</entity2\>

* 記述例 (外部サービス利用):  
  edoal:operator には、外部のWebサービスURIなどを指定することも可能です 1。  
  XML  
  \<entity2\>  
    \<edoal:Apply edoal:operator\="http://www.google.com/finance/converter"\>  
      \<edoal:arguments rdf:parseType\="Collection"\>  
        \<edoal:Property\>\<edoal:compose rdf:parseType\="Collection"/\>\</edoal:Property\>  
        \<edoal:Literal edoal:string\="EUR" /\>  
        \<edoal:Literal edoal:string\="CNY" /\>  
      \</edoal:arguments\>  
    \</edoal:Apply\>  
  \</entity2\>

### **7.3. 変換演算子 (Transformation Operator) ライブラリ**

edoal:Apply の edoal:operator で使用されるURIについて、EDOAL 1.0 公式仕様 1 は特定のリストを定義していません。代わりに、「可能な限り XQuery 1.0 and XPath 2.0 Functions and Operators (F\&O) の使用を推奨する」（推奨プレフィックス fn:）としています。

しかし、技術レポート D2.2.10 6 は、EDOALセマンティクスで中核的に想定される変換演算子のリスト（Table B.1）を明記しています。本仕様書は、Table 2 に示す演算子を EDOAL 1.0 の推奨変換演算子ライブラリとして定義します。

**Table 2: EDOAL 変換演算子 (Transformation Operators) 仕様** (D2.2.10, Table B.1 に基づく) 6

| 演算子 (推奨URIプレフィックス: fn:) | カテゴリ | 参照 (Origin) | 定義 (セマンティクス) |
| :---- | :---- | :---- | :---- |
| concat | string | XQuery | 複数の文字列を連結する。 |
| substring | string | XQuery | 文字列の一部を抽出する (開始位置、終了位置を指定)。 |
| length | string | XQuery | 文字列の長さ（文字数）を整数で返す。 |
| normalize-space | string | XQuery | 文字列の前後の空白を削除し、途中の連続する空白を1つに正規化する。 |
| add | numeric | XQuery | 2つの数値を加算する。 |
| subtract | numeric | XQuery | 第1引数から第2引数を減算する。 |
| multiply | numeric | XQuery | 2つの数値を乗算する。 |
| divide | numeric | XQuery | 第1引数を第2引数で除算する。 |

## **8\. 【拡張仕様】インスタンスマッチング (Linkkeys)**

Linkkeyは、EDOALの高度な機能であり、スキーマレベル（TBox）のアライメントとインスタンスレベル（ABox）のマッチングを橋渡しします 1。

align:Cell が2つのクラス間の対応（例：Livre \= Novel）を定義するとき、edoal:linkkey は、それらのクラスのインスタンス（個々の本）がどのような条件で $owl:sameAs$ と見なされるべきかを定義するルールセットを提供します 1。

### **8.1. edoal:linkkey**

align:Cell の子要素として使用されるプロパティで、インスタンス間の等価性条件を定義する edoal:Linkkey オブジェクトを値としてとります。

* **構文:** \<edoal:linkkey\> \<edoal:Linkkey\>... \</edoal:Linkkey\> \</edoal:linkkey\>  
* **記述例:** 1  
  XML  
  \<align:Cell rdf:about\="\#cell-with-linkkey"\>  
    \<align:entity1\>\<edoal:Class rdf:about\="\&ex1;Livre" /\>\</align:entity1\>  
    \<align:entity2\>\<edoal:Class rdf:about\="\&ex2;Novel" /\>\</align:entity2\>  
    \<align:relation\>\=\</align:relation\>

    \<edoal:linkkey\>  
      \<edoal:Linkkey\>  
        \</edoal:Linkkey\>  
    \</edoal:linkkey\>  
  \</align:Cell\>

### **8.2. edoal:binding**

edoal:Linkkey オブジェクトのプロパティであり、単一のプロパティ間比較ルールを定義します。Linkkey は複数の binding を持つことができ、それらは通常 AND 条件として解釈されます。

* **構文:** \<edoal:binding\> \[比較演算子\] \</edoal:binding\>  
* **記述例:** 1  
  XML  
  \<edoal:Linkkey\>  
    \<edoal:binding\>  
      \</edoal:binding\>  
    \<edoal:binding\>  
      \</edoal:binding\>  
  \</edoal:Linkkey\>

### **8.3. edoal:Equals**

edoal:binding の内部で使用される比較演算子クラス。2つのプロパティ（property1 と property2）の値が等価であるべきことを示します。

* **構文:** \<edoal:Equals\> \<edoal:property1\>...\</edoal:property1\> \<edoal:property2\>...\</edoal:property2\> \</edoal:Equals\>  
* **記述例:** 1  
  XML  
  \<edoal:binding\>  
    \<edoal:Equals\>  
      \<edoal:property1\>\<edoal:Property rdf:about\="\&ex1;titre" /\>\</edoal:property1\>  
      \<edoal:property2\>\<edoal:Property rdf:about\="\&ex2;title" /\>\</edoal:property2\>  
    \</edoal:Equals\>  
  \</edoal:binding\>

### **8.4. edoal:Intersects**

edoal:binding の内部で使用される比較演算子クラス。2つのプロパティ（通常、複数の値を持つ関係）の値域が空でない共通部分を持つべきことを示します。

* **構文:** \<edoal:Intersects\> \<edoal:property1\>...\</edoal:property1\> \<edoal:property2\>...\</edoal:property2\> \</edoal:Intersects\>  
* **記述例:** 1  
  XML  
  \<edoal:binding\>  
    \<edoal:Intersects\>  
      \<edoal:property1\>\<edoal:Relation rdf:about\="\&ex1;auteur" /\>\</edoal:property1\>  
      \<edoal:property2\>\<edoal:Relation rdf:about\="\&ex2;creator" /\>\</edoal:property2\>  
    \</edoal:Intersects\>  
  \</edoal:binding\>

## **9\. 【拡張仕様】変数 (Variables) とパターン言語**

edoal:Variable の扱いは、EDOAL 1.0 仕様において厳密な解釈を必要とします。

### **9.1. edoal:Variable の定義と位置づけ**

EDOAL 1.0 の公式仕様 1 には、edoal:Variable に関する2つの重要な記述が存在します。

1. **パターン言語の一部:** 変数 (Variable) は、「エンティティを抽象化できる一般化された対応関係を表現する」ための「**パターン言語 (pattern language)**」の導入要素であると説明されています 1。  
2. **将来のリリース:** この「パターン言語」自体は、「**後日リリース予定 (will be released at a later stage)**」であると明記されています 1。

### **9.2. EDOAL 1.0 における厳密な解釈**

上記 9.1 に基づき、本仕様書は EDOAL 1.0 における変数の位置づけを以下のように厳密に定義します。

* **セマンティクスの不在:** edoal:Variable クラス、および変数のスコープ、束縛、edoal:Apply での参照といったセマンティクスは、EDOAL 1.0 の仕様範囲外 (undefined) です。これらは将来の「EDOAL Pattern Language」で定義されることが意図されています。  
* **構文フックの存在:** EDOAL 1.0 のパーサーは、9.3 で定義される edoal:var 属性を認識する必要がありますが、これは将来の拡張性のための構文的フック (syntactic hook) としてのみ機能します。

### **9.3. edoal:var 属性**

EDOAL 1.0 仕様で定義されている変関連の唯一の構文は、edoal:var 属性です。

* **定義:** edoal:Class, edoal:Property などのエンティティ式タグに付与できる属性。そのエンティティ式にローカルな変数名（URIフラグメント）を関連付けます 1。  
* **記述例 (RDF/XML 構文):** 1  
  XML  
  \<edoal:Class edoal:var\="\#var1" /\>

* 記述例 (N3 構文 / 参考):  
  公式仕様 1 は、edoal:var 属性がRDFレベルでどのように解釈されるかを示唆するN3構文の例も示しています。これは \#var1 が edoal:Variable 型のインスタンスであることを示しています。  
  コード スニペット  
  :var1 a edoal:Variable;

#### **引用文献**

1. EDOAL: Expressive and Declarative Ontology Alignment Language, 11月 6, 2025にアクセス、 [https://ns.inria.fr/edoal/1.0/](https://ns.inria.fr/edoal/1.0/)  
2. The Alignment API 4.0 \- Semantic Web Journal, 11月 6, 2025にアクセス、 [https://www.semantic-web-journal.net/sites/default/files/swj60\_0.pdf](https://www.semantic-web-journal.net/sites/default/files/swj60_0.pdf)  
3. Alignment API \- Semantic Web Standards \- W3C, 11月 6, 2025にアクセス、 [https://www.w3.org/2001/sw/wiki/Alignment\_API](https://www.w3.org/2001/sw/wiki/Alignment_API)  
4. Exmo research pages: Alignments, 11月 6, 2025にアクセス、 [https://www.inrialpes.fr/exmo/research/align.html](https://www.inrialpes.fr/exmo/research/align.html)  
5. D2.2.10: Expressive alignment language and ... \- Knowledge Web, 11月 6, 2025にアクセス、 [https://knowledgeweb.semanticweb.org/semanticportal/deliverables/D2.2.10.pdf](https://knowledgeweb.semanticweb.org/semanticportal/deliverables/D2.2.10.pdf)  
6. (PDF) Expressive alignment language and implementation, 11月 6, 2025にアクセス、 [https://www.researchgate.net/publication/261179983\_Expressive\_alignment\_language\_and\_implementation](https://www.researchgate.net/publication/261179983_Expressive_alignment_language_and_implementation)  
7. The Alignment API 4.0 \- Semantic Web Journal, 11月 6, 2025にアクセス、 [https://www.semantic-web-journal.net/sites/default/files/swj60\_1.pdf](https://www.semantic-web-journal.net/sites/default/files/swj60_1.pdf)  
8. ekaw-cmt.edoal