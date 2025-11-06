"""
EDOAL アラインメントを簡易パースしてエンティティ対応関係を抽出するモジュール
- 現在は主に <Cell> 要素内の entity1 / entity2 を抽出する
- 出力は AlignmentMapping (entity_map: dict)
"""
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET
import json
import os

import logging
import os
from datetime import datetime


def get_logger(name: str, verbose: bool = False) -> logging.Logger:
    """ロガーを取得する。ログファイルは project_root/log/YYYY-MM-DD.log に保存される

    Args:
        name (str): ロガー名
        verbose (bool): True の場合コンソールに DEBUG を出力する
    Returns:
        logging.Logger: 設定済みロガー
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # log ディレクトリ
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'log')
    os.makedirs(log_dir, exist_ok=True)

    filename = datetime.now().strftime('%Y-%m-%d') + '.log'
    file_path = os.path.join(log_dir, filename)

    fh = logging.FileHandler(file_path, encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if verbose else logging.WARNING)
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(ch)

    return logger

class AlignmentMapping:
    """アラインメントマッピングを保持するクラス

    Attributes:
        entity_map (Dict[str, str]): source_uri -> target_uri の対応辞書
        rules (List[Tuple[str,str]]): 抽出されたルールのリスト
    """

    def __init__(self):
        self.entity_map: Dict[str, str] = {}
        self.rules: List[Tuple[str, str]] = []

    def to_dict(self):
        return {"entity_map": self.entity_map, "rules": self.rules}


def _ns(tag: str):
    # 簡易: 名前空間接頭辞があっても最後の localname を返す。パース時にタグ名比較に用いる程度
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def parse_alignment(path: str, verbose: bool = False) -> AlignmentMapping:
    """EDOAL (RDF/XML) を読み、対応関係を抽出する簡易パーサ

    Args:
        path (str): EDOAL XML ファイルのパス
        verbose (bool): 詳細ログ出力

    Returns:
        AlignmentMapping: 抽出結果
    """
    logger = get_logger('alignment_parser', verbose)
    mapping = AlignmentMapping()

    if not os.path.exists(path):
        logger.error(f"アラインメントファイルが見つかりません: {path}")
        raise FileNotFoundError(path)

    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError as e:
        logger.error(f"アラインメント XML のパースに失敗しました: {e}")
        raise

    # 単純な戦略: <Cell> 要素を探し、その内部で entity1/entity2 (または <entity rdf:resource=> 等) を探す
    cell_tags = []
    for elem in root.iter():
        if _ns(elem.tag).lower() == 'cell':
            cell_tags.append(elem)

    logger.info(f"Cell 要素数: {len(cell_tags)}")

    for c in cell_tags:
        src = None
        tgt = None
        # 子要素を探索
        for child in c.iter():
            name = _ns(child.tag).lower()
            # rdf:resource 属性や rdf:about / about を確認
            res = None
            for attr_key in child.attrib:
                if attr_key.endswith('resource') or attr_key.endswith('about'):
                    res = child.attrib[attr_key]
                    break
            # 要素名が entity1/entity2 の場合中身の resource を探す
            if name in ('entity1', 'entity') and res:
                if not src:
                    src = res
            elif name in ('entity2',) and res:
                tgt = res
            # または直接 <uri> などがある場合
            if name in ('uri',) and child.text and not src:
                src = child.text.strip()
            if name in ('uri',) and child.text and src and not tgt:
                tgt = child.text.strip()

        # 別の形式: Cell の直下に pair of <object1 resource..> と <object2 resource..>
        # それらが見つからない場合、子要素のテキストから heuristics
        if not src or not tgt:
            # より広く resource を探す
            resources = []
            for descendant in c.iter():
                for attr_key in descendant.attrib:
                    if attr_key.endswith('resource') or attr_key.endswith('about'):
                        resources.append(descendant.attrib[attr_key])
            if len(resources) >= 2:
                if not src:
                    src = resources[0]
                if not tgt:
                    tgt = resources[1]

        if src and tgt:
            mapping.entity_map[src] = tgt
            mapping.rules.append((src, tgt))
            logger.debug(f"抽出ルール: {src} -> {tgt}")
        else:
            logger.debug(f"Cell の解析でエンティティが見つかりませんでした: {ET.tostring(c, encoding='unicode')[:200]}")

    if verbose:
        # 中間結果を debug_output に出力
        dbg_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'debug_output')
        os.makedirs(dbg_dir, exist_ok=True)
        out_path = os.path.join(dbg_dir, os.path.basename(path) + '.mapping.json')
        with open(out_path, 'w', encoding='utf-8') as fh:
            json.dump(mapping.to_dict(), fh, ensure_ascii=False, indent=2)
        logger.info(f"マッピング中間結果を出力しました: {out_path}")

    logger.info(f"抽出されたルール数: {len(mapping.rules)}")
    return mapping

if __name__ == '__main__':
    # 簡易デモ
    import sys

    alignment_file = sys.argv[1]
    mapping = parse_alignment(alignment_file, verbose=True)
    print("抽出されたエンティティ対応関係:")
    for src, tgt in mapping.rules:
        print(f"  {src} -> {tgt}")