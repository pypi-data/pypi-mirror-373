from typing import List, Set, Dict, Optional, TextIO
import enum
import pysmt.shortcuts as smt
import pysmt.typing as smt_type
import pysmt.fnode
import pysmt
import os
import traceback
from .debug import check_debug, enable_debug, disable_debug, print_debug, print_warning

class VarType(enum.Enum):
    INT = 0
    BOOL = 1
    PTR = 2

class LiveVariable():
    id: int
    name: str
    var_type: VarType
    var: pysmt.fnode.FNode
    def __init__(self, id: int, name: str, var_type: str):
        self.id = id
        self.name = name
        if var_type == "int":
            self.var_type = VarType.INT
            self.var = smt.Symbol(name, smt_type.INT)
        elif var_type == "bool":
            self.var_type = VarType.BOOL
            self.var = smt.Symbol(name, smt_type.INT)
        else:
            self.var_type = VarType.PTR
            self.var = smt.Symbol(name, smt_type.INT)

    def __str__(self):
        return f"LiveVariable(id={self.id}, name={self.name}, var_type={self.var_type})"

    def __repr__(self):
        return self.__str__()

class InvariantType(enum.Enum):
    VAR = 0
    CONST = 1
    EQ = 2
    NE = 3
    GT = 4
    GE = 5
    LT = 6
    LE = 7
    ADD = 8
    SUB = 9
    MUL = 10
    DIV = 11
    AND = 12
    OR = 13
    NOT = 14
    XOR = 15

INVARIANT_MAP = { InvariantType.VAR: "VAR", InvariantType.CONST: "CONST", InvariantType.EQ: "==", InvariantType.NE: "!=", InvariantType.GT: ">", InvariantType.GE: ">=", InvariantType.LT: "<", InvariantType.LE: "<=", InvariantType.ADD: "+", InvariantType.SUB: "-", InvariantType.MUL: "*", InvariantType.DIV: "/", InvariantType.AND: "&&", InvariantType.OR: "||", InvariantType.NOT: "!", InvariantType.XOR: "^"}

class Relation(enum.Enum):
    GT = 1
    EQ = 0
    LT = -1

class Invariant():
    inv_type: InvariantType
    data: int
    left: Optional['Invariant']
    right: Optional['Invariant']

    def __init__(self, inv_type: InvariantType, left: Optional['Invariant'] = None, right: Optional['Invariant'] = None, data: int = 0):
        self.inv_type = inv_type
        if inv_type in [InvariantType.VAR, InvariantType.CONST]:
            self.data = data
            self.left = None
            self.right = None
        elif inv_type == InvariantType.NOT:
            self.data = 0
            self.left = left
            self.right = None
        else:
            self.data = 0
            self.left = left
            self.right = right

    def __str__(self) -> str:
        if self.inv_type == InvariantType.VAR:
            return f"VAR({self.data})"
        elif self.inv_type == InvariantType.CONST:
            return f"CONST({self.data})"
        elif self.inv_type == InvariantType.NOT:
            return f"!({self.left})"
        else:
            return f"({self.left} {INVARIANT_MAP[self.inv_type]} {self.right})"

    def __repr__(self) -> str:
        return str(self)

    def to_str(self, lv: Dict[int, LiveVariable]) -> str:
        if self.inv_type == InvariantType.VAR:
            return lv[self.data].name
        elif self.inv_type == InvariantType.CONST:
            return str(self.data)
        elif self.inv_type == InvariantType.NOT:
            if self.left is None:
                print_warning(f"Not enough child expression for type NOT")
                exit(1)
            return f"!({self.left.to_str(lv)})"
        else:
            if self.left is None or self.right is None:
                print_warning(f"Not enough child expression for type {INVARIANT_MAP[self.inv_type]}: (left {self.left}) (right {self.right})")
                exit(1)
            return f"({self.left.to_str(lv)} {INVARIANT_MAP[self.inv_type]} {self.right.to_str(lv)})"

    def result_type(self, lv: Dict[int, LiveVariable]) -> VarType:
        if self.inv_type == InvariantType.VAR:
            return lv[self.data].var_type
        elif self.inv_type == InvariantType.CONST:
            return VarType.INT
        elif self.inv_type in [InvariantType.ADD, InvariantType.SUB, InvariantType.MUL, InvariantType.DIV]:
            return VarType.INT
        else:
            return VarType.BOOL

    def convert_to_smt(self, lv: Dict[int, LiveVariable]) -> pysmt.fnode.FNode:
        if self.inv_type == InvariantType.VAR:
            return lv[self.data].var
        elif self.inv_type == InvariantType.CONST:
            return smt.Int(self.data)
        elif self.inv_type == InvariantType.NOT:
            if self.left is None:
                print_warning("Not enough child expression for type NOT")
                exit(1)
            elif self.left.result_type(lv) != VarType.BOOL:
                print_warning(f"Type NOT applied for non boolean expression {self.left}")
                exit(1)
            return smt.Not(self.left)
        else:
            if self.left is None or self.right is None:
                print_warning(f"Not enough child expression for type {INVARIANT_MAP[self.inv_type]}: (left {self.left}) (right {self.right})")
                exit(1)
            if self.inv_type in [InvariantType.AND, InvariantType.OR, InvariantType.XOR]:
                if self.left.result_type(lv) != VarType.BOOL or self.right.result_type(lv) != VarType.BOOL:
                    print_warning(f"Wrong result type for type {INVARIANT_MAP[self.inv_type]}: (left {self.left}) (right {self.right})")
                    exit(1)
            elif self.inv_type not in [InvariantType.EQ, InvariantType.NE]:
                if self.left.result_type(lv) != VarType.INT or self.right.result_type(lv) != VarType.INT:
                    print_warning(f"Wrong result type for type {INVARIANT_MAP[self.inv_type]}: (left {self.left}) (right {self.right})")
                    exit(1)
            left = self.left.convert_to_smt(lv)
            right = self.right.convert_to_smt(lv)
            if self.inv_type == InvariantType.EQ:
                return smt.Equals(left, right)
            elif self.inv_type == InvariantType.NE:
                return smt.Not(smt.Equals(left, right))
            elif self.inv_type == InvariantType.GT:
                return smt.GT(left, right)
            elif self.inv_type == InvariantType.GE:
                return smt.GE(left, right)
            elif self.inv_type == InvariantType.LT:
                return smt.LT(left, right)
            elif self.inv_type == InvariantType.LE:
                return smt.LE(left, right)
            elif self.inv_type == InvariantType.ADD:
                return smt.Plus(left, right)
            elif self.inv_type == InvariantType.SUB:
                return smt.Minus(left, right)
            elif self.inv_type == InvariantType.MUL:
                return smt.Times(left, right)
            elif self.inv_type == InvariantType.DIV:
                return smt.And(smt.NotEquals(right, smt.Int(0)), smt.Div(left, right))
            elif self.inv_type == InvariantType.AND:
                return smt.And(left, right)
            elif self.inv_type == InvariantType.OR:
                return smt.Or(left, right)
            elif self.inv_type == InvariantType.XOR:
                return smt.Xor(left, right)

    def compare(self, other: 'Invariant') -> Relation:
        return Relation.EQ

