/*
 * $Id: EDOALAlignment.java 1996 2014-11-23 16:30:55Z euzenat $
 *
 * Sourceforge version 1.6 - 2008 - was OMWGAlignment
 * Copyright (C) INRIA, 2007-2014
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation; either version 2.1 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 */

package fr.inrialpes.exmo.align.impl.edoal;

import alignementplantae.SparqlQuery;
import alignementplantae.SparqlTriple;
import java.util.Hashtable;
import java.util.Collection;
import java.util.Set;
import java.util.Map.Entry;
import java.net.URI;


import org.semanticweb.owl.align.AlignmentException;
import org.semanticweb.owl.align.Alignment;
import org.semanticweb.owl.align.Cell;
import org.semanticweb.owl.align.Relation;

import fr.inrialpes.exmo.ontowrap.Ontology;
import fr.inrialpes.exmo.ontowrap.LoadedOntology;
import fr.inrialpes.exmo.ontowrap.OntologyFactory;
import fr.inrialpes.exmo.ontowrap.OntowrapException;
import fr.inrialpes.exmo.align.impl.Annotations;
import fr.inrialpes.exmo.align.impl.Namespace;
import fr.inrialpes.exmo.align.impl.BasicAlignment;
import fr.inrialpes.exmo.align.impl.URIAlignment;
import fr.inrialpes.exmo.align.impl.ObjectAlignment;
import fr.inrialpes.exmo.align.impl.Extensions;
import fr.inrialpes.exmo.align.parser.SyntaxElement;
import fr.inrialpes.exmo.align.parser.SyntaxElement.Constructor;

import fr.inrialpes.exmo.align.parser.TypeCheckingVisitor;
import java.util.ArrayList;

/**
 * An alignment between complex expressions built from the elements of two ontologies
 * JE2014: Should be better an extension of ObjectAlignment (so far breaks tests)
 */

public class EDOALAlignment extends BasicAlignment {
	// final static Logger logger = LoggerFactory.getLogger( EDOALAlignment.class );
	/*
	 * An eventual initial alignment
	 *
	 */
	protected EDOALAlignment init = null;

	/*
	 * The list of variables declared in this alignment
	 * //EDOALPattern
	 */
	protected Hashtable<String,Variable> variables;

	public EDOALAlignment() {
		this.setLevel("2EDOAL");
		this.setXNamespace( Namespace.EDOAL.shortCut, Namespace.EDOAL.prefix );
		variables = new Hashtable<String,Variable>();
	}

	public void accept( TypeCheckingVisitor visitor ) throws AlignmentException {
		visitor.visit(this);
	}


	public void init( Object onto1, Object onto2 ) throws AlignmentException {
		if ( (onto1 == null) || (onto2 == null) )
			throw new AlignmentException("The source and target ontologies must not be null");
		Object o1 = null;
		if ( onto1 instanceof Ontology<?> ) o1 = onto1;
		else o1 = loadOntology( (URI)onto1 ); // W:[unchecked]
		Object o2 = null;
		if ( onto2 instanceof Ontology<?> ) o2 = onto2;
		else o2 = loadOntology( (URI)onto2 ); // W:[unchecked]
		super.init( o1, o2 );
	}

	public void loadInit( Alignment al ) throws AlignmentException {
		if ( al instanceof EDOALAlignment ) {
			init = (EDOALAlignment)al;
		} else {
			throw new AlignmentException( "EDOAL required as initial alignment");
		}
	}

	/*
	 * Dealing with variables
	 */

	public Variable recordVariable( String name, Expression expr ) {
		Variable var = variables.get( name );
		if ( var == null ) {
			var = new Variable( name );
			variables.put( name, var );
		}
		var.addOccurence( expr );
		return var;
	}

	/*
	 * Dealing with correspondences
	 */

	/** Cell methods **/
	public Cell addAlignCell( EDOALCell rule ) throws AlignmentException {
		addCell( rule );
		return rule;
	}

	public Cell addAlignCell(String id, Object ob1, Object ob2, Relation relation, double measure, Extensions extensions ) throws AlignmentException {
		if ( !( ob1 instanceof Expression && ob2 instanceof Expression ) )
			throw new AlignmentException("arguments must be Expressions");
		return super.addAlignCell( id, ob1, ob2, relation, measure, extensions);
	};
	public Cell addAlignCell(String id, Object ob1, Object ob2, Relation relation, double measure) throws AlignmentException {
		if ( !( ob1 instanceof Expression && ob2 instanceof Expression ) )
			throw new AlignmentException("arguments must be Expressions");
		return super.addAlignCell( id, ob1, ob2, relation, measure);
	};
	public Cell addAlignCell(Object ob1, Object ob2, String relation, double measure) throws AlignmentException {

		if ( !( ob1 instanceof Expression && ob2 instanceof Expression ) )
			throw new AlignmentException("arguments must be Expressions");
		return super.addAlignCell( ob1, ob2, relation, measure);
	};
	public Cell addAlignCell(Object ob1, Object ob2) throws AlignmentException {

		if ( !( ob1 instanceof Expression && ob2 instanceof Expression ) )
			throw new AlignmentException("arguments must be Expressions");
		return super.addAlignCell( ob1, ob2 );
	};
	public Cell createCell(String id, Object ob1, Object ob2, Relation relation, double measure) throws AlignmentException {
		return (Cell)new EDOALCell( id, (Expression)ob1, (Expression)ob2, relation, measure);
	}

