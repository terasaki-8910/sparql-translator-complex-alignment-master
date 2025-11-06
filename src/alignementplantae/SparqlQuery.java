/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package alignementplantae;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *
 * @author Administrateur
 */
public class SparqlQuery {
	private ArrayList<SparqlTriple> triples;

	private String queryTemplate;


	//TODO use regex pattern and matcher to get all types of queries, query template and set of triples
	public SparqlQuery(String query){
		query=query.replaceAll("prefix", "PREFIX");
		Pattern pattern0 = Pattern.compile("PREFIX(.+):[ ]*<([^>]+)>");
		Matcher matcher0 = pattern0.matcher(query);
		HashMap<String,String> prefixes = new HashMap<String,String>();
		while  (matcher0.find()){ 
			//System.out.println(matcher0.group());
			prefixes.put(matcher0.group(1).trim(),matcher0.group(2));
		}
		query=query.replaceAll("PREFIX(.+):[ ]*<([^>]+)>", "");
		for(String key :prefixes.keySet()) {
			query = query.replaceAll(key+":([A-Za-z0-9_-]+)", "<"+prefixes.get(key)+"$1>");
		}
		triples= new ArrayList<SparqlTriple>();
		queryTemplate=query;
		Pattern pattern1 = Pattern.compile("([^ ^\\t^\\\\{]+)\\+?[ \\t]+([^ ^\\t]+)\\+?[ \\t]+([^\\.^ ]+)[ \\t]?\\.");
		Matcher matcher1 = pattern1.matcher(query);
		int index=0;
		while(matcher1.find()) {
			SparqlTriple triple= new SparqlTriple(matcher1.group(1),matcher1.group(2),matcher1.group(3));
			queryTemplate=queryTemplate.replaceAll(matcher1.group().replaceAll("\\?", "\\\\?"), "{{triple"+index+"}}");
			triples.add(triple);
			index ++;
		}
		//System.out.println(queryTemplate);
		//printTriples();
	}

	public ArrayList<String> toTargetQuery() {
		ArrayList<String> result = new ArrayList<String>();
		result.add(queryTemplate);
		for(int i =0; i < triples.size();i++) {
			//triples.get(i).printTargetTriples();
			int initialSize = result.size();
			if (triples.get(i).hasTargetTriple()) {
				for (int k=0; k < initialSize;k++) {
					String res = result.get(k);
					for(int j =0; j < triples.get(i).getTargetTriples().size();j++) {
						result.add(res.replaceAll("\\{\\{triple"+i+"\\}\\}", triples.get(i).getTargetTriples().get(j)));
					}        				
				}
				for (int k=0; k < initialSize;k++) {
					result.remove(0);       				
				}

			}
			else {
				for (int k=0; k < initialSize;k++) {
					String res = result.get(k).replaceAll("\\{\\{triple"+i+"\\}\\}", triples.get(i).toString());
					result.add(res);
				}
				for (int k=0; k < initialSize;k++) {
					result.remove(0);       				
				}
			}
		}
		return result;
	}

	public void printTriples() {
		for(SparqlTriple t: triples) {
			System.out.println(t.toString());
		}
	}

	/**
	 * @return the list of triples
	 */
	public ArrayList<SparqlTriple> getTriples() {
		return triples;
	}

}
