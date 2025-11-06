package alignementplantae;

import fr.inrialpes.exmo.align.impl.edoal.EDOALAlignment;
import fr.inrialpes.exmo.align.impl.renderer.RDFRendererVisitor;
import fr.inrialpes.exmo.align.parser.AlignmentParser;
import org.semanticweb.owl.align.AlignmentException;
import org.semanticweb.owl.align.AlignmentVisitor;

import java.io.*;
import java.util.ArrayList;
import java.util.Properties;
import org.semanticweb.owl.align.Cell;

/**
 * Created by irit-ut2j on 27/04/2017.
 */
public class main {

	public static void main(String[] args) {
		String qtest= "PREFIX : <http://ekaw#>\n"
				+ "SELECT distinct ?x where { {?x a :Accepted_Paper. } union {?x :hasReviewer ?y .}}";
		/*try {
			File f = new File(args[0]);
			String queryOut = changeQuery(f, args[1]);
			System.out.println(queryOut);
			// FileWriter fw = new FileWriter(new File(args[2]));
			// fw.write(queryOut);
			// fw.close();

		} catch (Exception ex) {
			ex.printStackTrace();
		}*/
		try {
			File alignementfile = new File("/home/thieblin/eclipse-workspace/ComplexAlignmentGenerator/output/conference/test_0.0/conference-cmt.edoal");
			AlignmentParser ap=new AlignmentParser();
	        EDOALAlignment al=(EDOALAlignment) ap.parse(alignementfile.toURI());
	        //ArrayList<String> targetQueries = al.rewriteAllPossibilitiesQuery(qtest);
	      //  ArrayList<String> targetQueries = al.toTargetSPARQLQuery();
	        ArrayList<String> targetQueries = al.toSourceSPARQLQuery();
	        for (String s: targetQueries) {
	        	System.out.println(s);
	        }
		} catch (Exception ex) {
			ex.printStackTrace();
		}
		
		/*try {
        	File alignementfile = new File("/home/thieblin/eclipse-workspace/ComplexAlignmentGenerator/output/conference/test_0.0/cmt-conference.edoal");
			AlignmentParser ap=new AlignmentParser();
	        EDOALAlignment al = (EDOALAlignment) ap.parse(alignementfile.toURI());
        	EDOALAlignment inverseAl = (al.inverse());
        	PrintWriter writer = new PrintWriter (new File("test.edoal")); 
        	AlignmentVisitor renderer = new RDFRendererVisitor(writer); 
        	inverseAl.render(renderer); 
        	writer.flush(); 
        	writer.close();
		} catch (AlignmentException | FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}*/
       

	}

	static public String changeQuery(File alignementfile, String queryIn) throws AlignmentException {

        AlignmentParser ap=new AlignmentParser();
        EDOALAlignment al=(EDOALAlignment) ap.parse(alignementfile.toURI());
        
        System.out.println("Nb cells " + al.nbCells());
        for(Cell c : al.getArrayElements()){
            System.out.println(c.getId());
        }
       
        // Transform query
        String transformedQuery = null;
        try {
            InputStream in = new FileInputStream( queryIn );
            BufferedReader reader = new BufferedReader( new InputStreamReader(in) );
            String line ;
            String queryString = "";
            while ((line = reader.readLine()) != null) {
                queryString += line + "\n";
            }
            Properties parameters = new Properties();
            transformedQuery = ((EDOALAlignment)al).rewriteQuery( queryString, parameters );
            // System.out.println(queryString);

            // System.out.println(transformedQuery);

        } catch ( Exception ex ) { ex.printStackTrace(); }
        return transformedQuery;
    }
}
