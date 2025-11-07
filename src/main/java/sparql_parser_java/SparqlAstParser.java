package sparql_parser_java;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.apache.jena.query.Query;
import org.apache.jena.query.QueryFactory;
import org.apache.jena.sparql.core.Prologue;
import org.apache.jena.sparql.syntax.Element;
import org.apache.jena.sparql.syntax.ElementWalker;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;

public class SparqlAstParser {

    public static void main(String[] args) throws java.io.IOException {
        if (args.length == 0) {
            System.err.println("Usage: java -cp \".:lib/*\" sparql_parser_java.SparqlAstParser <PATH_TO_SPARQL_FILE>");
            return;
        }
        String filePath = args[0];
        String queryString = new String(Files.readAllBytes(Paths.get(filePath)));

        try {
            // クエリをパース
            Query query = QueryFactory.create(queryString);

            // クエリの主要部分を抽出
            Element queryPattern = query.getQueryPattern();
            Prologue prologue = query.getPrologue();
            
            // Gsonを使ってAST（Element）とPrefixマッピングをJSONに変換
            // カスタムシリアライザを使わないと循環参照でエラーになるため、
            // ここではJenaのオブジェクトを簡略化したMapに変換してからJSONにする
            Gson gson = new GsonBuilder().setPrettyPrinting().create();
            
            // Prefixマッピングを抽出
            Map<String, String> prefixMap = prologue.getPrefixMapping().getNsPrefixMap();

            // クエリパターン（AST）をカスタムのVisitorでMapに変換
            AstVisitor visitor = new AstVisitor();
            ElementWalker.walk(queryPattern, visitor);

            // 結果をまとめる
            ParserOutput output = new ParserOutput(prefixMap, visitor.getAstRoot());

            // JSONとして出力
            System.out.println(gson.toJson(output));

        } catch (Exception e) {
            System.err.println("Error parsing SPARQL query:");
            e.printStackTrace(System.err);
        }
    }
    
    // 出力用のコンテナクラス
    static class ParserOutput {
        Map<String, String> prefixes;
        Object ast;

        ParserOutput(Map<String, String> prefixes, Object ast) {
            this.prefixes = prefixes;
            this.ast = ast;
        }
    }
}