	public Set<Cell> getAlignCells1(Object ob) throws AlignmentException {
		if ( ob instanceof Expression ){
			return super.getAlignCells1( ob );
		} else {
			throw new AlignmentException("argument must be Expression");
		}
	}
	public Set<Cell> getAlignCells2(Object ob) throws AlignmentException {
		if ( ob instanceof Expression ){
			return super.getAlignCells2( ob );
		} else {
			throw new AlignmentException("argument must be Expression");
		}
	}

	// Deprecated: implement as the one retrieving the highest strength correspondence (
	public Cell getAlignCell1(Object ob) throws AlignmentException {
		if ( Annotations.STRICT_IMPLEMENTATION == true ){
			throw new AlignmentException("deprecated (use getAlignCells1 instead)");
		} else {
			if ( ob instanceof Expression ){
				return super.getAlignCell1( ob );
			} else {
				throw new AlignmentException("argument must be Expression");
			}
		}
	}

	public Cell getAlignCell2(Object ob) throws AlignmentException {
		if ( Annotations.STRICT_IMPLEMENTATION == true ){
			throw new AlignmentException("deprecated (use getAlignCells2 instead)");
		} else {
			if ( ob instanceof Expression ){
				return super.getAlignCell2( ob );
			} else {
				throw new AlignmentException("argument must be Expression");
			}
		}
	}

	/*
	 * Dealing with ontology Ids from an Alignment API standpoint
	 */
	public URI getOntology1URI() { return onto1.getURI(); };

	public URI getOntology2URI() { return onto2.getURI(); };

	public void setOntology1(Object ontology) throws AlignmentException {
		if ( ontology instanceof Ontology ){
			super.setOntology1( ontology );
		} else {
			throw new AlignmentException("arguments must be Ontology");
		};
	};

	public void setOntology2(Object ontology) throws AlignmentException {
		if ( ontology instanceof Ontology ){
			super.setOntology2( ontology );
		} else {
			throw new AlignmentException("arguments must be Ontology");
		};
	};



