from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF
from pyshacl import validate
import pandas, re

HYPER_ONTOLOGY_PATH = "./hyper_ontology.ttl"
TAG = Namespace("https://theknowledgecommons.org/ns/tagology/")
DAT = Namespace("https://theknowledgecommons.org/tmp/")

def slug(text: str) -> str:
    return re.sub(r'[^a-z0-9_]', '', text.strip().lower().replace(' ', '_'))

def load_hyper_ontology(hypergraph: Graph) -> bool:
    hypergraph.parse(HYPER_ONTOLOGY_PATH, format="turtle")
    hypergraph.bind("tag", TAG)
    hypergraph.bind("dat", DAT)
    return True

def add_isAArc(hypergraph: Graph, tails: list[URIRef], head: URIRef, headLabel: str) -> URIRef:
    arc = TAG[f"isA_{slug(headLabel)}"]
    hypergraph.add((arc, RDF.type, TAG.isAArc))
    
    hypergraph.add((arc, TAG.hasHead, head))

    for tail in tails:
        hypergraph.add((arc, TAG.hasTail, tail))

    return arc

def add_hasAArc(hypergraph: Graph, tail: URIRef, tailLabel: str, heads: list[URIRef]) -> URIRef:
    arc = TAG[f"{slug(tailLabel)}_hasA"]
    hypergraph.add((arc, RDF.type, TAG.hasAArc))
    
    for head in heads:
        hypergraph.add((arc, TAG.hasHead, head))

    hypergraph.add((arc, TAG.hasTail, tail))

    return arc

def load_from_csv(csv_path: str, csv_class: str, hypergraph: Graph) -> bool:
    df = pandas.read_csv(csv_path, dtype=str).fillna("")

    obj_class = slug(csv_class)
    obj_class_uri = DAT[obj_class]

    # [CSV object class] is a hypergraph node
    hypergraph.add((obj_class_uri, RDF.type, TAG.HyperNode))

    prop_uris = []
    for col in df.columns:
        prop = slug(col)
        prop_uri = DAT[prop]
        prop_uris.append(prop_uri)

        # [properties(columns)] are hypergraph nodes
        hypergraph.add((prop_uri, RDF.type, TAG.HyperNode))

        tag_uris = set()
        for _, row in df.iterrows():
            val = slug(row[col])
            tag_uri = DAT[f"{prop}--{val}"]
            tag_uris.add(tag_uri)

            # [tags = property(column):value pairs] are hypergraph nodes
            hypergraph.add((tag_uri, RDF.type, TAG.HyperNode))
        
        # [tags = property(column):value pairs] IS-A [property(column)]
        add_isAArc(hypergraph, list(tag_uris), prop_uri, prop)

    # [CSV object class] HAS-A [properties(columns)]
    add_hasAArc(hypergraph, obj_class_uri, obj_class, prop_uris)

    obj_uris = []
    for index, row in df.iterrows():
        obj_label = f"{obj_class}_{index}"
        obj_uri = DAT[obj_label]
        obj_uris.append(obj_uri)

        # [objects(rows)] are hypergraph nodes
        hypergraph.add((obj_uri, RDF.type, TAG.HyperNode))

        tag_uris = []
        for col in df.columns:
            prop = slug(col)
            val = slug(row[col])
            tag_uri = DAT[f"{prop}--{val}"]
            tag_uris.append(tag_uri)

        # all hypergraph nodes should have been added by this point
        # [objects(rows)] HAS-A [tags = property(column):value pairs]
        add_hasAArc(hypergraph, obj_uri, obj_label, tag_uris)

    # [objects(rows)] IS-A [CSV object class]
    add_isAArc(hypergraph, obj_uris, obj_class_uri, obj_class)

    return True

def test(csv_path: str, csv_class: str):
    hypergraph = Graph()
    load_hyper_ontology(hypergraph)
    load_from_csv(csv_path, csv_class, hypergraph)

    conforms, results_graph, results_text = validate(
        data_graph=hypergraph,
        shacl_graph=hypergraph,
        inference="rdfs"
    )
    print(results_text)

    print(f"Summary:\n  triples: {len(hypergraph)}")
    print("  Hypergraph Nodes: ", len(list(hypergraph.subjects(RDF.type, TAG.HyperNode))))
    print("  IS-A B-Hyperarcs: ", len(list(hypergraph.subjects(RDF.type, TAG.isAArc))))
    print("  HAS-A F-Hyperarcs: ", len(list(hypergraph.subjects(RDF.type, TAG.hasAArc))))
    print("\n")
    print(hypergraph.serialize(format="turtle"))

if __name__ == "__main__":
    test("rulings.csv", "Supreme Court Rulings")