class InvariantVisitor():
    def __init__(self):
        pass

    def visit(self, inv: Invariant):
        if inv.inv_type == InvariantType.VAR:
            self.visit_var(inv)
        elif inv.inv_type == InvariantType.CONST:
            self.visit_const(inv)
        else:
            self.visit_operation(inv)

    def visit_var(self, inv: Invariant):
        pass

    def visit_const(self, inv: Invariant):
        pass

    def visit_operation(self, inv: Invariant):
        if inv.left:
            self.visit(inv.left)
        if inv.right:
            self.visit(inv.right)

class VariableCollector(InvariantVisitor):
    variables: Set[int]
    def __init__(self):
        self.variables = set()

    def visit_var(self, inv: Invariant):
        self.variables.add(inv.data)

    def get_vars(self) -> Set[int]:
        return self.variables

class Lattice:
    inv: Invariant
    id: int
    parent: Set[int]
    children: Set[int]

    def __init__(self, inv: Invariant, id: int):
        self.inv = inv
        self.id = id
        self.parent = set()
        self.children = set()

    def add_parent(self, parent_id: int):
        self.parent.add(parent_id)

    def add_child(self, child_id: int):
        self.children.add(child_id)

    def get_parent(self) -> Set[int]:
        return self.parent

    def get_children(self) -> Set[int]:
        return self.children


class InvariantManager():
    invs: List[Invariant]
    lattice_map: Dict[int, Set[Lattice]]
    live_vars: Dict[int, LiveVariable]
    def __init__(self, live_vars: Dict[int, LiveVariable]):
        self.invs = list()
        self.live_vars = live_vars

    def add_invariant(self, inv: Invariant) -> int:
        self.invs.append(inv)
        return len(self.invs) - 1

    def get_invariant_by_id(self, id: int) -> Optional[Invariant]:
        if id < 0 or id >= len(self.invs):
            return None
        return self.invs[id]

    def add_invariant_to_lattice_recursive(self, parent: Set[Lattice], inv: Lattice):
        pass

    def add_invariant_to_lattice(self, inv: Invariant) -> int:
        inv_id = self.add_invariant(inv)
        lattice = Lattice(inv, inv_id)
        vars = VariableCollector()
        vars.visit(inv)
        for var in vars.get_vars():
            # Get lattice that contains the variable
            if var in self.lattice_map:
                l = self.lattice_map[var]
                self.add_invariant_to_lattice_recursive(l, lattice)
            else:
                # Create a new lattice
                self.lattice_map[var] = set()
                self.lattice_map[var].add(lattice)
        return inv_id

    def get_cond(self, smt_invs: List[pysmt.fnode.FNode]) -> pysmt.fnode.FNode:
        cond = smt.FALSE()
        for inv in smt_invs:
            cond = smt.Or(cond, inv)
        return cond

    def reduce(self):
        store = list()
        for i, inv in enumerate(self.invs):
            store.append(inv.convert_to_smt(self.live_vars))
        cond = self.get_cond(store)
        cond = smt.simplify(cond)

        model = smt.get_model(cond)
        if model:
            print_debug(f"Model: {model}")

    def dump(self, output: TextIO, out_smt_dir: Optional[str]):
        for i, inv in enumerate(self.invs):
            output.write(f"[invariant] [expr {inv.to_str(self.live_vars)}]\n")
            if out_smt_dir is not None:
                smt_inv = inv.convert_to_smt(self.live_vars)
                smt.write_smtlib(smt_inv, f"{out_smt_dir}/{i}.smt")

        if not check_debug():
            return
        # Satisfiability check
        combined_inv = smt.And([inv.convert_to_smt(self.live_vars) for inv in self.invs])
        print_debug(f"Check satisfiability of combined expr: {combined_inv}")
        try:
            if smt.is_valid(combined_inv):
                print_debug(f"Always True")
            elif smt.is_sat(combined_inv):
                print_debug(f"Satisfiable")
            elif smt.is_unsat(combined_inv):
                print_debug(f"Unsat")
            else:
                print_debug(f"Unknown")
        except Exception as e:
            print_debug(f"Error: {type(e).__name__}: {str(e)}")
            traceback.print_exc()