	/**
	 * Transform Alignment into OWLable Alignment 
	 * Relation or Property Constructions with AND, OR, NOT are not processed in OWL :
	 *  transformation of EDOAL before OWL transformation
	 */    
	public void transformAlignmentToBeOWLable() throws AlignmentException{
		String subsumes = "Subsumes";
		String subsumed = "SubsumedBy";
		String disjoint = "DisjointFrom";
		System.out.println("transformAlignment");
		/* System.out.println(this.nbCells());
        for (Cell c : this){
            System.out.println(c);
        }*/
		ArrayList<Cell> cellsToRemove = new ArrayList<Cell> ();
		for (Cell c : this){
			Object ob1 = c.getObject1();
			Object ob2 = c.getObject2();
			System.out.println(ob1+ " -- "+ob2);
			if (ob1 instanceof RelationConstruction){
				// And(ob11, ob12, ob13...) = ob2 --> ob2 <ob11, ob2 < ob12, ob2 <ob13, etc.
				if(((RelationConstruction) ob1).getOperator() == Constructor.AND){
					for (PathExpression p : ((RelationConstruction) ob1).getComponents()){
						this.addAlignCell(p, ob2, subsumes, c.getStrength());
					}
					cellsToRemove.add(c);
				}
				// OR (ob11, ob12, ob13, ...) = ob2 --> ob2 > ob11, ob2 > ob12 ...
				else if(((RelationConstruction) ob1).getOperator() == Constructor.OR){
					for (PathExpression p : ((RelationConstruction) ob1).getComponents()){
						this.addAlignCell(p, ob2, subsumed, c.getStrength());
					}
					cellsToRemove.add(c);;
				}
				// NOT(ob1) = ob2 --> ob2 disjoint ob1
				else if(((RelationConstruction) ob1).getOperator() == Constructor.NOT){
					for (PathExpression p : ((RelationConstruction) ob1).getComponents()){
						this.addAlignCell(p, ob2, disjoint, c.getStrength());
					}
					cellsToRemove.add(c);
				}
			}
			else if (ob2 instanceof RelationConstruction){
				// ob1 = AND(ob21, ob22,...) --> ob1 <ob21, ob1 < ob22, ...
				if(((RelationConstruction) ob2).getOperator() == Constructor.AND){
					for (PathExpression p : ((RelationConstruction) ob2).getComponents()){
						this.addAlignCell(p, ob1, subsumes, c.getStrength());
					}
					cellsToRemove.add(c);
				}
				// ob1 = OR(ob21, ob22, ...) --> ob1 > ob21, ob1 > ob22 ...
				else if(((RelationConstruction) ob2).getOperator() == Constructor.OR){
					for (PathExpression p : ((RelationConstruction) ob2).getComponents()){
						this.addAlignCell(p, ob1, subsumed, c.getStrength());
					}
					cellsToRemove.add(c);
				}
				// ob1 = NOT(ob2) --> ob2 disjoint ob1
				else if(((RelationConstruction) ob2).getOperator() == Constructor.NOT){
					for (PathExpression p : ((RelationConstruction) ob2).getComponents()){
						this.addAlignCell(p, ob1, disjoint, c.getStrength());
					}
					cellsToRemove.add(c);
				}
			}
			else if (ob1 instanceof PropertyConstruction){
				// And(ob11, ob12, ob13...) = ob2 --> ob2 <ob11, ob2 < ob12, ob2 <ob13, etc.
				if(((PropertyConstruction) ob1).getOperator() == Constructor.AND){
					for (PathExpression p : ((PropertyConstruction) ob1).getComponents()){
						this.addAlignCell(p, ob2, subsumes, c.getStrength());
					}
					cellsToRemove.add(c);
				}
				// OR (ob11, ob12, ob13, ...) = ob2 --> ob2 > ob11, ob2 > ob12 ...
				else if(((PropertyConstruction) ob1).getOperator() == Constructor.OR){
					for (PathExpression p : ((PropertyConstruction) ob1).getComponents()){
						this.addAlignCell(p, ob2, subsumed, c.getStrength());
					}
					cellsToRemove.add(c);
				}
				else if(((PropertyConstruction) ob1).getOperator() == Constructor.COMP){
					cellsToRemove.add(c);
				}
			}
			else if (ob2 instanceof PropertyConstruction){
				// ob1 = AND(ob21, ob22,...) --> ob1 <ob21, ob1 < ob22, ...
				if(((PropertyConstruction) ob2).getOperator() == Constructor.AND){
					for (PathExpression p : ((PropertyConstruction) ob2).getComponents()){
						this.addAlignCell(p, ob1, subsumes, c.getStrength());
					}
					cellsToRemove.add(c);
				}
				// ob1 = OR(ob21, ob22, ...) --> ob1 > ob21, ob1 > ob22 ...
				else if(((PropertyConstruction) ob2).getOperator() == Constructor.OR){
					for (PathExpression p : ((PropertyConstruction) ob2).getComponents()){
						this.addAlignCell(p, ob1, subsumed, c.getStrength());
					}
					cellsToRemove.add(c);
				}
				else if(((PropertyConstruction) ob2).getOperator() == Constructor.COMP){
					cellsToRemove.add(c);
				}
			}
		}    
		for (Cell c : cellsToRemove){
			this.remCell(c);
		}
		if(!cellsToRemove.isEmpty()){
			this.transformAlignmentToBeOWLable();
		}
		//System.out.println("YOL2BITCH");
	}

	/**
	 * This is a clone with the URI instead of Object objects
	 * This conversion will drop any correspondences using something not identified by an URI
	 * For converting to ObjectAlignment, first convert to URIAlignment and load as an ObjectAlignment
	 * The same code as for ObjectAlignment works...
	 */
	public URIAlignment toURIAlignment() throws AlignmentException {
		return toURIAlignment( false );
	}
	public URIAlignment toURIAlignment( boolean strict ) throws AlignmentException {
		URIAlignment align = new URIAlignment();
		align.init( getOntology1URI(), getOntology2URI() );
		align.setType( getType() );
		align.setLevel( getLevel() );
		align.setFile1( getFile1() );
		align.setFile2( getFile2() );
		align.setExtensions( extensions.convertExtension( "EDOALURIConverted", "http://exmo.inrialpes.fr/align/impl/edoal/EDOALAlignment#toURI" ) );
		for ( Cell c : this ) {
			try {
				align.addAlignCell( c.getId(), c.getObject1AsURI(this), c.getObject2AsURI(this), c.getRelation(), c.getStrength() );
			} catch (AlignmentException aex) {
				// Ignore every cell that does not work
				if ( strict ) {
					throw new AlignmentException( "Cannot convert to URIAlignment" );
				}
			}
		};
		return align;
	}

