# SPARQL Rewrite from Complex alignments

## Easy use
- Needed: java runtime environment (tested with 1.8)
- Download the SparqlTranslator jar and the lib folder from "jar_utiles" then run
`java -jar SparqlTranslator.jar EDOALAlignmentOfYourChoice SPARQLQueryOfYourChoice`

## Code
This is an extension of the Alignment API.
- A few classes were added (in the alignmentplantae package).
- The EDOALAlignment class was modified to implement the rewriting system (function translateMessage overrides the BasicAlignment one).
- To get more details about the implementation of the paper, read the OM2016 paper (cf. References)
- The system can only process (1:n) correspondences and SPARQL queries with a variable as subject.
- A few changes were made the the OWLRendererVisitorClass

## Alignments
Some alignments are available on the repository.
They are in the EDOAL format. The following are in the folders
- mtsr2017
  - Two alignments
        - AgronomicTaxon - DBpedia
        - AgronomicTaxon - Agrovoc
  - Three query folders. Each one has a results folder
     - queries_AgronomicTaxon: queries derived from AgronomicTaxon competency questions
     - queries_Agrovoc: automatically rewritten queries from AgronomicTaxon queries
     - queries_DBpedia: automatically rewritten queries from AgronomicTaxon queries
  - AgronomicTaxon folder: Populated AgronomicTaxon module with all Triticum subtaxa
- om2016
 - Two datasets:
    - conference
        - ekaw-cmt
        - ekaw-confOf
    - taxon
      - AgronomicTaxon (older version) - DBpedia
  - Three subfolders in each dataset:
     - query: query on the source ontology to be rewritten
     - query-gold: manually rewritten query on target ontology
     - query_out: automatically rewritten query on target ontology (before some optimisations)

## References
- [EDOAL](http://alignapi.gforge.inria.fr/edoal.html)
- [Alignment API](http://alignapi.gforge.inria.fr/)
- [Conference dataset](http://oaei.ontologymatching.org/2016/conference)
- [AgronomicTaxon](http://ontology.irstea.fr/agronomictaxon/core)
- [OM2016 paper](http://ceur-ws.org/Vol-1766/om2016_Tpaper5.pdf)
- [MTSR2017 paper](https://www.researchgate.net/publication/321028656_Cross-Querying_LOD_Datasets_Using_Complex_Alignments_An_Application_to_Agronomic_Taxa)

# OWL Renderer
To use the modified OWLRenderer:
`java -jar parserprinter.jar -r fr.inrialpes.exmo.align.impl.renderer.OWLAxiomsRendererVisitor -o results/folder/alignment.owl relative/path/to/alignment.edoal`

To work, the parserprinter.jar must be in at the root of the folder in which the other datasets are (absolute paths don't work...)
