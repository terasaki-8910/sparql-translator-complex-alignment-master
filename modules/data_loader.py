"""
data_loader.py
ファイルベースとエンドポイントベースのデータソースを統合的に扱うモジュール

設計原則:
- ファクトリパターンによる type フィールドの厳密な解釈
- rdflib (file) と SPARQLWrapper (endpoint) の透過的な切り替え
- コンテキスト無視の禁止 (Prohibition.md Section 3)
"""

from typing import Union, Dict, Any, List
from pathlib import Path
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON
from modules.config_loader import ConfigLoader


class DataSourceFactory:
    """
    データソースのファクトリクラス
    type フィールドに基づいて適切なクライアントを生成
    """
    
    @staticmethod
    def create_source(dataset_info: Dict[str, Any], config_loader: ConfigLoader):
        """
        データセット情報から適切なデータソースを生成
        
        Args:
            dataset_info: datasets_registry.json からのデータセット情報
            config_loader: ConfigLoaderインスタンス
            
        Returns:
            FileDataSource または EndpointDataSource
            
        Raises:
            ValueError: type フィールドが不正な場合
        """
        ds_type = dataset_info.get("type")
        
        if ds_type == "file":
            return FileDataSource(dataset_info, config_loader.project_root)
        elif ds_type == "endpoint":
            return EndpointDataSource(dataset_info)
        else:
            raise ValueError(f"不正なデータセットタイプ: {ds_type}")


class FileDataSource:
    """
    ファイルベースのRDFデータソース
    rdflib を使用してローカルファイルをロード
    """
    
    def __init__(self, dataset_info: Dict[str, Any], project_root: Path):
        """
        Args:
            dataset_info: データセット情報
            project_root: プロジェクトルート
        """
        self.dataset_info = dataset_info
        self.project_root = Path(project_root)
        self.graph = None
        self._load_graph()
    
    def _load_graph(self):
        """
        RDFファイルを rdflib.Graph にロード
        """
        file_path = self.dataset_info.get("path")
        if not file_path:
            raise ValueError("ファイルデータソースに path が指定されていません")
        
        # 絶対パスに変換
        if not Path(file_path).is_absolute():
            file_path = self.project_root / file_path
        else:
            file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"データセットファイルが見つかりません: {file_path}")
        
        # フォーマットを決定
        format_map = {
            "turtle": "turtle",
            "xml": "xml",
            "n3": "n3",
            "nt": "nt"
        }
        rdf_format = format_map.get(self.dataset_info.get("format", "turtle"), "turtle")
        
        self.graph = rdflib.Graph()
        try:
            self.graph.parse(str(file_path), format=rdf_format)
        except Exception as e:
            raise RuntimeError(f"RDFファイルのパースに失敗: {file_path}, エラー: {e}")
    
    def query(self, sparql_query: str) -> List[Dict[str, Any]]:
        """
        SPARQLクエリを実行
        
        Args:
            sparql_query: SPARQL クエリ文字列
            
        Returns:
            クエリ結果のリスト
        """
        if not self.graph:
            raise RuntimeError("グラフがロードされていません")
        
        try:
            results = self.graph.query(sparql_query)
            return self._convert_results(results)
        except Exception as e:
            raise RuntimeError(f"SPARQL クエリの実行に失敗: {e}")
    
    def _convert_results(self, results) -> List[Dict[str, Any]]:
        """
        rdflib の結果を辞書リストに変換
        
        Args:
            results: rdflib.query.Result
            
        Returns:
            結果の辞書リスト
        """
        converted = []
        for row in results:
            row_dict = {}
            for var in results.vars:
                value = row[var]
                if value is not None:
                    row_dict[str(var)] = str(value)
            converted.append(row_dict)
        return converted
    
    def get_type(self) -> str:
        return "file"