	/**
	 * convert an URI alignment into a corresponding EDOALAlignment
	 * The same could be implemented for ObjectAlignent if necessary
	 */
	// This works for any BasicAlignment but will return an empty
	// alignment if they do not have proper URI dereferencing.
	// It would be better to implement this for ObjectAlignment
	// and to use return toEDOALAlignment( ObjectAlignment.toObjectAlignment( al ) );
	// for URIAlignment
	//
	// Basic -> URI
	//       -> Object
	//       -> EDOAL
	public static LoadedOntology<? extends Object> loadOntology( URI onto ) throws AlignmentException {
		if ( onto == null ) throw new AlignmentException("The source and target ontologies must not be null");
		try {
			OntologyFactory fact = OntologyFactory.getFactory();
			return fact.loadOntology( onto );
		} catch ( OntowrapException owex ) {
			throw new AlignmentException( "Cannot load ontologies", owex );
		}
	}
	public static LoadedOntology<? extends Object> loadOntology( Ontology<Object> onto ) throws AlignmentException {
		if ( onto == null ) throw new AlignmentException("The source and target ontologies must not be null");
		if ( onto instanceof LoadedOntology<?> ) return (LoadedOntology<? extends Object>)onto;
		try {
			OntologyFactory fact = OntologyFactory.getFactory();
			return fact.loadOntology( onto );
		} catch ( OntowrapException owex ) {
			throw new AlignmentException( "Cannot load ontologies", owex );
		}
	}

	public static EDOALAlignment toEDOALAlignment( URIAlignment al ) throws AlignmentException {
		return toEDOALAlignment( (BasicAlignment)al );
	}
	
	public EDOALAlignment inverse() throws AlignmentException {
		EDOALAlignment result = new EDOALAlignment();
		result.init( onto2, onto1 );
		result.setFile1( getFile2() );
		result.setFile2( getFile1() );
		result.setType( invertType() );
		result.setLevel( getLevel() );
		result.setExtensions( extensions.convertExtension( "inverted", "http://exmo.inrialpes.fr/align/impl/BasicAlignment#inverse" ) );
		for ( Entry<Object,Object> e : namespaces.entrySet() ) {
			result.setXNamespace( (String)e.getKey(), (String)e.getValue() );
		}
		for ( Cell c : this ) {
			result.addCell( c.inverse() );
		}
		return (EDOALAlignment)result;
	};

	public static EDOALAlignment toEDOALAlignment( ObjectAlignment al ) throws AlignmentException {
		//logger.debug( "Converting ObjectAlignment to EDOALAlignment" );
		EDOALAlignment alignment = new EDOALAlignment();
		// They are obviously loaded
		alignment.init( al.getOntologyObject1(), al.getOntologyObject2() );
		alignment.convertToEDOAL( al );
		return alignment;
	}

	public static EDOALAlignment toEDOALAlignment( BasicAlignment al ) throws AlignmentException {
		//logger.debug( "Converting BasicAlignment to EDOALAlignment" );
		EDOALAlignment alignment = new EDOALAlignment();
		LoadedOntology<? extends Object> o1 = loadOntology( al.getOntologyObject1() );
		LoadedOntology<? extends Object> o2 = loadOntology( al.getOntologyObject2() );
		alignment.init( o1, o2 );
		alignment.convertToEDOAL( al );
		return alignment;
	}
	/**
	 * The EDOALAlignment has LoadedOntologies as ontologies
	 */
	public void convertToEDOAL( BasicAlignment al ) throws AlignmentException {
		setType( al.getType() );
		setExtensions( al.getExtensionsObject().convertExtension( "toEDOAL", "fr.inrialpes.exmo.align.edoal.EDOALAlignment#toEDOAL" ) );
		LoadedOntology<Object> o1 = (LoadedOntology<Object>)getOntologyObject1(); // [W:unchecked]
		LoadedOntology<Object> o2 = (LoadedOntology<Object>)getOntologyObject2(); // [W:unchecked]
		for ( Cell c : al ) {
			try {
				Cell newc = addAlignCell( c.getId(), 
						createEDOALExpression( o1, c.getObject1AsURI( al ) ),
						createEDOALExpression( o2, c.getObject2AsURI( al ) ),
						c.getRelation(), 
						c.getStrength() );
				Collection<String[]> exts = c.getExtensions();
				if ( exts != null ) {
					for ( String[] ext : exts ){
						newc.setExtension( ext[0], ext[1], ext[2] );
					}
				}
			} catch ( AlignmentException aex ) {
				//		logger.debug( "IGNORED Exception (continue importing)", aex );
			} catch ( OntowrapException owex ) {
				throw new AlignmentException( "Cannot dereference entity", owex );
			}
		}
	}

