from typing import List, Set, Dict, Tuple, Union

from . import utils
from . import invariant
from .invariant import Invariant, InvariantType
from .debug import print_debug

import enum
import sys

class Synthesizer():
    live_vars: Dict[int, invariant.LiveVariable]
    special_values: List[int]

    def __init__(self, live_vars: Dict[int, invariant.LiveVariable]):
        self.live_vars = live_vars
        self.special_values = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2147483647, 4294967295] # 2048, 4096, 8192, 16384, 32768, 65536, 1048575, 
    
    def get_const_list(self, lowerbound: int, upperbound: int) -> List[int]:
        const_list = list(range(lowerbound, upperbound + 1))
        for i in self.special_values:
            if i > upperbound:
                const_list.append(i)
        return const_list
     
    def gen_eq_const(self, var: List[invariant.LiveVariable]) -> List[Invariant]:
        invariants = list()
        const_list = self.get_const_list(-10, 100)
        for v in var:
            for i in const_list:
                if i == 0:
                    continue
                invariants.append(Invariant(InvariantType.EQ, Invariant(InvariantType.VAR, data=v.id), Invariant(InvariantType.CONST, data=i)))
        return invariants
    
    def gen_zero_non_zero(self, var: List[invariant.LiveVariable]) -> List[Invariant]:
        invariants = list()
        for v in var:
            invariants.append(Invariant(InvariantType.EQ, Invariant(InvariantType.VAR, data=v.id), Invariant(InvariantType.CONST, data=0)))
            invariants.append(Invariant(InvariantType.NE, Invariant(InvariantType.VAR, data=v.id), Invariant(InvariantType.CONST, data=0)))
        return invariants
    
    def gen_ne_const(self, var: List[invariant.LiveVariable]) -> List[Invariant]:
        invariants = list()
        const_list = self.get_const_list(-10, 10)
        for v in var:
            for i in const_list:
                if i == 0:
                    continue
                invariants.append(Invariant(InvariantType.NE, Invariant(InvariantType.VAR, data=v.id), Invariant(InvariantType.CONST, data=i)))
        return invariants
    
    def gen_ge_const(self, var: List[invariant.LiveVariable]) -> List[Invariant]:
        invariants = list()
        const_list = self.get_const_list(-10, 10)
        for v in var:
            for i in const_list:
                invariants.append(Invariant(InvariantType.GE, Invariant(InvariantType.VAR, data=v.id), Invariant(InvariantType.CONST, data=i)))
        return invariants
    
    def gen_le_const(self, var: List[invariant.LiveVariable]) -> List[Invariant]:
        invariants = list()
        const_list = self.get_const_list(-10, 10)
        for v in var:
            for i in const_list:
                invariants.append(Invariant(InvariantType.LE, Invariant(InvariantType.VAR, data=v.id), Invariant(InvariantType.CONST, data=i)))
        return invariants
    
    def gen_ge_var(self, var: List[invariant.LiveVariable]) -> List[Invariant]:
        invariants = list()
        for v1 in var:
            for v2 in var:
                if v1.var_type != v2.var_type:
                    continue
                if v1.id != v2.id:
                    invariants.append(Invariant(InvariantType.GE, Invariant(InvariantType.VAR, data=v1.id), Invariant(InvariantType.VAR, data=v2.id)))
        return invariants

    def gen_diff_ge_const(self, var: List[invariant.LiveVariable]) -> List[Invariant]:
        invariants = list()
        const_list = self.get_const_list(1, 10)
        for v1 in var:
            for v2 in var:
                if v1.id == v2.id:
                    continue
                if v1.var_type != v2.var_type:
                    continue
                for i in const_list:
                    invariants.append(Invariant(InvariantType.GE, Invariant(InvariantType.SUB, Invariant(InvariantType.VAR, data=v1.id), Invariant(InvariantType.VAR, data=v2.id)), Invariant(InvariantType.CONST, data=i)))
        return invariants
    
    def gen_ge_div_const(self, var: List[invariant.LiveVariable]) -> List[Invariant]:
        invariants = list()
        const_list = range(2, 10)
        for v1 in var:
            for v2 in var:
                if v1.id == v2.id:
                    continue
                if v1.var_type != v2.var_type:
                    continue
                for i in const_list:
                    invariants.append(Invariant(InvariantType.LE, Invariant(InvariantType.MUL, Invariant(InvariantType.VAR, data=v1.id), Invariant(InvariantType.CONST, data=i)), Invariant(InvariantType.VAR, data=v2.id)))
        return invariants
    
    
    def evaluate(self, inv: Invariant, vals: Dict[int, int]) -> Union[bool, int]:
        # Evaluate the given invariant on the given patches
        inv_type = inv.inv_type
        if inv_type == InvariantType.VAR:
            return vals[inv.data]
        elif inv_type == InvariantType.CONST:
            return inv.data
        elif inv_type == InvariantType.EQ:
            return self.evaluate(inv.left, vals) == self.evaluate(inv.right, vals)
        elif inv_type == InvariantType.NE:
            return self.evaluate(inv.left, vals) != self.evaluate(inv.right, vals)
        elif inv_type == InvariantType.GT:
            return self.evaluate(inv.left, vals) > self.evaluate(inv.right, vals)
        elif inv_type == InvariantType.GE:
            return self.evaluate(inv.left, vals) >= self.evaluate(inv.right, vals)
        elif inv_type == InvariantType.LT:
            return self.evaluate(inv.left, vals) < self.evaluate(inv.right, vals)
        elif inv_type == InvariantType.LE:
            return self.evaluate(inv.left, vals) <= self.evaluate(inv.right, vals)
        elif inv_type == InvariantType.ADD:
            return self.evaluate(inv.left, vals) + self.evaluate(inv.right, vals)
        elif inv_type == InvariantType.SUB:
            return self.evaluate(inv.left, vals) - self.evaluate(inv.right, vals)
        elif inv_type == InvariantType.MUL:
            return self.evaluate(inv.left, vals) * self.evaluate(inv.right, vals)
        elif inv_type == InvariantType.DIV:
            return self.evaluate(inv.left, vals) // self.evaluate(inv.right, vals)
    
    def synthesize(self) -> List[Invariant]:
        # Synthesize a program that fits the given patches
        # and satisfies the given constraints
        live_vars = list(self.live_vars.values())
        int_live_vars = [v for v in live_vars if v.var_type == utils.VarType.INT]
        invariants = list()
        # Equal to a constant
        invariants.extend(self.gen_eq_const(int_live_vars))
        # Non zero
        invariants.extend(self.gen_zero_non_zero(live_vars))
        # Not equal to a constant
        invariants.extend(self.gen_ne_const(int_live_vars))
        # Greater than or equal to a constant
        invariants.extend(self.gen_ge_const(int_live_vars))
        # Less than or equal to a constant
        invariants.extend(self.gen_le_const(int_live_vars))
        # Greater than or equal to a variable
        invariants.extend(self.gen_ge_var(live_vars))
        # Diff greater or equal than a constant
        invariants.extend(self.gen_diff_ge_const(live_vars))
        # Div result greater than a constant
        invariants.extend(self.gen_ge_div_const(live_vars))
        return invariants
        
    def validate(self, hypothesis_space: List[Invariant], neg_vals, pos_vals) -> List[Invariant]:
        # Reduce the given patches to a minimal set
        # that still satisfies the given constraints
        refined = list()
        for inv in hypothesis_space:
            valid = True
            # negative validation: invariant should be false
            for vals in neg_vals:
                if self.evaluate(inv, vals):
                    valid = False
                    break
            if not valid:
                print_debug(f"Invalid neg: {inv} from {vals}")
                continue
            # positive validation: invariant should be true
            for vals in pos_vals:
                if not self.evaluate(inv, vals):
                    valid = False
                    print_debug(f"Invalid pos: {inv} from {vals}")
                    break
            if valid:
                refined.append(inv)
        return refined
    
    