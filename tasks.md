ast_serializer.py
このタスクをJenaを使って行い、その結果をPythonで受け取るように変更する。
緊急: SELECT句を動的に変更する必要がある。現在は?rankで仮置きしているが、これを元のクエリ、現在のクエリと整合性が取れる形に変更する必要がある
query_string += "\nSELECT ?rank WHERE {\n" # TODO: SELECT句を動的に構築
