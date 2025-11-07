package sparql_parser_java;

import org.apache.jena.graph.Node;
import org.apache.jena.graph.Triple;
import org.apache.jena.sparql.core.TriplePath;
import org.apache.jena.sparql.expr.Expr;
import org.apache.jena.sparql.syntax.*;

import java.util.*;

/**
 * JenaのAST (Element) を再帰的に訪問し、
 * JSONにシリアライズ可能なMap/Listの構造に変換するVisitor。
 */
public class AstVisitor implements ElementVisitor {

    private final Stack<Object> stack = new Stack<>();

    public Object getAstRoot() {
        return stack.isEmpty() ? null : stack.peek();
    }

    private Map<String, Object> nodeToMap(Node node) {
        Map<String, Object> map = new LinkedHashMap<>();
        if (node == null) return map;

        if (node.isURI()) {
            map.put("type", "uri");
            map.put("value", node.getURI());
        } else if (node.isLiteral()) {
            map.put("type", "literal");
            map.put("value", node.getLiteralLexicalForm());
            if (node.getLiteralDatatypeURI() != null) {
                map.put("datatype", node.getLiteralDatatypeURI());
            }
            if (node.getLiteralLanguage() != null && !node.getLiteralLanguage().isEmpty()) {
                map.put("lang", node.getLiteralLanguage());
            }
        } else if (node.isVariable()) {
            map.put("type", "variable");
            map.put("value", node.getName());
        } else if (node.isBlank()) {
            map.put("type", "blank");
            map.put("value", node.getBlankNodeId().toString());
        } else {
            map.put("type", "unknown");
            map.put("value", node.toString());
        }
        return map;
    }
    
    private Map<String, Object> tripleToMap(Triple triple) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("type", "triple");
        map.put("subject", nodeToMap(triple.getSubject()));
        map.put("predicate", nodeToMap(triple.getPredicate()));
        map.put("object", nodeToMap(triple.getObject()));
        return map;
    }

    @Override
    public void visit(ElementTriplesBlock el) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("type", "bgp"); // Basic Graph Pattern
        List<Object> triples = new ArrayList<>();
        for (Triple triple : el.getPattern()) {
            triples.add(tripleToMap(triple));
        }
        map.put("triples", triples);
        stack.push(map);
    }

    @Override
    public void visit(ElementFilter el) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("type", "filter");
        // Exprの変換は複雑なので、ここでは単純にtoString()で表現
        map.put("expression", el.getExpr().toString());
        stack.push(map);
    }

    @Override
    public void visit(ElementGroup el) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("type", "group");
        List<Object> patterns = new ArrayList<>();
        for (Element element : el.getElements()) {
            element.visit(this);
            patterns.add(stack.pop());
        }
        map.put("patterns", patterns);
        stack.push(map);
    }

    // --- 他のElementタイプのvisitメソッドも同様に実装 ---
    // 今回のサンプルクエリでは上記3つが主ですが、網羅性を高めるために追加します。

    @Override
    public void visit(ElementUnion el) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("type", "union");
        List<Object> patterns = new ArrayList<>();
        for (Element element : el.getElements()) {
            element.visit(this);
            patterns.add(stack.pop());
        }
        map.put("patterns", patterns);
        stack.push(map);
    }

    @Override
    public void visit(ElementOptional el) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("type", "optional");
        el.getOptionalElement().visit(this);
        map.put("pattern", stack.pop());
        stack.push(map);
    }

    @Override
    public void visit(ElementPathBlock el) {
        // ElementTriplesBlockと同様に、個々のトリプルパスを構造化する
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("type", "bgp"); // BGP (Basic Graph Pattern) として扱う
        List<Object> triples = new ArrayList<>();
        for (TriplePath triplePath : el.getPattern()) {
            // TriplePathをTripleに変換して処理 (単純なケース)
            if (triplePath.isTriple()) {
                triples.add(tripleToMap(triplePath.asTriple()));
            } else {
                // 複雑なパス（例: a/b*|c）は、ここでは単純にtoString()で表現
                Map<String, Object> pathMap = new LinkedHashMap<>();
                pathMap.put("type", "path");
                pathMap.put("subject", nodeToMap(triplePath.getSubject()));
                pathMap.put("path", triplePath.getPath().toString());
                pathMap.put("object", nodeToMap(triplePath.getObject()));
                triples.add(pathMap);
            }
        }
        map.put("triples", triples);
        stack.push(map);
    }

    // 以下、今回は利用しないがインターフェースとして必要なメソッド
    @Override public void visit(ElementData el) { stack.push(Collections.singletonMap("type", "data")); }
    @Override public void visit(ElementDataset el) { stack.push(Collections.singletonMap("type", "dataset")); }
    @Override public void visit(ElementNamedGraph el) { stack.push(Collections.singletonMap("type", "namedgraph")); }
    @Override public void visit(ElementExists el) { stack.push(Collections.singletonMap("type", "exists")); }
    @Override public void visit(ElementNotExists el) { stack.push(Collections.singletonMap("type", "notexists")); }
    @Override public void visit(ElementMinus el) { stack.push(Collections.singletonMap("type", "minus")); }
    @Override public void visit(ElementService el) { stack.push(Collections.singletonMap("type", "service")); }
    @Override public void visit(ElementSubQuery el) { stack.push(Collections.singletonMap("type", "subquery")); }
    @Override public void visit(ElementAssign el) { stack.push(Collections.singletonMap("type", "assign")); }
    @Override public void visit(ElementBind el) { stack.push(Collections.singletonMap("type", "bind")); }
    @Override public void visit(ElementLateral el) { stack.push(Collections.singletonMap("type", "lateral")); }
}