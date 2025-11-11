import subprocess
import json
import os

class AstSerializer:
    """
    Javaで実装されたSPARQLシリアライザーを呼び出し、
    書き換え後のJSON ASTをSPARQLクエリ文字列に変換するラッパー。
    """

    def __init__(self, project_root: str = None):
        """
        プロジェクトのルートディレクトリを初期化時に受け取る。
        
        :param project_root: プロジェクトのルートディレクトリへのパス。
                            Noneの場合は、このファイルから相対的に推測する。
        """
        if project_root is None:
            # このファイルの場所からプロジェクトルートを推測
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
        else:
            self.project_root = project_root
        
        self.gradlew_path = os.path.join(self.project_root, 'gradlew')

    def serialize(self, ast: dict) -> str:
        """
        書き換え後のJSON ASTをSPARQLクエリ文字列に変換する。

        :param ast: 書き換え後のJSON AST（辞書形式）
        :return: シリアライズされたSPARQLクエリ文字列
        :raises RuntimeError: Javaプログラムの実行に失敗した場合
        """
        # ASTをJSON文字列に変換
        ast_json_string = json.dumps(ast)

        # Javaプログラムを実行するためのコマンドを構築
        command = [
            self.gradlew_path,
            'runSerializer',
            '--quiet',  # Gradleのログを抑制
            '--console=plain'
        ]

        try:
            # サブプロセスとしてJavaプログラムを実行し、ASTをstdinに渡す
            result = subprocess.run(
                command,
                cwd=self.project_root,
                input=ast_json_string,
                capture_output=True,
                text=True,
                check=True
            )

            # 標準出力からSPARQLクエリ文字列を取得
            output_str = result.stdout.strip()
            
            if not output_str:
                raise RuntimeError("Java serializer returned empty output.")
            
            return output_str

        except subprocess.CalledProcessError as e:
            # Javaプログラムがエラーを返した場合
            error_message = f"SPARQL AST Serializer (Java) failed with exit code {e.returncode}.\n"
            error_message += f"Stderr:\n{e.stderr}\n"
            error_message += f"Stdout:\n{e.stdout}"
            raise RuntimeError(error_message)
        except FileNotFoundError:
            raise RuntimeError(f"Could not find gradlew executable at {self.gradlew_path}. "
                             "Ensure the project root is correct and Gradle wrapper is set up.")


if __name__ == '__main__':
    # このモジュールを直接実行した場合のテスト用コード
    import pprint
    
    # テスト用の書き換え済みAST
    test_ast = {
        'prefixes': {
            '': 'http://ekaw#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        },
        'ast': {
            'type': 'group',
            'patterns': [
                {
                    'type': 'bgp',
                    'triples': [
                        {
                            'type': 'triple',
                            'subject': {'type': 'variable', 'value': 'paper'},
                            'predicate': {'type': 'uri', 'value': 'http://cmt#readByReviewer'},
                            'object': {'type': 'variable', 'value': 'reviewer'}
                        },
                        {
                            'type': 'triple',
                            'subject': {'type': 'variable', 'value': 'paper'},
                            'predicate': {'type': 'uri', 'value': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                            'object': {'type': 'uri', 'value': 'http://cmt#Paper'}
                        }
                    ]
                }
            ]
        },
        'queryType': 'SELECT',
        'isDistinct': False,
        'selectVariables': ['reviewer'],
        'orderBy': [],
        'limit': None,
        'offset': None
    }

    print("--- Input AST ---")
    pprint.pprint(test_ast)

    # このファイルの場所からプロジェクトルートを特定
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))

    try:
        serializer = AstSerializer(project_root)
        sparql_query = serializer.serialize(test_ast)
        
        print("\n--- Serialized SPARQL Query ---")
        print(sparql_query)
        
    except RuntimeError as e:
        print(f"\n--- An error occurred ---")
        print(e)
