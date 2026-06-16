from pyoxigraph import Store, NamedNode
from scipy.sparse import coo_array, save_npz
import numpy, time, pickle

# BG-Hypergraph Incidence Matrix
# Rows: HyperNodes
# Columns: HyperArcs
# Arc Tail: -1
# Arc Head: 1

def build_node_index(hyper_store: Store) -> dict[NamedNode, int]:
    query_str = """
        PREFIX tag: <https://theknowledgecommons.org/ns/tagology/>
        SELECT ?node
        WHERE {
            ?node a tag:HyperNode .
        }"""

    index = {}
    for r in hyper_store.query(query_str):
        uri = r['node'].value
        index[uri] = len(index)
    print(f"[STATUS] HyperNode index built with {len(index)} entries")
    return index

def build_arc_index(hyper_store: Store) -> dict[NamedNode, int]:
    query_str = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX tag: <https://theknowledgecommons.org/ns/tagology/>
        SELECT ?arc
        WHERE {
            ?arc a/rdfs:subClassOf+ tag:HyperArc .
        }"""

    index = {}
    for r in hyper_store.query(query_str):
        uri = r['arc'].value
        index[uri] = len(index)
    print(f"[STATUS] HyperArc index built with {len(index)} entries")
    return index

def get_total_incidences(hyper_store:Store) -> int:
    query_str = """
        PREFIX tag: <https://theknowledgecommons.org/ns/tagology/>
        SELECT (COUNT(*) AS ?count)
        WHERE {
            {?arc tag:hasTail ?node .}
            UNION
            {?arc tag:hasHead ?node .}
        }"""
    results = list(hyper_store.query(query_str))
    return int(results[0]['count'].value)

def hypergraph_to_matrix(hyper_store: Store) -> None:
    node_index = build_node_index(hyper_store)
    arc_index = build_arc_index(hyper_store)

    total_incidences = get_total_incidences(hyper_store)
    print(f"Loading {total_incidences} incidences...")
    
    rows = numpy.empty(total_incidences, dtype=numpy.int32)
    cols = numpy.empty(total_incidences, dtype=numpy.int32)
    data = numpy.empty(total_incidences, dtype=numpy.int8)

    tails_query = """
        PREFIX tag: <https://theknowledgecommons.org/ns/tagology/>
        SELECT ?arc ?node
        WHERE {
            ?arc tag:hasTail ?node .
        }"""
    heads_query = """
        PREFIX tag: <https://theknowledgecommons.org/ns/tagology/>
        SELECT ?arc ?node
        WHERE {
            ?arc tag:hasHead ?node .
        }"""

    tails_results = hyper_store.query(tails_query)
    heads_results = hyper_store.query(heads_query)


    k = 0
    for r in tails_results:
        arc = r['arc'].value
        node = r['node'].value

        rows[k] = node_index[node]
        cols[k] = arc_index[arc]
        data[k] = -1

        k += 1
        if k%1_000_000 == 0:
            print(f"[STATUS] Loaded {k:,} incidences")

    for r in heads_results:
        arc = r['arc'].value
        node = r['node'].value

        rows[k] = node_index[node]
        cols[k] = arc_index[arc]
        data[k] = 1

        k += 1
        if k%1_000_000 == 0:
            print(f"[STATUS] Loaded {k:,} incidences")

    assert k == total_incidences, f"Expected {total_incidences:,} incidences but got {k:,}"

    M = coo_array(
        (data, (rows, cols)),
        shape=(len(node_index), len(arc_index)),
        dtype=numpy.int8)
    print(f"[STATUS] Matrix shape: {M.shape}")
    print(f"[STATUS] Matrix nnz: {M.nnz:,}")

    save_npz("scdb_hypermatrix.npz", M)
    with open("node_index.pkl", "wb") as f:
        pickle.dump(node_index, f)
    with open("arc_index.pkl", "wb") as f:
        pickle.dump(arc_index, f)
    print("[STATUS] Saved scdb_hypermatrix.npz, node_index.pkl, arc_index.pkl")

def test() -> None:
    start = time.perf_counter() 
    hyper_store = Store("../scdbTesting/scdb_store")
    hypergraph_to_matrix(hyper_store)
    duration = (time.perf_counter() - start) / 60
    print(f"[PERFORMANCE] Total Duration: {duration:.2f} minutes")

if __name__ == "__main__":
    test()