	private static Id createEDOALExpression( LoadedOntology<Object> o, URI u ) throws OntowrapException, AlignmentException {
		Object e = o.getEntity( u );
		if ( o.isClass( e ) ) {
			return new ClassId( u );
		} else if ( o.isDataProperty( e ) ) {
			return new PropertyId( u );
		} else if ( o.isObjectProperty( e ) ) {
			return new RelationId( u );
		} else if ( o.isIndividual( e ) ) {
			return new InstanceId( u );
		} else throw new AlignmentException( "Cannot interpret URI "+u );
	}


	/**
	 * Generate a copy of this alignment object
	 */
	// JE: this is a mere copy of the method in BasicAlignement
	// It has two difficulties
	// - it should call the current init() and not that of BasicAlignement
	// - it should catch the AlignmentException that it is supposed to raise
	public Object clone() {
		EDOALAlignment align = new EDOALAlignment();
		try {
			align.init( (Ontology)getOntology1(), (Ontology)getOntology2() );
		} catch ( AlignmentException e ) {};
		align.setType( getType() );
		align.setLevel( getLevel() );
		align.setFile1( getFile1() );
		align.setFile2( getFile2() );
		align.setExtensions( extensions.convertExtension( "cloned", this.getClass().getName()+"#clone" ) );
		try {
			align.ingest( this );
		} catch (AlignmentException ex) { 
			//	    logger.debug( "IGNORED Exception", ex );
		}
		return align;
	}

	public ArrayList<String> toSourceSPARQLQuery() {
		ArrayList<String> result = new ArrayList<String>();

		for(Cell cell: this) {
			String query= "SELECT distinct ";
			if(cell.getObject1() instanceof PathExpression) {
				query+="?s ?o WHERE { ";
				query+=getSparqlRelation(cell.getObject1(),"?s","?o");
				query+=" }";
			}
			else if(cell.getObject1() instanceof ClassExpression) {
				query+="?s WHERE {";
				query+=getSparqlClass(cell.getObject1(),"?s","a");
				query+="}";
			}
			//System.out.println(query);
			result.add(query);
		}

		return result;
	}

	public ArrayList<String> toTargetSPARQLQuery() {
		ArrayList<String> result = new ArrayList<String>();

		for(Cell cell: this) {
			String query= "SELECT distinct ";
			if(cell.getObject2() instanceof PathExpression) {
				query+="?s ?o WHERE { ";
				query+=getSparqlRelation(cell.getObject2(),"?s","?o");
				query+=" }";
			}
			else if(cell.getObject2() instanceof ClassExpression) {
				query+="?s WHERE {";
				query+=getSparqlClass(cell.getObject2(),"?s","a");
				query+="}";
			}
			//System.out.println(query);
			result.add(query);
		}

		return result;
	}


	public ArrayList<String> rewriteAllPossibilitiesQuery(String query){
		SparqlQuery spQ = new SparqlQuery(query);
		boolean translationPossibleO1 = false;
		boolean translationPossibleO2 = false;
		for (SparqlTriple triple: spQ.getTriples()) {
			for( Cell cell : this ){
				try {
					URI uri1 = cell.getObject1AsURI();
					URI uri2 = cell.getObject2AsURI();
					if(uri1!=null){
						if(triple.inSparqlTriple(uri1.toString())){
							translationPossibleO1 = true;
						}
						if(translationPossibleO1){
							if (triple.getPredicate().equals("<"+uri1.toString()+">")){
					//			System.out.println(uri1.toString() + " in query as predicate");
								triple.addTargetTriple(getSparqlRelation(cell.getObject2(), triple.getSubject(), triple.getObject() ));
							}
							else if (triple.getObject().equals("<"+uri1.toString()+">")){
						//		System.out.println(uri1.toString() + " in query as object");
								triple.addTargetTriple(getSparqlClass(cell.getObject2(), triple.getSubject(), triple.getPredicate()));
							}               
						}
					}

					if(uri2!=null && !translationPossibleO1){
						if(triple.inSparqlTriple(uri2.toString())){
							translationPossibleO2 = true;
						}
						if(translationPossibleO2){
							if (triple.getPredicate().equals("<"+uri2.toString()+">")){
								//pour l'instant juste predicat
						//		System.out.println(uri2.toString() + " in query as predicate");
								triple.addTargetTriple(getSparqlRelation(cell.getObject1(), triple.getSubject(), triple.getObject()));
							}
							else if (triple.getObject().equals("<"+uri2.toString()+">")){
					//			System.out.println(uri2.toString() + " in query as object");
								triple.addTargetTriple(getSparqlClass(cell.getObject1(), triple.getSubject(), triple.getPredicate()));
							}               
						}
					}
				} catch (AlignmentException alex) {
					alex.printStackTrace();
				}
			}
		}

		return spQ.toTargetQuery();
	}
	@Override
	public String translateMessage( String query ) {
		return rewriteAllPossibilitiesQuery(query).get(0);
	}

