# This file contains test cases that you need to pass to get a grade
# You MUST NOT touch anything here except ONE block below
# You CAN modify this file IF AND ONLY IF you have found a bug and are willing to fix it
# Otherwise, please report it
from copy import deepcopy
import pytest
from grammars_constants import REGEXP_CFG, GRAMMARS, GRAMMARS_DIFFERENT, CFG_EBNF
from helper import generate_rnd_start_and_final
from rpq_template_test import (
    rpq_cfpq_test,
    different_grammars_test,
    cfpq_algorithm_test,
)
from cfpq_concrete_cases import CASES_CFPQ, CaseCFPQ

# Fix import statements in try block to run tests
try:
    from project.task6 import hellings_based_cfpq
    from project.task7 import matrix_based_cfpq
    from project.tensor_based_cfpq import tensor_based_cfpq, cfg_to_rsm, ebnf_to_rsm
except ImportError:
    pytestmark = pytest.mark.skip("Task 8 is not ready to test!")


class TestTensorBasedCFPQ:
    @pytest.mark.parametrize("case", CASES_CFPQ)
    def test_concrete_cases(self, case: CaseCFPQ):
        case.check_answer_rsm(tensor_based_cfpq, cfg_to_rsm)

    @pytest.mark.parametrize("regex_str, cfg_list", REGEXP_CFG)
    def test_rpq_cfpq_tensor(self, graph, regex_str, cfg_list) -> None:
        cfg_list_rsm = [cfg_to_rsm(grammar) for grammar in cfg_list]
        rpq_cfpq_test(graph, regex_str, cfg_list_rsm, tensor_based_cfpq)

    @pytest.mark.parametrize("eq_grammars", GRAMMARS)
    def test_different_grammars(self, graph, eq_grammars):
        eq_grammars_rsm = [cfg_to_rsm(grammar) for grammar in eq_grammars]
        different_grammars_test(graph, eq_grammars_rsm, tensor_based_cfpq)

    @pytest.mark.parametrize("cfg_list, ebnf_list", CFG_EBNF)
    def test_cfpq_tensor(self, graph, cfg_list, ebnf_list):
        cfpq_algorithm_test(
            graph, ebnf_list, cfg_list, ebnf_to_rsm, cfg_to_rsm, tensor_based_cfpq
        )

    @pytest.mark.parametrize("grammar", GRAMMARS_DIFFERENT)
    def test_hellings_matrix_tensor(self, graph, grammar):
        start_nodes, final_nodes = generate_rnd_start_and_final(graph)
        hellings = hellings_based_cfpq(
            deepcopy(grammar), deepcopy(graph), start_nodes, final_nodes
        )
        matrix = matrix_based_cfpq(
            deepcopy(grammar), deepcopy(graph), start_nodes, final_nodes
        )
        tensor = tensor_based_cfpq(
            cfg_to_rsm(deepcopy(grammar)), deepcopy(graph), start_nodes, final_nodes
        )
        assert (hellings == matrix) and (matrix == tensor)
