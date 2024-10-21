from pyformlang.cfg import CFG, Terminal, Production, Epsilon
import networkx as nx


def cfg_to_weak_normal_form(cfg: CFG) -> CFG:
    eps_term = Terminal("_EPSILON_")
    while eps_term in cfg.terminals or eps_term in cfg.variables:
        eps_term = Terminal(f"_{eps_term}_")

    cfg = CFG(
        start_symbol=cfg.start_symbol,
        productions={
            Production(
                head=production.head,
                body=[
                    obj if not isinstance(obj, Epsilon) else eps_term
                    for obj in production.body
                ]
                if len(production.body) > 0
                else [eps_term],
            )
            for production in cfg.productions
        },
    )

    cfg = cfg.to_normal_form()

    cfg = CFG(
        start_symbol=cfg.start_symbol,
        productions={
            Production(
                head=production.head,
                body=[obj if obj != eps_term else Epsilon() for obj in production.body],
            )
            for production in cfg.productions
        },
    )

    return cfg


def term_to_vars(cfg: CFG) -> dict:
    acc = {}
    for production in cfg.productions:
        if len(production.body) == 1 and isinstance(production.body[0], Terminal):
            acc.setdefault(production.body[0], set()).add(production.head)

    return acc


def vars_body_to_head(cfg: CFG) -> dict:
    acc = {}
    for production in cfg.productions:
        if len(production.body) == 2:
            acc.setdefault(tuple(production.body), set()).add(production.head)

    return acc


def hellings_based_cfpq(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    wnf = cfg_to_weak_normal_form(cfg)

    edges = {(v1, Terminal(label), v2) for (v1, v2, label) in graph.edges.data("label")}

    ttv = term_to_vars(wnf)
    vbth = vars_body_to_head(wnf)

    eval_edges = set(
        {(v1, var, v2) for (v1, term, v2) in edges if term in ttv for var in ttv[term]}
    )

    for v in graph.nodes:
        for var in wnf.get_nullable_symbols():
            eval_edges.add((v, var, v))

    edges_queue = list(eval_edges)

    def process_update(e1, e2, buffer: set):
        st1, x, fn1 = e1
        st2, y, fn2 = e2
        xy = tuple([x, y])

        if st2 == fn1 and xy in vbth:
            for var in vbth[xy]:
                reduce_edge = (st1, var, fn2)
                if reduce_edge not in eval_edges:
                    buffer.add(reduce_edge)
                    edges_queue.append(reduce_edge)

    while edges_queue:
        e1 = edges_queue.pop(0)
        buffer = set()
        for e2 in eval_edges:
            process_update(e1, e2, buffer)
            process_update(e2, e1, buffer)
        eval_edges |= buffer

    pairs = {
        (v1, v2)
        for v1, var, v2 in eval_edges
        if v1 in start_nodes
        and var.value == wnf.start_symbol.value
        and v2 in final_nodes
    }

    return pairs
