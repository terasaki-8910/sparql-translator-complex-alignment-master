package sparql_serializer_java;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import org.apache.jena.graph.Node;
import org.apache.jena.graph.NodeFactory;
import org.apache.jena.graph.Triple;
import org.apache.jena.query.Query;
import org.apache.jena.query.QueryFactory;
import org.apache.jena.query.SortCondition;
import org.apache.jena.sparql.core.Var;
import org.apache.jena.sparql.expr.Expr;
import org.apache.jena.sparql.expr.ExprVar;
import org.apache.jena.sparql.syntax.*;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * JSON AST（書き換え済み）を標準入力から読み取り、
 * Jena Queryオブジェクトを再構築してSPARQL文字列として標準出力に書き出す。
 */
public class SparqlAstSerializer {

    public static void main(String[] args) {
        try {
            // 標準入力からJSON ASTを読み取る
            BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
            StringBuilder jsonBuilder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                jsonBuilder.append(line);
            }
            String jsonString = jsonBuilder.toString();

            // JSONをパース
            Gson gson = new Gson();
            JsonObject astJson = gson.fromJson(jsonString, JsonObject.class);

            // Queryオブジェクトを再構築
            Query query = reconstructQuery(astJson);

            // SPARQL文字列として出力
            System.out.println(query.serialize());

        } catch (Exception e) {
            System.err.println("Error serializing AST to SPARQL:");
            e.printStackTrace(System.err);
            System.exit(1);
        }
    }

    /**
     * JSON ASTからJena Queryオブジェクトを再構築する
     */
    private static Query reconstructQuery(JsonObject astJson) {
        Query query = QueryFactory.create();

        // Prefixマッピングを設定
        if (astJson.has("prefixes")) {
            JsonObject prefixes = astJson.getAsJsonObject("prefixes");
            for (Map.Entry<String, JsonElement> entry : prefixes.entrySet()) {
                query.setPrefix(entry.getKey(), entry.getValue().getAsString());
            }
        }

        // クエリタイプを設定
        String queryType = astJson.has("queryType") ? astJson.get("queryType").getAsString() : "SELECT";
        switch (queryType) {
            case "SELECT":
                query.setQuerySelectType();
                break;
            case "CONSTRUCT":
                query.setQueryConstructType();
                break;
            case "DESCRIBE":
                query.setQueryDescribeType();
                break;
            case "ASK":
                query.setQueryAskType();
                break;
        }

        // DISTINCT フラグを設定
        if (astJson.has("isDistinct") && astJson.get("isDistinct").getAsBoolean()) {
            query.setDistinct(true);
        }

        // SELECT変数を設定
        if (astJson.has("selectVariables")) {
            JsonArray selectVars = astJson.getAsJsonArray("selectVariables");
            for (JsonElement varElement : selectVars) {
                query.addResultVar(varElement.getAsString());
            }
        }

        // WHERE句（ASTパターン）を設定
        if (astJson.has("ast")) {
            JsonObject astNode = astJson.getAsJsonObject("ast");
            Element whereClause = reconstructElement(astNode);
            query.setQueryPattern(whereClause);
        }

        // ORDER BY を設定
        if (astJson.has("orderBy") && astJson.getAsJsonArray("orderBy").size() > 0) {
            JsonArray orderByArray = astJson.getAsJsonArray("orderBy");
            for (JsonElement orderElement : orderByArray) {
                String orderStr = orderElement.getAsString();
                // "(SortCondition ?var)" のような文字列から変数名を抽出
                // 簡易実装: ?で始まる変数名を抽出
                if (orderStr.contains("?")) {
                    String varName = orderStr.substring(orderStr.indexOf("?") + 1);
                    varName = varName.replaceAll("[^a-zA-Z0-9_]", ""); // 記号を除去
                    Expr expr = new ExprVar(varName);
                    query.addOrderBy(expr, Query.ORDER_ASCENDING);
                }
            }
        }

        // LIMIT を設定
        if (astJson.has("limit") && !astJson.get("limit").isJsonNull()) {
            query.setLimit(astJson.get("limit").getAsLong());
        }

        // OFFSET を設定
        if (astJson.has("offset") && !astJson.get("offset").isJsonNull()) {
            query.setOffset(astJson.get("offset").getAsLong());
        }

        return query;
    }

    /**
     * JSON ASTのノードからJena Elementを再構築する（再帰的）
     */
    private static Element reconstructElement(JsonObject node) {
        String type = node.has("type") ? node.get("type").getAsString() : "";

        switch (type) {
            case "group":
                return reconstructGroup(node);
            case "bgp":
                return reconstructBGP(node);
            case "union":
                return reconstructUnion(node);
            case "optional":
                return reconstructOptional(node);
            case "filter":
                return reconstructFilter(node);
            default:
                // 未対応のノードタイプは空のグループを返す
                return new ElementGroup();
        }
    }

    /**
     * グループノードを再構築
     */
    private static ElementGroup reconstructGroup(JsonObject node) {
        ElementGroup group = new ElementGroup();
        if (node.has("patterns")) {
            JsonArray patterns = node.getAsJsonArray("patterns");
            for (JsonElement patternElement : patterns) {
                if (patternElement.isJsonObject()) {
                    Element element = reconstructElement(patternElement.getAsJsonObject());
                    group.addElement(element);
                }
            }
        }
        return group;
    }

    /**
     * BGP (Basic Graph Pattern) ノードを再構築
     */
    private static ElementTriplesBlock reconstructBGP(JsonObject node) {
        ElementTriplesBlock triplesBlock = new ElementTriplesBlock();
        if (node.has("triples")) {
            JsonArray triples = node.getAsJsonArray("triples");
            for (JsonElement tripleElement : triples) {
                if (tripleElement.isJsonObject()) {
                    Triple triple = reconstructTriple(tripleElement.getAsJsonObject());
                    triplesBlock.addTriple(triple);
                }
            }
        }
        return triplesBlock;
    }

    /**
     * UNIONノードを再構築
     */
    private static ElementUnion reconstructUnion(JsonObject node) {
        ElementUnion union = new ElementUnion();
        if (node.has("patterns")) {
            JsonArray patterns = node.getAsJsonArray("patterns");
            for (JsonElement patternElement : patterns) {
                if (patternElement.isJsonObject()) {
                    Element element = reconstructElement(patternElement.getAsJsonObject());
                    union.addElement(element);
                }
            }
        }
        return union;
    }

    /**
     * OPTIONALノードを再構築
     */
    private static ElementOptional reconstructOptional(JsonObject node) {
        if (node.has("pattern")) {
            Element optElement = reconstructElement(node.getAsJsonObject("pattern"));
            return new ElementOptional(optElement);
        }
        return new ElementOptional(new ElementGroup());
    }

    /**
     * FILTERノードを再構築
     */
    private static ElementFilter reconstructFilter(JsonObject node) {
        // FILTER の式は複雑なため、ここでは文字列として保存されたものを使用
        // 実際には、式を完全に再構築する必要があるが、簡易実装として文字列パースを試みる
        if (node.has("expression")) {
            String exprString = node.get("expression").getAsString();
            // TODO: 式の完全な再構築が必要な場合はここを拡張
            // 現状はJenaのパーサーを利用して簡易的に処理
            try {
                // ダミーのQueryを作成して式をパース
                String dummyQuery = "SELECT * WHERE { FILTER(" + exprString + ") }";
                Query q = QueryFactory.create(dummyQuery);
                Element pattern = q.getQueryPattern();
                // パターンからFILTERを抽出
                if (pattern instanceof ElementGroup) {
                    ElementGroup eg = (ElementGroup) pattern;
                    for (Element e : eg.getElements()) {
                        if (e instanceof ElementFilter) {
                            return (ElementFilter) e;
                        }
                    }
                }
            } catch (Exception e) {
                System.err.println("Warning: Could not parse FILTER expression: " + exprString);
            }
        }
        // パースできなかった場合はダミーのFILTERを返す
        return new ElementFilter(new ExprVar("dummy"));
    }

    /**
     * トリプルを再構築
     */
    private static Triple reconstructTriple(JsonObject tripleNode) {
        Node subject = reconstructNode(tripleNode.getAsJsonObject("subject"));
        Node predicate = reconstructNode(tripleNode.getAsJsonObject("predicate"));
        Node object = reconstructNode(tripleNode.getAsJsonObject("object"));
        return new Triple(subject, predicate, object);
    }

    /**
     * ノード（主語、述語、目的語）を再構築
     */
    private static Node reconstructNode(JsonObject nodeJson) {
        String type = nodeJson.has("type") ? nodeJson.get("type").getAsString() : "";
        String value = nodeJson.has("value") ? nodeJson.get("value").getAsString() : "";

        switch (type) {
            case "uri":
                return NodeFactory.createURI(value);
            case "variable":
                return Var.alloc(value).asNode();
            case "literal":
                // リテラルの完全な処理（言語タグ、データタイプ）
                if (nodeJson.has("datatype")) {
                    String datatype = nodeJson.get("datatype").getAsString();
                    return NodeFactory.createLiteral(value, NodeFactory.getType(datatype));
                } else if (nodeJson.has("language")) {
                    String language = nodeJson.get("language").getAsString();
                    return NodeFactory.createLiteral(value, language);
                } else {
                    return NodeFactory.createLiteral(value);
                }
            default:
                // デフォルトは変数として扱う
                return Var.alloc("unknown").asNode();
        }
    }
}
