import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Any, Optional

# --- Data Classes for EDOAL Structure ---

@dataclass
class EDOALEntity:
    """Base class for all EDOAL entities."""
    pass

@dataclass
class IdentifiedEntity(EDOALEntity):
    """Represents an entity identified by a URI."""
    uri: str

@dataclass
class Class(IdentifiedEntity): pass

@dataclass
class Property(IdentifiedEntity): pass

@dataclass
class Relation(IdentifiedEntity): pass

@dataclass
class Instance(IdentifiedEntity): pass

@dataclass
class LogicalConstructor(EDOALEntity):
    """Represents logical constructors like and, or, not."""
    operator: str
    operands: List[EDOALEntity] = field(default_factory=list)

@dataclass
class PathConstructor(EDOALEntity):
    """Represents path constructors like compose, inverse."""
    operator: str
    operands: List[EDOALEntity] = field(default_factory=list)

@dataclass
class Restriction(EDOALEntity):
    """Base class for restrictions."""
    on_attribute: EDOALEntity

@dataclass
class AttributeValueRestriction(Restriction):
    comparator: str
    value: Any

@dataclass
class AttributeDomainRestriction(Restriction):
    class_expression: EDOALEntity

# --- Alignment Structure ---

@dataclass
class Cell:
    """Represents a single correspondence (a Cell)."""
    entity1: EDOALEntity
    entity2: EDOALEntity
    relation: str
    measure: float

@dataclass
class Alignment:
    """Represents the entire alignment."""
    onto1: str
    onto2: str
    cells: List[Cell] = field(default_factory=list)

import sys

class EdoalParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        self.namespaces = self._get_namespaces()

    def _get_namespaces(self):
        # Manually parsing namespaces for xml.etree.ElementTree
        ns = dict([
            node for _, node in ET.iterparse(self.file_path, events=['start-ns'])
        ])
        # Add common namespaces if not defined in the file
        if 'rdf' not in ns:
            ns['rdf'] = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        if 'align' not in ns:
            ns['align'] = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        if 'edoal' not in ns:
            ns['edoal'] = 'http://ns.inria.org/edoal/1.0/#'
        # The default namespace key is empty, let's alias it for findall
        if '' in ns:
            ns['default'] = ns['']
        return ns

    def parse(self) -> Alignment:
        onto1 = self.root.find('.//align:onto1/align:Ontology', self.namespaces).get('{' + self.namespaces['rdf'] + '}about')
        onto2 = self.root.find('.//align:onto2/align:Ontology', self.namespaces).get('{' + self.namespaces['rdf'] + '}about')
        
        alignment = Alignment(onto1=onto1, onto2=onto2)

        for cell_element in self.root.findall('.//align:Cell', self.namespaces):
            entity1_element = cell_element.find('align:entity1', self.namespaces)
            entity2_element = cell_element.find('align:entity2', self.namespaces)
            relation_element = cell_element.find('align:relation', self.namespaces)
            measure_element = cell_element.find('align:measure', self.namespaces)

            entity1 = self._parse_entity(entity1_element[0]) if entity1_element is not None and len(entity1_element) > 0 else None
            entity2 = self._parse_entity(entity2_element[0]) if entity2_element is not None and len(entity2_element) > 0 else None
            
            relation = relation_element.text if relation_element is not None else None
            measure = float(measure_element.text) if measure_element is not None else 0.0

            if entity1 and entity2:
                alignment.cells.append(Cell(entity1, entity2, relation, measure))
        return alignment

    def _parse_entity(self, element: ET.Element) -> Optional[EDOALEntity]:
        """
        Recursively parses an XML element into an EDOALEntity data class.
        """
        if element is None:
            return None

        tag = element.tag.split('}')[-1]
        rdf_about = element.get('{' + self.namespaces['rdf'] + '}about')

        # Identified Entities
        if rdf_about:
            if tag == 'Class': return Class(uri=rdf_about)
            if tag == 'Property': return Property(uri=rdf_about)
            if tag == 'Relation': return Relation(uri=rdf_about)
            if tag == 'Instance': return Instance(uri=rdf_about)

        # Restrictions
        if tag == 'AttributeDomainRestriction':
            on_attr_elem = element.find('edoal:onAttribute', self.namespaces)
            class_expr_elem = element.find('edoal:class', self.namespaces)
            return AttributeDomainRestriction(
                on_attribute=self._parse_entity(on_attr_elem[0]) if on_attr_elem is not None and len(on_attr_elem) > 0 else None,
                class_expression=self._parse_entity(class_expr_elem[0]) if class_expr_elem is not None and len(class_expr_elem) > 0 else None
            )
        
        if tag == 'AttributeValueRestriction':
            on_attr_elem = element.find('edoal:onAttribute', self.namespaces)
            comparator_elem = element.find('edoal:comparator', self.namespaces)
            value_elem = element.find('edoal:value', self.namespaces)
            return AttributeValueRestriction(
                on_attribute=self._parse_entity(on_attr_elem[0]) if on_attr_elem is not None and len(on_attr_elem) > 0 else None,
                comparator=comparator_elem.get('{' + self.namespaces['rdf'] + '}resource') if comparator_elem is not None else None,
                value=self._parse_entity(value_elem[0]) if value_elem is not None and len(value_elem) > 0 else None
            )

        # Logical/Path Constructors (and, or, compose, etc.)
        if tag in ['and', 'or', 'compose', 'inverse', 'transitive', 'not']:
             operands = [self._parse_entity(child) for child in element[0]] if len(element) > 0 and element[0].get('{' + self.namespaces['rdf'] + '}parseType') == 'Collection' else [self._parse_entity(element[0])]
             if tag in ['and', 'or', 'not']:
                 return LogicalConstructor(operator=tag, operands=operands)
             else:
                 return PathConstructor(operator=tag, operands=operands)

        # Fallback for complex structures not yet implemented
        return IdentifiedEntity(uri=f"Complex Entity: {tag}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        parser = EdoalParser(sys.argv[1])
        alignment_result = parser.parse()
        print(f"Ontology 1: {alignment_result.onto1}")
        print(f"Ontology 2: {alignment_result.onto2}")
        print(f"Found {len(alignment_result.cells)} correspondences.")
        print("=" * 30)
        for i, cell in enumerate(alignment_result.cells):
            print(f"--- Cell {i+1} ---")
            print(f"  Entity 1: {cell.entity1}")
            print(f"  Entity 2: {cell.entity2}")
            print(f"  Relation: {cell.relation}")
            print(f"  Measure:  {cell.measure}")
        print("=" * 30)
    else:
        print("Usage: python edoal_parser.py <path_to_edoal_file>")