class EndpointDataSource:
    """
    エンドポイントベースのSPARQLデータソース
    SPARQLWrapper を使用してリモートエンドポイントにクエリ
    """
    
    def __init__(self, dataset_info: Dict[str, Any]):
        """
        Args:
            dataset_info: データセット情報（url を含む）
        """
        self.dataset_info = dataset_info
        self.endpoint_url = dataset_info.get("url")
        
        if not self.endpoint_url:
            raise ValueError("エンドポイントデータソースに url が指定されていません")
        
        self.sparql = SPARQLWrapper(self.endpoint_url)
        self.sparql.setReturnFormat(JSON)
    
    def query(self, sparql_query: str) -> List[Dict[str, Any]]:
        """
        SPARQLクエリを実行
        
        Args:
            sparql_query: SPARQL クエリ文字列
            
        Returns:
            クエリ結果のリスト
        """
        try:
            self.sparql.setQuery(sparql_query)
            results = self.sparql.query().convert()
            return self._convert_results(results)
        except Exception as e:
            raise RuntimeError(f"エンドポイント {self.endpoint_url} へのクエリ実行に失敗: {e}")
    
    def _convert_results(self, results: Dict) -> List[Dict[str, Any]]:
        """
        SPARQLWrapper の JSON 結果を辞書リストに変換
        
        Args:
            results: SPARQLWrapper の結果
            
        Returns:
            結果の辞書リスト
        """
        if "results" not in results or "bindings" not in results["results"]:
            return []
        
        converted = []
        for binding in results["results"]["bindings"]:
            row_dict = {}
            for var, value in binding.items():
                row_dict[var] = value.get("value", "")
            converted.append(row_dict)
        return converted
    
    def get_type(self) -> str:
        return "endpoint"


class DataLoader:
    """
    データソースの統合管理クラス
    """
    
    def __init__(self, config_loader: ConfigLoader):
        """
        Args:
            config_loader: ConfigLoaderインスタンス
        """
        self.config_loader = config_loader
        self.sources_cache = {}
    
    def load_sources_for_pair(self, pair_name: str) -> Dict[str, Union[FileDataSource, EndpointDataSource]]:
        """
        アラインメントペアに必要な全データソースをロード
        
        Args:
            pair_name: アラインメントペア名
            
        Returns:
            データソースの辞書 {dataset_id: DataSource}
        """
        alignment_config = self.config_loader.load_alignment_config(pair_name)
        sources = {}
        
        # ファイルベースのデータセット
        if "datasets" in alignment_config and alignment_config["datasets"]:
            datasets = alignment_config["datasets"]
            
            # 新形式（文字列のリスト）か旧形式（辞書のリスト）かを判定
            if isinstance(datasets, list) and len(datasets) > 0:
                if isinstance(datasets[0], str):
                    # 新形式: datasets_registry.json のIDを参照
                    for dataset_id in datasets:
                        if dataset_id not in self.sources_cache:
                            dataset_info = self.config_loader.get_dataset_info(dataset_id)
                            if dataset_info:
                                source = DataSourceFactory.create_source(dataset_info, self.config_loader)
                                self.sources_cache[dataset_id] = source
                        
                        if dataset_id in self.sources_cache:
                            sources[dataset_id] = self.sources_cache[dataset_id]
                
                elif isinstance(datasets[0], dict):
                    # 旧形式: alignment.json 内に直接定義
                    # この場合は datasets_registry.json を使わず、直接ロード
                    for idx, dataset_dict in enumerate(datasets):
                        cache_key = f"{pair_name}_dataset_{idx}"
                        if cache_key not in self.sources_cache:
                            source = DataSourceFactory.create_source(dataset_dict, self.config_loader)
                            self.sources_cache[cache_key] = source
                        sources[cache_key] = self.sources_cache[cache_key]
        
        # エンドポイントベースのデータセット
        if "endpoints" in alignment_config and alignment_config["endpoints"]:
            for endpoint_id, endpoint_url in alignment_config["endpoints"].items():
                endpoint_key = f"endpoint_{endpoint_id}"
                if endpoint_key not in self.sources_cache:
                    dataset_info = self.config_loader.get_dataset_info(endpoint_key)
                    if dataset_info:
                        source = DataSourceFactory.create_source(dataset_info, self.config_loader)
                        self.sources_cache[endpoint_key] = source
                
                if endpoint_key in self.sources_cache:
                    sources[endpoint_id] = self.sources_cache[endpoint_key]
        
        return sources
