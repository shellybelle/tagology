from rdflib import Namespace, URIRef, Literal
from rdflib.namespace import RDF
from pyoxigraph import Store, RdfFormat
from pathlib import Path
import pandas, re, requests

TAG = Namespace("https://theknowledgecommons.org/ns/tagology/")
DATA = Namespace("https://theknowledgecommons.org/tmp/")
DCTERM = Namespace("http://purl.org/dc/terms/")

class Writer:
    def __init__(self, output_file: str):
        self.file = output_file
        self.out = None
        self.triple_count = 0

    def __enter__(self):
        self.out = open(self.file, "w", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.out:
            self.out.close()

    def triple(self, s: URIRef, p: URIRef, o: URIRef | Literal) -> None:
        if self.out is None:
            raise RuntimeError("Writer not opened")
        self.out.write(f"{s.n3()} {p.n3()} {o.n3()} .\n")
        self.triple_count += 1

def slug(text: str) -> str:
    s = str(text).strip().lower()
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s)
    return s.strip('_') or "empty"

def add_isAArc(writer: Writer, tails: list[URIRef], head: URIRef, headLabel: str) -> None:
    arc = TAG[f"isA_{slug(headLabel)}"]
    writer.triple(arc, RDF.type, TAG.isAArc)
    for tail in tails:
        writer.triple(arc, TAG.hasTail, tail)
    writer.triple(arc, TAG.hasHead, head)

def add_hasAArc(writer: Writer, tail: URIRef, tailLabel: str, heads: list[URIRef]) -> None:
    arc = TAG[f"{slug(tailLabel)}_hasA"]
    writer.triple(arc, RDF.type, TAG.hasAArc)
    writer.triple(arc, TAG.hasTail, tail)
    for head in heads:
        writer.triple(arc, TAG.hasHead, head)

def csv_to_nt(csv_url: str, csv_obj: str) -> Path:

    r = requests.head(csv_url, allow_redirects=True)
    r.raise_for_status()
    size_mb = int(r.headers.get("Content-Length", 0)) / (1024 * 1024)
    
    print(f"[STATUS] Parsing {csv_url} ({size_mb:.2f} MB)...") 
    df = pandas.read_csv(csv_url, dtype=str, compression='infer').fillna("")

    obj_class = slug(csv_obj)
    output_file = f"./hypergraph_{obj_class}.nt"

    with Writer(output_file) as writer:
        obj_class_uri = DATA[obj_class]

        # [CSV object class] is a hypergraph node
        writer.triple(obj_class_uri, RDF.type, TAG.HyperNode)
        writer.triple(obj_class_uri, TAG.label, Literal(csv_obj))

        prop_uris = []
        for col in df.columns:
            prop = slug(col)
            prop_uri = DATA[prop]
            prop_uris.append(prop_uri)

            # [properties(columns)] are hypergraph nodes
            writer.triple(prop_uri, RDF.type, TAG.HyperNode)
            writer.triple(prop_uri, TAG.label, Literal(col))

            tag_uris = []
            for cell in df[col].unique():
                val = slug(cell)
                tag_uri = DATA[f"tag/{prop}/{val}"]
                tag_uris.append(tag_uri)

                # [tags = property(column):value pairs] are hypergraph nodes
                writer.triple(tag_uri, RDF.type, TAG.HyperNode)
                writer.triple(tag_uri, TAG.label, Literal(cell))
        
            # [tags = property(column):value pairs] IS-A [property(column)]
            add_isAArc(writer, tag_uris, prop_uri, prop)

        # [CSV object class] HAS-A [properties(columns)]
        add_hasAArc(writer, obj_class_uri, obj_class, prop_uris)

        obj_uris = []
        for index, row in df.iterrows():
            obj_label = f"{obj_class}_{index}"
            obj_uri = DATA[obj_label]
            obj_uris.append(obj_uri)

            # [objects(rows)] are hypergraph nodes
            writer.triple(obj_uri, RDF.type, TAG.HyperNode)
            writer.triple(obj_uri, DCTERM.source, URIRef(csv_url))

            tag_uris = []
            for col in df.columns:
                prop = slug(col)
                val = slug(row[col])
                tag_uri = DATA[f"tag/{prop}/{val}"]
                tag_uris.append(tag_uri)

            # all hypergraph nodes should have been added by this point
            # [objects(rows)] HAS-A [tags = property(column):value pairs]
            add_hasAArc(writer, obj_uri, obj_label, tag_uris)

        # [objects(rows)] IS-A [CSV object class]
        add_isAArc(writer, obj_uris, obj_class_uri, obj_class)

        print(f"[STATUS] {output_file} created with {writer.triple_count} triples")

    # TODO : only return this on full success
    return Path(output_file)

def nt_to_hypergraph(output_path: Path, hyper_store: Store) -> None:
    hyper_store.bulk_load(path=output_path, format=RdfFormat.N_TRIPLES, lenient=True)
    print(f"[STATUS] Loaded {str(output_path)} into triplestore")

def csv_to_hypergraph(hyper_store: Store, csv_url: str, csv_obj: str) -> None:
    output_path = csv_to_nt(csv_url, csv_obj)
    nt_to_hypergraph(output_path, hyper_store)
    output_path.unlink()
    print(f"[STATUS] {str(output_path)} deleted")

def test() -> None:
    hyper_store = Store("../scdbTesting/scdb_store")
    hyper_store.bulk_load(path="../hyper_ontology.ttl", format=RdfFormat.TURTLE)
    
    csv_to_hypergraph(hyper_store, "http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_caseCentered_Citation.csv.zip", "Supreme Court Cases by Citation")
    csv_to_hypergraph(hyper_store, "http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_caseCentered_Docket.csv.zip", "Supreme Court Cases by Docket")
    csv_to_hypergraph(hyper_store, "http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_caseCentered_LegalProvision.csv.zip", "Supreme Court Cases by Provision")
    csv_to_hypergraph(hyper_store, "http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_caseCentered_Vote.csv.zip", "Supreme Court Cases by Provision - Split Votes")
    csv_to_hypergraph(hyper_store, "http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_justiceCentered_Citation.csv.zip", "Supreme Court Judges by Citation")
    csv_to_hypergraph(hyper_store, "http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_justiceCentered_Docket.csv.zip", "Supreme Court Judges by Docket")
    csv_to_hypergraph(hyper_store, "http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_justiceCentered_LegalProvision.csv.zip", "Supreme Court Judges by Provision")
    csv_to_hypergraph(hyper_store, "http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_justiceCentered_Vote.csv.zip", "Supreme Court Judges by Provision - Split Votes")

    total_query = """
        SELECT (COUNT(*) AS ?triples)
        WHERE { ?s ?p ?o }"""
    count_query = """
        SELECT ?type (COUNT(*) AS ?count)
        WHERE {
            ?s a ?type .
        }
        GROUP BY ?type"""
    incidence_query = """
        PREFIX tag: <https://theknowledgecommons.org/ns/tagology/>
        SELECT (COUNT(*) AS ?incidences)
        WHERE {
            { ?arc tag:hasTail ?node }
            UNION
            { ?arc tag:hasHead ?node }
        }"""

    for row in hyper_store.query(total_query):
        print(f"[STATUS] Store contains {row['triples']} triples")
    for row in hyper_store.query(count_query):
        print(f"    {row['type']}: {row['count']}")
    for row in hyper_store.query(incidence_query):
        print(f"    incidences: {row['incidences']}")

if __name__ == "__main__":
    test()

