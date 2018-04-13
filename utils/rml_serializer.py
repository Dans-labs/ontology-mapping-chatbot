from rdflib import Graph, Namespace, Literal, URIRef, BNode, RDFS, XSD

rr = Namespace("http://www.w3.org/ns/r2rml#")
rml = Namespace("http://semweb.mmlab.be/ns/rml#")
ql = Namespace('http://semweb.mmlab.be/ns/ql#')

RDF_TYPE = {
    'boolean': XSD.boolean,
    'date': XSD.date,
    'datetime': XSD.datetime,
    'int': XSD.int,
    'double': XSD.double
}

SUBJECT_URI = "https://data.opendatasoft.com/ld/resources/{dataset_id}/{class_name}/{{{field_name}}}"


def serialize(confirmed_correspondances, dataset_id):
    rdf_mapping = Graph()
    rdf_mapping.bind("ql", ql)
    rdf_mapping.bind("rr", rr)
    rdf_mapping.bind("rml", rml)
    for class_correspondance in confirmed_correspondances['classes']:
        add_class_map(rdf_mapping, class_correspondance, dataset_id)
    for property_correspondance in confirmed_correspondances['properties']:
        add_predicate_map(rdf_mapping, property_correspondance, confirmed_correspondances['classes'])
    return rdf_mapping.serialize(format='ttl')


def add_class_map(rdf_mapping, class_correspondance, dataset_id):
    subject_id = URIRef("#{}".format(class_correspondance['class']))
    logical_source = rml['logicalSource']
    logical_source_node = BNode()
    rdf_mapping.add((subject_id, logical_source, logical_source_node))
    rdf_mapping.add((logical_source_node, rml['source'], Literal(dataset_id)))
    rdf_mapping.add((logical_source_node, rml['referenceFormulation'], ql['JSONPath']))
    rdf_mapping.add((logical_source_node, rml['iterator'], Literal("$.[*].fields")))
    # Adding resource subject and type
    subject_map_node = BNode()
    subject_map = rr['subjectMap']
    rdf_mapping.add((subject_id, subject_map, subject_map_node))
    rdf_mapping.add((subject_map_node, rr['template'], Literal(SUBJECT_URI.format(dataset_id=dataset_id, class_name=class_correspondance['class'], field_name=class_correspondance['field_name']))))
    rdf_mapping.add((subject_map_node, rr['class'], URIRef(class_correspondance['uri'])))
    # Adding label of the resource
    predicate_map = rr['predicateObjectMap']
    node = BNode()
    rdf_mapping.add((subject_id, predicate_map, node))
    rdf_mapping.add((node, rr['predicate'], RDFS.label))
    object_node = BNode()
    rdf_mapping.add((node, rr['objectMap'], object_node))
    rdf_mapping.add((object_node, rml['reference'], Literal("$.{}".format(class_correspondance['field_name']))))


def add_predicate_map(rdf_mapping, property_correspondance, class_correspondances):
    subject_id = URIRef("#{}".format(property_correspondance['associated_class']))
    predicate_map = rr['predicateObjectMap']
    node = BNode()
    rdf_mapping.add((subject_id, predicate_map, node))
    rdf_mapping.add((node, rr['predicate'], URIRef(property_correspondance['uri'])))
    object_node = BNode()
    rdf_mapping.add((node, rr['objectMap'], object_node))
    field_name = property_correspondance['field_name']
    class_correspondance = get_class(field_name, class_correspondances)
    if class_correspondance:
        # Target of the predicate is a resource (URI)
        parent_map_id = URIRef("#{}".format(class_correspondance['class']))
        if parent_map_id != subject_id:
            rdf_mapping.add((object_node, rr['parentTriplesMap'], parent_map_id))
    else:
        # Target of the predicate is a field value (Term)
        field_type = property_correspondance['type']
        rdf_mapping.add((object_node, rml['reference'], Literal("$.{}".format(field_name))))
        if field_type in RDF_TYPE:
            rdf_mapping.add((object_node, rr['datatype'], RDF_TYPE[field_type]))


def get_class(field_name, class_correspondances):
    for class_correspondance in class_correspondances:
        if field_name == class_correspondance['field_name']:
            return class_correspondance
    return None
