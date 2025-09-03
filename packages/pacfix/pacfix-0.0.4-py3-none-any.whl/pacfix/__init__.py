from typing import NamedTuple, List, Dict, Set, Tuple

from .invariant import InvariantManager, LiveVariable
from .synthesis import Synthesizer
from .utils import calculate_pac, filter_duplicate
from .debug import enable_debug, disable_debug, print_debug, print_warning

__all__ = ["__version__", "Result", "learn"]
__version__ = "0.0.4"


class Result(NamedTuple):
    size_orig: int
    size_final: int
    samples_neg: int
    samples_pos: int
    pac_epsilon: float
    pac_epsilon_no_uniq: float
    # TODO: move InvariantManager.dump out
    # and pass around just List[Invariant]
    inv_mgr: InvariantManager


def learn(live_vars: Dict[int, LiveVariable],
          neg_vals_init: List[Dict[int, int]],
          pos_vals_init: List[Dict[int, int]],
          pac_delta: float):
    synthesizer = Synthesizer(live_vars)
    hypothesis_space = synthesizer.synthesize()
    size_orig = len(hypothesis_space)

    neg_vals = filter_duplicate(neg_vals_init)
    pos_vals = filter_duplicate(pos_vals_init)
    refined_space = synthesizer.validate(hypothesis_space, neg_vals, pos_vals)

    samples = len(neg_vals) + len(pos_vals)
    pac_epsilon = calculate_pac(samples, size_orig, pac_delta)
    samples_no_uniq = len(neg_vals_init) + len(pos_vals_init)
    pac_epsilon_no_uniq = calculate_pac(samples_no_uniq, size_orig, pac_delta)

    inv_manager = InvariantManager(live_vars)
    inv_manager.reduce()
    for inv in refined_space:
        inv_manager.add_invariant(inv)
    return Result(size_orig, len(refined_space),
        len(neg_vals), len(pos_vals),
        pac_epsilon, pac_epsilon_no_uniq, inv_manager)
