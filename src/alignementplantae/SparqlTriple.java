/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package alignementplantae;

import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *
 * @author Administrateur
 */
public class SparqlTriple {
    private String subject;
    private String object;
    private String predicate;
    private ArrayList <String> targetTriples;
    
    public SparqlTriple(String su, String pr, String ob){
        this.subject=su;
        this.object=ob;
        this.predicate=pr;
        targetTriples = new ArrayList<String>();
    }
    
    public SparqlTriple(String triple){
    	Pattern pattern1 = Pattern.compile("([^ ^\\t^\\\\{]+)\\+?[ \\t]+([^ ^\\t]+)\\+?[ \\t]+([^\\.^ ]+)[ \\t]?\\.");
		Matcher matcher1 = pattern1.matcher(triple);
		if(matcher1.find()) {
			this.subject =matcher1.group(1);
			this.predicate = matcher1.group(2);
			this.object=matcher1.group(3);
		}
		targetTriples = new ArrayList<String>();
    }

    public boolean inSparqlTriple(String uri){
        return this.getSubject().contains(uri) || this.getObject().contains(uri) ||this.getPredicate().contains(uri);
    }
    
    public void addTargetTriple(String targetTriple) {
    	this.targetTriples.add(targetTriple);
    }

    public boolean hasTargetTriple() {
    	return !this.targetTriples.isEmpty();
    }
    
    public ArrayList<String> getTargetTriples(){
    	return this.targetTriples;
    }
    
    public void printTargetTriples() {
    	for(String t:targetTriples) {
    		System.out.println(t);
    	}
    }
    /**
     * @return the subject
     */
    public String getSubject() {
        return subject;
    }

    /**
     * @return the object
     */
    public String getObject() {
        return object;
    }

    /**
     * @return the predicate
     */
    public String getPredicate() {
        return predicate;
    }
    
    public String toString(){
        return this.getSubject()+" "+this.getPredicate()+" "+this.getObject()+".";
    }
}
