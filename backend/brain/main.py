from brain.hypergraph import csv_to_hypergraph
from brain.hypermatrix import TagMatrix
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

def main():
    start = time.perf_counter()

    store_path = Path(STORE_DIR)
    if store_path.exists():
        shutil.rmtree(store_path)

    hyper_store = Store(store_path)
    hyper_store.bulk_load(path=Path(HYPER_ONTOLOGY), format=RdfFormat.TURTLE)
    print(f"[STATUS] Triplestore created with hypergraph ontology {HYPER_ONTOLOGY}")

    # TODO : get csvs from user
    # csv_to_hypergraph()

    tag_matrix = TagMatrix(hyper_store)

    # TODO : use hyper_matrix and indexes

    hyper_store.clear()
    shutil.rmtree(store_path)
    print(f"[STATUS] Deleted triplestore")
    
    duration = (time.perf_counter() - start) / 60
    print(f"[PERFORMANCE] Total Duration: {duration:.2f} minutes")

if __name__ == "__main__":
    main()
