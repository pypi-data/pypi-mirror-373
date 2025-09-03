# iterate over the iris and literals to build a 32-bit index
# hashing causes collisions
from .main import DB, log
import igraph as ig
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

NO_WALKS = 100
MAX_WALK_LENGTH = 15


def generate_walks(args):
    s, graph, small_big = args
    walks = set()
    for _ in range(NO_WALKS):
        walk = graph.random_walk(s, MAX_WALK_LENGTH, return_type="vertices")
        walks.add(tuple(small_big[node] for node in walk))
    return s, walks


def build_rdf2vec():
    cursor = DB.cursor()
    cursor.execute(
        "create table if not exists random_walks (s ubigint, walks ubigint[])"
    )

    small_big = {}
    big_small = {}
    i = 0
    for row in DB.execute(
        "select hash from iris union select hash from literals"
    ).fetchall():
        h = row[0]
        big_small[h] = i
        small_big[i] = h
        i += 1
    log.debug("Retrieved hashes")

    edges = []
    # props = []
    nodes = set()
    for s, o in DB.execute("select distinct s,o from triples").fetchall():
        edges.append((big_small[s], big_small[o]))
        # props.append(big_small[p])
        nodes.add(s)
        nodes.add(o)
    log.debug("Retrieved triples")

    graph = ig.Graph(n=len(small_big))
    graph.add_edges(edges)
    # graph.es["p_i"] = props

    def generate_walks(s):
        walks = set()
        for _ in range(NO_WALKS):
            walk = graph.random_walk(s, MAX_WALK_LENGTH, return_type="vertices")
            walks.add(tuple(small_big[node] for node in walk))
        return s, list(walks)

    vertices_to_process = [
        big_small[row[0]]
        for row in DB.execute(
            "select T.s from triples T left join random_walks R on T.s = R.s where R.s is null limit 10"
        ).fetchall()
    ]

    results = []
    # Use ThreadPoolExecutor instead of multiprocessing.Pool
    with ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
        # Submit all tasks and collect futures
        future_results = [
            executor.submit(generate_walks, s) for s in vertices_to_process
        ]

        # Get results as they complete
        for future in future_results:
            results.append(future.result())

    cursor.executemany("insert into random_walks (s, walks) values (?, ?)", results)
    cursor.commit()


def xor_fold(x: int) -> int:
    return (x & 0xFFFFFFFF) ^ (x >> 32)


def knuth_hash(x: int) -> int:
    A = 2654435761  # Knuth's magic number
    return (x * A) & 0xFFFFFFFF
