from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from pyshacl import validate
import pandas, re, time

HYPER_ONTOLOGY_PATH = "./hyper_ontology.ttl"
TAG = Namespace("https://theknowledgecommons.org/ns/tagology/")
DAT = Namespace("https://theknowledgecommons.org/tmp/")

def slug(text: str) -> str:
    s = str(text).strip().lower()
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    s = re.sub(r'_+', '_', s)
    return s.strip('_') or "empty"

def load_hyper_ontology(hypergraph: Graph) -> None:
    hypergraph.parse(HYPER_ONTOLOGY_PATH, format="turtle")
    hypergraph.bind("tag", TAG)
    hypergraph.bind("dat", DAT)

def add_isAArc(hypergraph: Graph, tails: list[URIRef], head: URIRef, headLabel: str) -> None:
    arc = TAG[f"isA_{slug(headLabel)}"]
    hypergraph.add((arc, RDF.type, TAG.isAArc))
    
    hypergraph.add((arc, TAG.hasHead, head))

    for tail in tails:
        hypergraph.add((arc, TAG.hasTail, tail))

def add_hasAArc(hypergraph: Graph, tail: URIRef, tailLabel: str, heads: list[URIRef]) -> None:
    arc = TAG[f"{slug(tailLabel)}_hasA"]
    hypergraph.add((arc, RDF.type, TAG.hasAArc))
    
    for head in heads:
        hypergraph.add((arc, TAG.hasHead, head))

    hypergraph.add((arc, TAG.hasTail, tail))

def load_from_csv(csv_path: str, csv_class: str, hypergraph: Graph) -> None:
    df = pandas.read_csv(csv_path, dtype=str).fillna("")

    obj_class = slug(csv_class)
    obj_class_uri = DAT[obj_class]

    # [CSV object class] is a hypergraph node
    hypergraph.add((obj_class_uri, RDF.type, TAG.HyperNode))
    hypergraph.add((obj_class_uri, RDFS.label, Literal(csv_class)))

    prop_uris = []
    for col in df.columns:
        prop = slug(col)
        prop_uri = DAT[prop]
        prop_uris.append(prop_uri)

        # [properties(columns)] are hypergraph nodes
        hypergraph.add((prop_uri, RDF.type, TAG.HyperNode))
        hypergraph.add((prop_uri, RDFS.label, Literal(col)))

        tag_uris = []
        for cell in df[col].unique():
            val = slug(cell)
            tag_uri = DAT[f"tag/{prop}/{val}"]
            tag_uris.append(tag_uri)

            # [tags = property(column):value pairs] are hypergraph nodes
            hypergraph.add((tag_uri, RDF.type, TAG.HyperNode))
            hypergraph.add((tag_uri, RDFS.label, Literal(cell)))
        
        # [tags = property(column):value pairs] IS-A [property(column)]
        add_isAArc(hypergraph, tag_uris, prop_uri, prop)

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
            tag_uri = DAT[f"tag/{prop}/{val}"]
            tag_uris.append(tag_uri)

        # all hypergraph nodes should have been added by this point
        # [objects(rows)] HAS-A [tags = property(column):value pairs]
        add_hasAArc(hypergraph, obj_uri, obj_label, tag_uris)

    # [objects(rows)] IS-A [CSV object class]
    add_isAArc(hypergraph, obj_uris, obj_class_uri, obj_class)

def test(csv_path: str, csv_class: str) -> None:
    start = time.perf_counter()

    hypergraph = Graph()
    load_hyper_ontology(hypergraph)
    load_from_csv(csv_path, csv_class, hypergraph)

    '''
    # shacl validation of BF-hypergraph
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
    '''

    hypergraph.serialize(destination="hypergraph.ttl", format="turtle")

    duration = (time.perf_counter() - start) / 60
    print(f"[PERFORMANCE] Graph creation took {duration:.2f} minutes")

if __name__ == "__main__":
    test("./SCDB/SCDB_2025_01_caseCentered_Citation.csv", "Supreme Court Cases by Citation")