	public String getSparqlRelation (Object o2, String subject, String object){
		String result ="";
		if (o2 instanceof RelationId){
			result=subject +" <"+((RelationId) o2).getURI().toString()+"> "+object+". ";
		}
		else if(o2 instanceof PropertyId){
			result=subject +" <"+((PropertyId) o2).getURI().toString()+"> "+object+". ";
		}
		else if (o2 instanceof PropertyConstruction){
			Collection<PathExpression> pathExp =((PropertyConstruction) o2).getComponents();
			//OPERATEURS            
			if (((PropertyConstruction) o2).getOperator().equals(SyntaxElement.OR.getOperator())){
				int i=0;
				for (PathExpression p : pathExp){
					if (i<(pathExp.size()-1)){
						result+="{"+getSparqlRelation(p,subject,object)+"}UNION\n";
					}
					else if (i==(pathExp.size()-1)){
						result+="{"+getSparqlRelation(p,subject,object)+"}";
					}
					i++;
				}
			}
			else if (((PropertyConstruction) o2).getOperator().equals(SyntaxElement.AND.getOperator())){
				for (PathExpression p : pathExp){
					result+=getSparqlRelation(p,subject,object)+"\n";
				}
			}
			else if (((PropertyConstruction) o2).getOperator().equals(SyntaxElement.NOT.getOperator())){
				vartemp++;
				result+=subject+" ?var_temp"+(vartemp-1)+" "+object+".\n"
						+ "MINUS {";

				for (PathExpression p : pathExp){
					result+=getSparqlRelation(p,subject,object)+"\n";
				}
				result+="}\n";
			}
			else if (((PropertyConstruction) o2).getOperator().equals(SyntaxElement.COMPOSE.getOperator())){
				ArrayList<String> variablesInPath = new ArrayList<String>();
				variablesInPath.add(subject);
				for(int i =0; i < pathExp.size()-1; i++) {
					vartemp++;
					variablesInPath.add("?var_temp"+(vartemp-1));
				}
				variablesInPath.add(object);


				int i =0;
				for (PathExpression p: pathExp) {
					vartemp++;
					result+=getSparqlRelation(p,variablesInPath.get(i),variablesInPath.get(i+1))+"\n";
					i++;
				}	
				
			}

		}
		else if (o2 instanceof RelationConstruction){
			Collection<PathExpression> pathExp =((RelationConstruction) o2).getComponents();
			if (((RelationConstruction) o2).getOperator().equals(SyntaxElement.OR.getOperator())){
				int i=0;
				for (PathExpression p : pathExp){
					if (i<(pathExp.size()-1)){
						result+="{"+getSparqlRelation(p,subject,object)+"}UNION\n";
					}
					else if (i==(pathExp.size()-1)){
						result+="{"+getSparqlRelation(p,subject,object)+"}";
					}
					i++;
				}
			}
			else if (((RelationConstruction) o2).getOperator().equals(SyntaxElement.AND.getOperator())){
				for (PathExpression p : pathExp){
					result+=getSparqlRelation(p,subject,object)+"\n";
				}
			}
			else if (((RelationConstruction) o2).getOperator().equals(SyntaxElement.NOT.getOperator())){
				vartemp++;
				result+=subject+" ?var_temp"+(vartemp-1)+" "+object+".\n"
						+ "MINUS {";

				for (PathExpression p : pathExp){
					result+=getSparqlRelation(p,subject,object)+"\n";
				}
				result+="}\n";
			}
			else if (((RelationConstruction) o2).getOperator().equals(SyntaxElement.INVERSE.getOperator())){
				for (PathExpression p : pathExp){
					result+=getSparqlRelation(p,object,subject)+"\n";
				}
			}
			else if (((RelationConstruction) o2).getOperator().equals(SyntaxElement.COMPOSE.getOperator())){
				ArrayList<String> variablesInPath = new ArrayList<String>();
				variablesInPath.add(subject);
				for(int i =0; i < pathExp.size()-1; i++) {
					vartemp++;
					variablesInPath.add("?var_temp"+(vartemp-1));
				}
				variablesInPath.add(object);

				int i =0;
				for (PathExpression p: pathExp) {
					vartemp++;
					result+=getSparqlRelation(p,variablesInPath.get(i),variablesInPath.get(i+1))+"\n";
					i++;
				}	
			}
			else if (((RelationConstruction) o2).getOperator().equals(SyntaxElement.SYMMETRIC.getOperator())){
				for (PathExpression p : pathExp){
					result+="{"+getSparqlRelation(p,subject,object)+"}UNION\n"
							+ "{"+getSparqlRelation(p,object,subject)+"}\n";
				}
			}
			//for transitivity : find a way to write the "+" at the end of the relation
			else if (((RelationConstruction) o2).getOperator().equals(SyntaxElement.TRANSITIVE.getOperator())){
				for (PathExpression p : pathExp){
					if (p instanceof RelationId){
						result+=subject +" <"+((RelationId) p).getURI().toString()+">+ "+object+". \n";
					}
				}
			}
			else if (((RelationConstruction) o2).getOperator().equals(SyntaxElement.REFLEXIVE.getOperator())){
				for (PathExpression p : pathExp){
					result+=getSparqlRelation(p,subject,subject)+"\n";
				}
			}

		}
		else if (o2 instanceof RelationDomainRestriction){
			result+=getSparqlClass(((RelationDomainRestriction)o2).getDomain(),subject,"<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>");
		}
		else if (o2 instanceof RelationCoDomainRestriction){
			result+=getSparqlClass(((RelationCoDomainRestriction)o2).getCoDomain(),object,"<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>");
		}
		else if (o2 instanceof PropertyDomainRestriction){
			result+=getSparqlClass(((PropertyDomainRestriction)o2).getDomain(),subject,"<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>");
		}
		else if (o2 instanceof PropertyTypeRestriction){
			result+="FILTER(datatype("+object+") = <"+
					((PropertyTypeRestriction)o2).getType().getType()+">).\n";
		}
		else if (o2 instanceof PropertyValueRestriction){
			System.out.println(((PropertyValueRestriction)o2).getComparator().getURI()+" "
					+ ""+((PropertyValueRestriction)o2).getValue().getClass());

			if(((PropertyValueRestriction)o2).getValue() instanceof Value) {
				String comparator="";
				if(((PropertyValueRestriction)o2).getComparator().getURI().toString().equals(""
						+ "http://ns.inria.org/edoal/1.0/#equals")){
					comparator="=";
				}
				else if (((PropertyValueRestriction)o2).getComparator().getURI().toString().equals(""
						+ "http://ns.inria.org/edoal/1.0/#lower-than")){
					comparator="<";
				}
				else if (((PropertyValueRestriction)o2).getComparator().getURI().toString().equals(""
						+ "http://ns.inria.org/edoal/1.0/#greater-than")){
					comparator=">";
				}

				if(((Value)((PropertyValueRestriction)o2).getValue()).getType()==null){
					System.err.println(" WARN : No datatype specified for the PropertyValueRestriction"
							+ "\n \t it might not work for String values");
					result+="FILTER("+object+" "+comparator+" "+
							((Value)((PropertyValueRestriction)o2).getValue()).getValue()+").\n";
				}
				else {               
					result+="FILTER("+object+" "+comparator+ " \""+
							((Value)((PropertyValueRestriction)o2).getValue()).getValue()+"\"^^"
							+ "<"+((Value)((PropertyValueRestriction)o2).getValue()).getType().toString()+">).\n";
				}
			}
			else{
				System.err.println("This processing of PropertyValueRestriction only accepts Literals");
			}
		}

		return result;
	}

