from pyformlang.cfg import CFG, Terminal
from itertools import product
import networkx as nx
from scipy.sparse import csc_matrix
from typing import Set
from project.task6 import cfg_to_weak_normal_form, term_to_vars, vars_body_to_head


def matrix_based_cfpq(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> set[tuple[int, int]]:
    wnf = cfg_to_weak_normal_form(cfg)
    ttv = term_to_vars(wnf)
    vbth = vars_body_to_head(wnf)

    n = graph.number_of_nodes()
    node_by_idx = {i: node for i, node in enumerate(graph.nodes)}
    node_idx = {node: i for i, node in node_by_idx.items()}

    matricies = {var: csc_matrix((n, n), dtype=bool) for var in wnf.variables}

    for v1, v2, label in graph.edges.data("label"):
        tv = ttv.get(Terminal(label), set())
        i1, i2 = node_idx[v1], node_idx[v2]
        for var in tv:
            matricies[var][i1, i2] = True

    for v, vn in product(graph.nodes, wnf.get_nullable_symbols()):
        i = node_idx[v]
        matricies[vn][i, i] = True

    updated = list(wnf.variables)
    while updated:
        cur = updated.pop(0)
        for body, heads in vbth.items():
            if cur not in body:
                continue
            for head in heads:
                old_matrix = matricies[head]
                matricies[head] += matricies[body[0]] @ matricies[body[1]]
                if matricies[head].nnz > old_matrix.nnz:
                    updated.append(head)

    st = wnf.start_symbol
    if st not in matricies:
        return set()

    return {
        (node_by_idx[i1], node_by_idx[i2])
        for i1, i2 in zip(*matricies[st].nonzero())
        if node_by_idx[i1] in start_nodes and node_by_idx[i2] in final_nodes
    }
