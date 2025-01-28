import itertools
from scipy.sparse import csc_matrix
from pyformlang.finite_automaton import Symbol, State
from pyformlang.rsa import RecursiveAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.cfg import CFG, Production
from project.task3 import intersect_automata, AdjacencyMatrixFA, get_edges_from_fa

__all__ = ["cfg_to_rsm", "ebnf_to_rsm", "tensor_based_cfpq"]


def cfg_to_text(cfg: CFG) -> str:
    productions = [
        f"{prod.head} -> {' '.join(str(x.value) for x in prod.body)}"
        for prod in cfg.productions
    ]
    return "\n".join(productions) + "\n"


def cfg_to_rsm(cfg: CFG) -> RecursiveAutomaton:
    normalized_cfg = cfg.to_normal_form()
    if cfg.generate_epsilon():
        epsilon_production = Production(normalized_cfg.start_symbol, [])
        normalized_cfg = CFG(
            start_symbol=normalized_cfg.start_symbol,
            productions=list(normalized_cfg.productions) + [epsilon_production],
        )
    return RecursiveAutomaton.from_text(cfg_to_text(normalized_cfg), cfg.start_symbol)


def ebnf_to_rsm(ebnf: str) -> RecursiveAutomaton:
    return RecursiveAutomaton.from_text(ebnf)


def rsm_to_nfa(rsm: RecursiveAutomaton) -> NondeterministicFiniteAutomaton:
    def create_state(symbol: Symbol, state: State) -> State:
        return State((symbol, state.value))

    boxes = rsm.boxes
    start_states = set()
    final_states = set()
    transitions = []

    for symbol, box in boxes.items():
        for st1, label, st2 in get_edges_from_fa(box.dfa):
            new_st1, new_st2 = create_state(symbol, st1), create_state(symbol, st2)
            transitions.append((new_st1, label, new_st2))

        for start in box.start_state:
            start_states.add(create_state(symbol, start))

        for final in box.final_states:
            final_states.add(create_state(symbol, final))

    nfa = NondeterministicFiniteAutomaton(
        start_state=start_states, final_states=final_states
    )
    nfa.add_transitions(transitions)
    return nfa


def tensor_based_cfpq(
    rsm: RecursiveAutomaton,
    graph_nfa: NondeterministicFiniteAutomaton,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    def get_graph_delta(
        closure: csc_matrix, intersection: AdjacencyMatrixFA
    ) -> dict[Symbol, csc_matrix]:
        def unpack_state(state: State) -> tuple[State, State]:
            return State(state[0]), State(state[1])

        def get_label(state: State) -> Symbol:
            return state.value.value[0]

        delta = {}
        for idx1, idx2 in zip(*closure.nonzero()):
            state1, state2 = (
                intersection.idx_by_state[idx1],
                intersection.idx_by_state[idx2],
            )
            graph_state1, rsm_state1 = unpack_state(state1)
            graph_state2, rsm_state2 = unpack_state(state2)

            graph_idx1, graph_idx2 = (
                graph_matrix.states[graph_state1],
                graph_matrix.states[graph_state2],
            )

            assert get_label(rsm_state1) == get_label(rsm_state2)

            if not (
                rsm_matrix.states[rsm_state1] in rsm_matrix.start_states
                and rsm_matrix.states[rsm_state2] in rsm_matrix.final_states
            ):
                continue

            label = get_label(rsm_state1)
            n = len(graph_matrix.states)
            if (
                label not in graph_matrix.matricies
                or not graph_matrix.matricies[label][graph_idx1, graph_idx2]
            ):
                delta.setdefault(label, csc_matrix((n, n), dtype=bool))[
                    graph_idx1, graph_idx2
                ] = True

        return delta

    rsm_nfa = rsm_to_nfa(rsm)
    graph_matrix = AdjacencyMatrixFA(graph_nfa)
    rsm_matrix = AdjacencyMatrixFA(rsm_nfa)

    while True:
        intersection_matrix = intersect_automata(graph_matrix, rsm_matrix)
        closure = intersection_matrix.transitive_closure()
        graph_delta = get_graph_delta(closure, intersection_matrix)
        if not graph_delta:
            break
        graph_matrix.update_matricies(graph_delta)

    start_symbol = rsm.initial_label

    if start_symbol in graph_matrix.matricies:
        start_matrix = graph_matrix.matricies[start_symbol]
        return {
            (start, final)
            for start, final in itertools.product(start_nodes, final_nodes)
            if start_matrix[
                graph_matrix.states[State(start)], graph_matrix.states[State(final)]
            ]
        }

    return set()