	public String getSparqlClass (Object o2, String subject, String predicate){
		String result ="";
		if (o2 instanceof ClassId){
			result=subject +" "+predicate+" <"+((ClassId) o2).getURI().toString()+">. ";
		}
		else if (o2 instanceof ClassConstruction){
			Collection<ClassExpression> pathExp =((ClassConstruction) o2).getComponents();
			if (((ClassConstruction) o2).getOperator().equals(SyntaxElement.OR.getOperator())){
				int i=0;
				for (ClassExpression p : pathExp){
					if (i<(pathExp.size()-1)){
						result+="{"+getSparqlClass(p,subject,predicate)+"}UNION\n";
					}
					else if (i==(pathExp.size()-1)){
						result+="{"+getSparqlClass(p,subject,predicate)+"}";
					}
					i++;
				}
			}
			else if (((ClassConstruction) o2).getOperator().equals(SyntaxElement.AND.getOperator())){
				for (ClassExpression p : pathExp){
					result+=getSparqlClass(p,subject,predicate)+"\n";
				}
			}
			else if (((ClassConstruction) o2).getOperator().equals(SyntaxElement.NOT.getOperator())){
				vartemp++;
				result+=subject+" "+predicate+" ?var_temp"+(vartemp-1)+".\n"
						+ "MINUS {";

				for (ClassExpression p : pathExp){
					result+=getSparqlClass(p,subject,predicate)+"\n";
				}
				result+="}\n";
			}
		}

		else if (o2 instanceof ClassOccurenceRestriction)    {
			PathExpression p =((ClassOccurenceRestriction)o2).getRestrictionPath();
			vartemp++;
			String variable_temp_here ="?variable_temp"+(vartemp-1); 
			String compte_here="?compte_var_temp"+(vartemp-1); 
			String comparator="";
			if(((ClassOccurenceRestriction)o2).getComparator().getURI().toString().equals(""
					+ "http://ns.inria.org/edoal/1.0/#greater-than") && 
					((ClassOccurenceRestriction)o2).getOccurence()==0){
				result+=getSparqlRelation(p,subject,variable_temp_here);
			}
			else{
				if(((ClassOccurenceRestriction)o2).getComparator().getURI().toString().equals(""
						+ "http://ns.inria.org/edoal/1.0/#equals")){
					comparator="=";
				}
				else if (((ClassOccurenceRestriction)o2).getComparator().getURI().toString().equals(""
						+ "http://ns.inria.org/edoal/1.0/#lower-than")){
					comparator="<";
				}
				else if (((ClassOccurenceRestriction)o2).getComparator().getURI().toString().equals(""
						+ "http://ns.inria.org/edoal/1.0/#greater-than")){
					comparator=">";
				}
				result+="{SELECT "+subject+" (COUNT("+variable_temp_here+") AS "+compte_here+")\n"
						+ "WHERE{ \n"+getSparqlRelation(p,subject,variable_temp_here)+"}\n"
						+ "GROUP BY ("+subject+")\n}\n"
						+ "FILTER("+compte_here+" "+comparator+" "
						+ ""+((ClassOccurenceRestriction)o2).getOccurence()+").\n";

			}
		}
		//all restrictions but ClassOccurenceRestriction
		else if (o2 instanceof ClassRestriction){
			//ajouter les filtres
			PathExpression p =((ClassRestriction)o2).getRestrictionPath();
			//System.out.println(p.getClass());
			//System.out.println(o2.getClass());
			vartemp++;
			String variable_temp_here ="?variable_temp"+(vartemp-1);           


			if(o2 instanceof ClassValueRestriction){
				String comparator="";
				if(((ClassValueRestriction)o2).getComparator().getURI().toString().equals(""
						+ "http://ns.inria.org/edoal/1.0/#equals")){
					comparator="=";
				}
				else if (((ClassValueRestriction)o2).getComparator().getURI().toString().equals(""
						+ "http://ns.inria.org/edoal/1.0/#lower-than")){
					comparator="<";
				}
				else if (((ClassValueRestriction)o2).getComparator().getURI().toString().equals(""
						+ "http://ns.inria.org/edoal/1.0/#greater-than")){
					comparator=">";
				}

				if(((ClassValueRestriction)o2).getValue() instanceof Value){
					result+=getSparqlRelation(p,subject,variable_temp_here);
					if(((Value)((ClassValueRestriction)o2).getValue()).getType() != null) {
						result+="FILTER("+variable_temp_here+" "+comparator+ " \""+
								((Value)((ClassValueRestriction)o2).getValue()).getValue()+"\"^^"
								+ "<"+((Value)((ClassValueRestriction)o2).getValue()).getType().toString()+">).\n";
					}
					else {
						result+="FILTER(str("+variable_temp_here+") "+comparator+ " \""+
								((Value)((ClassValueRestriction)o2).getValue()).getValue()+"\").\n";
					}
					
				}
				else if(((ClassValueRestriction)o2).getValue() instanceof InstanceId){
					result+=getSparqlRelation(p,subject,"<"+((InstanceId)((ClassValueRestriction)o2).getValue()).getURI().toString()+">");
					//result+="\nFILTER("+variable_temp_here+" "+comparator+ " "+
					//   "<"+((InstanceId)((ClassValueRestriction)o2).getValue()).getURI().toString()+">).\n";
				}
				else{
					System.err.println("AttributeValueRestrictions have not yet been implemented"
							+ " for the type of value you entered. "
							+ "\nType implemented : Literal or Instance");
				}
			}
			else if (o2 instanceof ClassDomainRestriction){
				result+=getSparqlRelation(p,subject,variable_temp_here);
				result+="\n"+getSparqlClass(((ClassDomainRestriction)o2).getDomain(),variable_temp_here,""
						+ "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>");
			}
			else if (o2 instanceof ClassTypeRestriction){
				result+=getSparqlRelation(p,subject,variable_temp_here);
				result+="\nFILTER(datatype("+variable_temp_here+") = <"+
						((ClassTypeRestriction)o2).getType().getType().toString()+">).\n";
			}         

		}
		return result;
	}   



}
