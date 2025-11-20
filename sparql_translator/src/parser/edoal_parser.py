"""
EDOAL (簡易) パーサ

このモジュールは EDOAL 形式のアラインメント XML を読み取り、
内部的なエンティティ表現（クラス、プロパティ、制約、論理結合など）を
Python の dataclass にマッピングする簡易パーサを実装しています。

注意:
- 本実装は学習/プロトタイプ用途の簡易実装であり、EDOAL 全仕様を網羅していません。
- コードの振る舞いは変更せず、日本語コメントを追加しています。
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Any, Optional
import csv
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Any, Optional

# 基底クラス
@dataclass
class EDOALEntity:
    """EDOAL 内の任意のエンティティの基底クラス

    具体的なエンティティ（識別子を持つもの、論理構成子、制約など）は
    このクラスを継承して表現します。
    """
    pass


@dataclass
class IdentifiedEntity(EDOALEntity):
    uri: str

    """URI によって識別されるエンティティの基底クラス

    例: クラス、プロパティ、個体など、EDOAL内でURIを持つ要素を表現します。
    """

## 以下4つはエンティティの型を表すデータクラス
@dataclass
class Class(IdentifiedEntity):
    """OWL/RDF の Class を表すシンプルなデータクラス（URI を保持）"""
    pass

@dataclass
class Property(IdentifiedEntity):
    """プロパティ（属性）を表すデータクラス（URI を保持）"""
    pass

@dataclass
class Relation(IdentifiedEntity):
    """関係（Relation）を表すデータクラス（URI を保持）"""
    pass

@dataclass
class Instance(IdentifiedEntity):
    """個体（インスタンス）を表すデータクラス（URI を保持）"""
    pass

# 論理構成子や制約を表すクラス
@dataclass
class LogicalConstructor(EDOALEntity):
    operator: str
    operands: List[EDOALEntity] = field(default_factory=list)

    """論理結合子 (AND/OR/NOT など) を表現するクラス

    operator: 結合子の名前（'and','or','not' など）
    operands: 結合される子要素のリスト
    """

@dataclass
class PathConstructor(EDOALEntity):
    operator: str
    operands: List[EDOALEntity] = field(default_factory=list)

    """経路/パスに関する構成子（compose, inverse, transitive など）"""

@dataclass
class Restriction(EDOALEntity):
    on_attribute: EDOALEntity

    """属性制約の基底クラス。on_attribute は制約対象の属性を指す"""

@dataclass
class AttributeValueRestriction(Restriction):
    comparator: str
    value: Any

    """属性の値に対する制約（比較演算子と値）を表すクラス"""

@dataclass
class AttributeDomainRestriction(Restriction):
    class_expression: EDOALEntity

    """属性のドメインに関する制約（属性の対象がどのクラスに属するか等）"""

@dataclass
class AttributeOccurenceRestriction(Restriction):
    comparator: str
    value: Any

    """属性の出現回数に対する制約（例: 'greater-than 0'で存在チェック）"""

@dataclass
class RelationDomainRestriction(EDOALEntity):
    class_expression: EDOALEntity

    """関係（Relation）のドメイン制約（主語がどのクラスに属するか）"""

@dataclass
class RelationCoDomainRestriction(EDOALEntity):
    class_expression: EDOALEntity

    """関係（Relation）のコドメイン制約（目的語がどのクラスに属するか）"""


@dataclass
class Cell:
    # EDOALEntityを継承
    entity1: EDOALEntity
    entity2: EDOALEntity
    relation: str
    measure: float

    """アラインメント上の 1 対応（Cell）を表すデータクラス

    entity1 / entity2: 対応する 2 つのエンティティ
    relation: 関係の種類（例: 'http://www.w3.org/2004/02/skos/core#exactMatch' のような文字列）
    measure: 一致度（スコア）
    """

@dataclass
class Alignment:
    onto1: str
    onto2: str
    cells: List[Cell] = field(default_factory=list)

    """アラインメント全体を保持するクラス

    onto1 / onto2: アラインメント対象となる2つのオントロジーの識別子（URI）
    cells: 対応（Cell）のリスト
    """

import sys

class EdoalParser:
    """EDOAL ファイルをパースするメインクラス

    Args:
        file_path: EDOAL (RDF/XML) ファイルのパス
        verbose: デバッグログを出力するかどうか (デフォルト: False)
    """
    def __init__(self, file_path, verbose=False):
        # ファイルパスを保持
        self.file_path = file_path
        self.verbose = verbose
        # XML を読み込んで ElementTree を構築
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        # 名前空間の辞書を初期化
        self.namespaces = self._get_namespaces()

    def _get_namespaces(self):
        """XML ファイルから使用されている名前空間を収集して辞書で返す

        Jinja のように名前空間プレフィックスが存在しない場合でも、
        EDOAL/RDF で一般的に使われるプレフィックスを補完します。
        """
        ns = dict([
            node for _, node in ET.iterparse(self.file_path, events=['start-ns'])
        ])
        # 必要な共通名前空間がなければ既定値を設定
        if 'rdf' not in ns:
            ns['rdf'] = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        if 'align' not in ns:
            ns['align'] = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        if 'edoal' not in ns:
            ns['edoal'] = 'http://ns.inria.org/edoal/1.0/#'
        # デフォルト名前空間が存在する場合は 'default' として参照可能にする
        if '' in ns:
            ns['default'] = ns['']
        return ns

    def parse(self) -> Alignment:
        """EDOAL XML をパースして Alignment オブジェクトを返す

        処理概要:
        - align:onto1 および align:onto2 の Ontology 要素から対象オントロジーを取得
        - 各 align:Cell を走査し、entity1/entity2/relation/measure を抽出
        - entity は _parse_entity を用いて再帰的に解析
        """
        # onto1/onto2 の抽出 (rdf:about 属性を使用)
        onto1 = self.root.find('.//align:onto1/align:Ontology', self.namespaces).get('{' + self.namespaces['rdf'] + '}about')
        onto2 = self.root.find('.//align:onto2/align:Ontology', self.namespaces).get('{' + self.namespaces['rdf'] + '}about')
        
        alignment = Alignment(onto1=onto1, onto2=onto2)

        # 各 Cell 要素を解析
        for cell_element in self.root.findall('.//align:Cell', self.namespaces):
            # entity1, entity2, relation, measure を取得（存在チェックを行う）
            entity1_element = cell_element.find('align:entity1', self.namespaces)
            entity2_element = cell_element.find('align:entity2', self.namespaces)
            relation_element = cell_element.find('align:relation', self.namespaces)
            measure_element = cell_element.find('align:measure', self.namespaces)

            # entity 要素は内部に実際の Class/Property 等の要素を持つ想定
            entity1 = self._parse_entity(entity1_element[0]) if entity1_element is not None and len(entity1_element) > 0 else None
            entity2 = self._parse_entity(entity2_element[0]) if entity2_element is not None and len(entity2_element) > 0 else None
            
            relation = relation_element.text if relation_element is not None else None
            measure = float(measure_element.text) if measure_element is not None else 0.0

            # 両方のエンティティが解析できた場合に Cell を追加
            if entity1 and entity2:
                alignment.cells.append(Cell(entity1, entity2, relation, measure))
        return alignment

    def _parse_entity(self, element: ET.Element) -> Optional[EDOALEntity]:
        """個々のエンティティ要素を再帰的に解析して EDOALEntity を返す

        処理:
        - 要素のタグ名を取得し、rdf:about があれば識別子として扱う
        - Class/Property/Relation/Instance のような識別可能な要素は対応する dataclass を返す
        - 制約（AttributeDomainRestriction/AttributeValueRestriction）や論理演算子は
          子要素を再帰的に解析して適切なオブジェクトに変換する
        - それ以外は IdentifiedEntity(URI を持たない複合エンティティ) として返す
        """
        if element is None:
            return None

        # タグのローカル名 (namespace を除去したもの)
        tag = element.tag.split('}')[-1]
        # rdf:about 属性があるかを確認（直接 URI を持つ要素）
        rdf_about = element.get('{' + self.namespaces['rdf'] + '}about')

        # 識別可能なエンティティ (URI を持つ)
        if rdf_about:
            if tag == 'Class': return Class(uri=rdf_about)
            if tag == 'Property': return Property(uri=rdf_about)
            if tag == 'Relation': return Relation(uri=rdf_about)
            if tag == 'Instance': return Instance(uri=rdf_about)
        
        # rdf:about を持たず、子要素を持つ場合は子要素を辿る（Container 的な表現）
        if tag in ['Class', 'Property', 'Relation'] and len(element) > 0:
            return self._parse_entity(element[0])

        # AttributeDomainRestriction の解析
        if tag == 'AttributeDomainRestriction':
            on_attr_elem = element.find('edoal:onAttribute', self.namespaces)
            class_expr_elem = element.find('edoal:class', self.namespaces)
            return AttributeDomainRestriction(
                on_attribute=self._parse_entity(on_attr_elem[0]) if on_attr_elem is not None and len(on_attr_elem) > 0 else None,
                class_expression=self._parse_entity(class_expr_elem[0]) if class_expr_elem is not None and len(class_expr_elem) > 0 else None
            )
        
        # AttributeValueRestriction の解析
        if tag == 'AttributeValueRestriction':
            on_attr_elem = element.find('edoal:onAttribute', self.namespaces)
            comparator_elem = element.find('edoal:comparator', self.namespaces)
            value_elem = element.find('edoal:value', self.namespaces)
            
            # valueの解析: LiteralまたはURIリファレンス
            value = None
            if value_elem is not None and len(value_elem) > 0:
                value_child = value_elem[0]
                value_tag = value_child.tag.split('}')[-1] if '}' in value_child.tag else value_child.tag
                
                if value_tag == 'Literal':
                    # Literalの場合: edoal:string, edoal:type属性を取得
                    value = {
                        'string': value_child.get('{' + self.namespaces['edoal'] + '}string', ''),
                        'type': value_child.get('{' + self.namespaces['edoal'] + '}type', '')
                    }
                elif value_tag in ['Class', 'Property', 'Relation', 'Instance']:
                    # URIリファレンスの場合
                    uri = value_child.get('{' + self.namespaces['rdf'] + '}about')
                    if uri:
                        value = {'uri': uri}
                else:
                    # その他の場合はエンティティとして解析
                    value = self._parse_entity(value_child)
            
            return AttributeValueRestriction(
                on_attribute=self._parse_entity(on_attr_elem[0]) if on_attr_elem is not None and len(on_attr_elem) > 0 else None,
                comparator=comparator_elem.get('{' + self.namespaces['rdf'] + '}resource') if comparator_elem is not None else None,
                value=value
            )
        
        # AttributeOccurenceRestriction の解析
        if tag == 'AttributeOccurenceRestriction':
            on_attr_elem = element.find('edoal:onAttribute', self.namespaces)
            comparator_elem = element.find('edoal:comparator', self.namespaces)
            value_elem = element.find('edoal:value', self.namespaces)
            
            # valueの解析: 通常は数値（出現回数）
            value = None
            if value_elem is not None:
                value_text = value_elem.text
                if value_text:
                    try:
                        value = int(value_text)
                    except ValueError:
                        value = value_text
            
            return AttributeOccurenceRestriction(
                on_attribute=self._parse_entity(on_attr_elem[0]) if on_attr_elem is not None and len(on_attr_elem) > 0 else None,
                comparator=comparator_elem.get('{' + self.namespaces['rdf'] + '}resource') if comparator_elem is not None else None,
                value=value
            )
        
        # RelationDomainRestriction の解析
        if tag == 'RelationDomainRestriction':
            class_elem = element.find('edoal:class', self.namespaces)
            return RelationDomainRestriction(
                class_expression=self._parse_entity(class_elem[0]) if class_elem is not None and len(class_elem) > 0 else None
            )
        
        # RelationCoDomainRestriction の解析
        if tag == 'RelationCoDomainRestriction':
            class_elem = element.find('edoal:class', self.namespaces)
            return RelationCoDomainRestriction(
                class_expression=self._parse_entity(class_elem[0]) if class_elem is not None and len(class_elem) > 0 else None
            )

        # 論理演算子やパス構成子 (and, or, compose, inverse, transitive, not)
        if tag in ['and', 'or', 'compose', 'inverse', 'transitive', 'not']:
             # rdf:parseType="Collection" の場合は要素の順序を保持して複数オペランドを解析
             # elementの直下の子要素をすべて走査する
             operands = []
             for child in element:
                 parsed = self._parse_entity(child)
                 if parsed is not None:
                     operands.append(parsed)
             
             # デバッグログ: パース結果を出力
             if self.verbose:
                 print(f"[DEBUG EdoalParser] Parsed {tag} with {len(operands)} operands:")
                 for idx, op in enumerate(operands):
                     print(f"  Operand {idx}: {type(op).__name__} - {op}")
             
             if tag in ['and', 'or', 'not']:
                 return LogicalConstructor(operator=tag, operands=operands)
             else:
                 return PathConstructor(operator=tag, operands=operands)

        # 上記に該当しない複合エンティティは汎用の IdentifiedEntity として返す
        return IdentifiedEntity(uri=f"Complex Entity: {tag}")

# parseしたAlignmentとEDOAL内部の構造を比較するための関数
def compare_alignment_and_edoal(alignment: Alignment, edoal_parser: EdoalParser, output_csv_path: str = "comparison_output.csv"):
    """パースした Alignment オブジェクトと元の EDOAL XML の構造を比較するデバッグ用関数
        CSVファイルに、各セルの比較を出力する。
    """
    import os

    # EDOAL ファイルを読み込んでテキストとして取得
    with open(edoal_parser.file_path, 'r', encoding='utf-8') as f:
        edoal_text = f.read()

    # EDOAL XML から Cell 要素を取得
    edoal_cells = edoal_parser.root.findall('.//align:Cell', edoal_parser.namespaces)

    # 比較結果を CSV に書き出す
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Cell_Index', 'Parsed_Cell_About', 'EDOAL_Cell_About', 'EDOAL_Cell_XML',
            'Parsed_Entity1_URI', 'EDOAL_Entity1_URI', 'EDOAL_Entity1_XML',
            'Parsed_Entity2_Structure', 'EDOAL_Entity2_XML',
            'Parsed_Alignment',
            'Parsed_Relation', 'EDOAL_Relation',
            'Parsed_Measure', 'EDOAL_Measure',
            'Entity1_Match', 'Entity2_Match', 'Relation_Match', 'Measure_Match'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, parsed_cell in enumerate(alignment.cells):
            if i < len(edoal_cells):
                edoal_cell = edoal_cells[i]

                # Cell の about 属性と XML
                parsed_about = f"Cell {i+1}"
                edoal_about = edoal_cell.get(f"{{{edoal_parser.namespaces['rdf']}}}about", "N/A")

                # EDOAL XML から Cell のテキストを抽出 (インデント調整)
                edoal_cell_xml = extract_xml_section(edoal_text, '<Cell', '</Cell>', about_attr=edoal_about).strip()

                # Entity1 の比較
                parsed_entity1_uri = getattr(parsed_cell.entity1, 'uri', str(parsed_cell.entity1))
                edoal_entity1_elem = edoal_cell.find('align:entity1', edoal_parser.namespaces)
                edoal_entity1_xml = extract_xml_section(edoal_text, '<entity1>', '</entity1>', cell_index=i).strip()
                # 簡易的に URI を抽出
                edoal_entity1_uri = "N/A"
                if edoal_entity1_elem is not None and len(edoal_entity1_elem) > 0:
                    inner_elem = edoal_entity1_elem[0]
                    edoal_entity1_uri = inner_elem.get(f"{{{edoal_parser.namespaces['rdf']}}}about", "Complex Structure")

                entity1_match = parsed_entity1_uri == edoal_entity1_uri

                # Entity2 の比較 (複雑な構造のため、XML文字列を比較)
                parsed_entity2_str = str(parsed_cell.entity2)
                edoal_entity2_elem = edoal_cell.find('align:entity2', edoal_parser.namespaces)
                edoal_entity2_xml = extract_xml_section(edoal_text, '<entity2>', '</entity2>', cell_index=i).strip()
                # 簡易マッチング: URI が一致するか、または構造の基本部分
                entity2_match = False
                if hasattr(parsed_cell.entity2, 'uri'):
                    parsed_uri = parsed_cell.entity2.uri
                    # EDOAL XML から URI を抽出 (簡易)
                    if edoal_entity2_elem is not None:
                        inner_elem = edoal_entity2_elem.find('.//*[@rdf:about]', edoal_parser.namespaces)
                        if inner_elem is not None:
                            edoal_uri = inner_elem.get(f"{{{edoal_parser.namespaces['rdf']}}}about")
                            entity2_match = parsed_uri == edoal_uri
                        else:
                            entity2_match = "Complex" in parsed_entity2_str and "Complex" in edoal_entity2_xml
                else:
                    entity2_match = "Complex" in parsed_entity2_str and "Complex" in edoal_entity2_xml

                # Relation の比較
                parsed_relation = parsed_cell.relation
                edoal_relation_elem = edoal_cell.find('align:relation', edoal_parser.namespaces)
                edoal_relation = edoal_relation_elem.text if edoal_relation_elem is not None else "N/A"
                relation_match = parsed_relation == edoal_relation

                # Measure の比較
                parsed_measure = parsed_cell.measure
                edoal_measure_elem = edoal_cell.find('align:measure', edoal_parser.namespaces)
                edoal_measure_text = edoal_measure_elem.text if edoal_measure_elem is not None else "0.0"
                try:
                    edoal_measure = float(edoal_measure_text)
                except ValueError:
                    edoal_measure = 0.0
                measure_match = abs(parsed_measure - edoal_measure) < 1e-6

                # パースした Alignment の内容
                parsed_alignment = str(parsed_cell)

                # CSV に書き込み
                writer.writerow({
                    'Cell_Index': i + 1,
                    'Parsed_Cell_About': parsed_about,
                    'EDOAL_Cell_About': edoal_about,
                    'EDOAL_Cell_XML': edoal_cell_xml,
                    'Parsed_Entity1_URI': parsed_entity1_uri,
                    'EDOAL_Entity1_URI': edoal_entity1_uri,
                    'EDOAL_Entity1_XML': edoal_entity1_xml,
                    'Parsed_Entity2_Structure': parsed_entity2_str,
                    'EDOAL_Entity2_XML': edoal_entity2_xml,
                    'Parsed_Alignment': parsed_alignment,
                    'Parsed_Relation': parsed_relation,
                    'EDOAL_Relation': edoal_relation,
                    'Parsed_Measure': parsed_measure,
                    'EDOAL_Measure': edoal_measure,
                    'Entity1_Match': entity1_match,
                    'Entity2_Match': entity2_match,
                    'Relation_Match': relation_match,
                    'Measure_Match': measure_match
                })

    print(f"Comparison output saved to {output_csv_path}")

def extract_xml_section(full_text: str, start_tag: str, end_tag: str, about_attr: str = None, cell_index: int = None) -> str:
    """EDOAL テキストから特定の XML セクションを抽出するヘルパー関数"""
    import re

    if about_attr:
        # Cell の場合、rdf:about 属性で特定 (alignment.edoal の構造に合わせる)
        # 実際のファイル構造に合わせたパターン
        pattern = rf'(\s*<Cell[^>]*rdf:about="{re.escape(about_attr)}"[^>]*>.*?</Cell>)'
        match = re.search(pattern, full_text, re.DOTALL)
        if match:
            return match.group(1).strip()

    elif cell_index is not None:
        # entity1/entity2 の場合、出現順で特定
        # 実際のファイル構造に合わせたパターン
        if 'entity1' in start_tag:
            pattern = r'(\s*<entity1>.*?</entity1>)'
        elif 'entity2' in start_tag:
            pattern = r'(\s*<entity2>.*?</entity2>)'
        else:
            return "N/A"

        matches = list(re.finditer(pattern, full_text, re.DOTALL))
        if cell_index < len(matches):
            return matches[cell_index].group(1).strip()

    return "N/A"


# 使用例: テストデータを使用して比較
if __name__ == '__main__':
    def compare_alignment(file_path):
        parser = EdoalParser(file_path=file_path)
        alignment_result = parser.parse()
        print(f"Ontology 1: {alignment_result.onto1}")
        print(f"Ontology 2: {alignment_result.onto2}")
        print(f"Found {len(alignment_result.cells)} correspondences.")
        print("=" * 30)
        for i, cell in enumerate(alignment_result.cells):
            print(f"--- Cell {i+1} ---")
            print(f"  Entity 1: {cell.entity1}")
            print(f"  Entity 2: {cell.entity2}")
            print(f"  Relation: {cell.relation}")
            print(f"  Measure:  {cell.measure}")
        print("=" * 30)
            # 比較関数を呼び出し
        dataset_name = os.path.basename(os.path.dirname(os.path.dirname(alignment_file)))
        parent = os.path.basename(os.path.dirname(alignment_file))
        base = os.path.splitext(os.path.basename(alignment_file))[0]
        output_csv = f"res/{dataset_name + '_' if parent else ''}{base}_comparison.csv"
        compare_alignment_and_edoal(alignment_result, parser, output_csv)

    # デフォルトのテストファイルをリストアップ
    test_files = [
        "test_data/agro-db/alignment/alignment.edoal",
        "test_data/conference/alignment/alignment.edoal",
        "test_data/taxons/alignment/alignment.edoal",
        "test_data/agronomic-voc/alignment/alignment.edoal"
    ]

    if len(sys.argv) > 1:
        alignment_file = sys.argv[1]
        compare_alignment(alignment_file)
    else:
        for alignment_file in test_files:
            compare_alignment(alignment_file)