import xml.etree.ElementTree as ET
import sys

class EdoalParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        self.namespaces = self._get_namespaces()

    def _get_namespaces(self):
        # Extract namespaces from the root element
        ns = {}
        for key, value in self.root.attrib.items():
            if 'xmlns' in key:
                prefix = key.split(':')[-1]
                ns[prefix] = value
        # Add default namespace if present
        if '' in self.root.nsmap:
            ns['default'] = self.root.nsmap['']
        # Add common namespaces if not defined
        if 'rdf' not in ns:
            ns['rdf'] = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        if 'align' not in ns:
            ns['align'] = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        if 'edoal' not in ns:
            ns['edoal'] = 'http://ns.inria.org/edoal/1.0/#'
        return ns

    def parse(self):
        alignments = []
        for cell in self.root.findall('.//align:Cell', self.namespaces):
            entity1_element = cell.find('align:entity1', self.namespaces)
            entity2_element = cell.find('align:entity2', self.namespaces)
            relation_element = cell.find('align:relation', self.namespaces)
            measure_element = cell.find('align:measure', self.namespaces)

            entity1 = self._parse_entity(entity1_element)
            entity2 = self._parse_entity(entity2_element)
            
            relation = relation_element.text if relation_element is not None else None
            measure = float(measure_element.text) if measure_element is not None else None

            alignments.append((entity1, entity2, relation, measure))
        return alignments

    def _parse_entity(self, entity_element):
        """
        Parses the entity element to extract a simple URI for now.
        This will be extended to handle complex structures.
        """
        if entity_element is None:
            return None
        
        # Find the first child with an rdf:about attribute
        for elem in entity_element.iter():
            about_uri = elem.get('{' + self.namespaces['rdf'] + '}about')
            if about_uri:
                return about_uri
        
        return "Complex Entity (TODO)"


if __name__ == '__main__':
    if len(sys.argv) > 1:
        parser = EdoalParser(sys.argv[1])
        results = parser.parse()
        for res in results:
            print(f"Entity 1: {res[0]}")
            print(f"Entity 2: {res[1]}")
            print(f"Relation: {res[2]}")
            print(f"Measure:  {res[3]}")
            print("-" * 20)
    else:
        print("Usage: python edoal_parser.py <path_to_edoal_file>")
