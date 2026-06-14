from rdflib import Namespace, URIRef, Literal
from rdflib.namespace import RDF
import pandas, re, time, requests, os

HYPER_ONTOLOGY_TTL = "./hyper_ontology.ttl"
OUTPUT_DIR = "./hypergraphs"
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

'''
import psutil
def print_ram():
    rss = psutil.Process(os.getpid()).memory_info().rss / (1024**3)
    print(f"[PERFORMANCE] Current RAM usage: {rss:.2f} GB")
'''

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

def load_from_csv(csv_url: str, csv_obj: str) -> str:
    df = pandas.read_csv(csv_url, dtype=str, compression='infer').fillna("")

    obj_class = slug(csv_obj)
    output_file = f"{OUTPUT_DIR}/hypergraph_{obj_class}.nt"

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

def csvs_to_hypergraph(csvs: list[tuple[str, str]]) -> None:
    for csv_url, csv_obj in csvs:
        r = requests.head(csv_url, allow_redirects=True)
        r.raise_for_status()
        size_mb = int(r.headers.get("Content-Length", 0)) / (1024 * 1024)
        print(f"[STATUS] Loading {csv_url} ({size_mb:.2f} MB)...")
        load_from_csv(csv_url, csv_obj)

def test():
    start = time.perf_counter()

    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
    else:
        os.makedirs(OUTPUT_DIR)

    # TODO: USER ENTERED FILES AND CLASSES
    csvs = [
        ("http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_caseCentered_Citation.csv.zip",
         "Supreme Court Cases by Citation"),
        ("http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_caseCentered_Docket.csv.zip",
         "Supreme Court Cases by Docket"),
        ("http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_caseCentered_LegalProvision.csv.zip",
         "Supreme Court Cases by Provision"),
        ("http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_caseCentered_Vote.csv.zip",
         "Supreme Court Cases by Provision - Split Votes"),
        ("http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_justiceCentered_Citation.csv.zip",
         "Supreme Court Judges by Citation"),
        ("http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_justiceCentered_Docket.csv.zip",
         "Supreme Court Judges by Docket"),
        ("http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_justiceCentered_LegalProvision.csv.zip",
         "Supreme Court Judges by Provision"),
        ("http://scdb.wustl.edu/_brickFiles/2025_01/SCDB_2025_01_justiceCentered_Vote.csv.zip",
         "Supreme Court Judges by Provision - Split Votes")]

    csvs_to_hypergraph(csvs)

    # TODO : SHACL validation

    print(f"[STATUS] {len(csvs)} CSVs translated to semantic hypergraph .nt files")
    duration = (time.perf_counter() - start) / 60
    print(f"[PERFORMANCE] Translation took {duration:.2f} minutes")
