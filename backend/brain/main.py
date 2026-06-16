from brain.hypergraph import csv_to_hypergraph
from brain.hypermatrix import hypergraph_to_matrix
from pyoxigraph import Store, RdfFormat
from pathlib import Path
import time, shutil

'''
import psutil
def print_ram():
    rss = psutil.Process(os.getpid()).memory_info().rss / (1024**3)
    print(f"[PERFORMANCE] Current RAM usage: {rss:.2f} GB")
'''

STORE_DIR = "./scdb_store"
#STORE_DIR = "./hyper_store"
HYPER_ONTOLOGY = "./hyper_ontology.ttl"

def test(hyper_store: Store):
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

def main():
    start = time.perf_counter()

    store_path = Path(STORE_DIR)
    if store_path.exists():
        shutil.rmtree(store_path)

    hyper_store = Store(store_path)
    hyper_store.bulk_load(path=Path(HYPER_ONTOLOGY), format=RdfFormat.TURTLE)
    print(f"[STATUS] Triplestore created with hypergraph ontology {HYPER_ONTOLOGY}")

    test(hyper_store)

    #hyper_store.clear()
    #shutil.rmtree(store_path)
    
    duration = (time.perf_counter() - start) / 60
    print(f"[PERFORMANCE] Total Duration: {duration:.2f} minutes")

if __name__ == "__main__":
    main()
