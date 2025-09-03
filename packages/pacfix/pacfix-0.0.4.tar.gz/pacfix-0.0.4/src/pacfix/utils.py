import os
import math
from typing import List, Dict, TextIO, Tuple, Set

from .invariant import LiveVariable, VarType
from .debug import print_debug

def get_valuations(input_dir: str) -> List[str]:
    if not os.path.exists(input_dir):
        print_debug(f"Directory {input_dir} does not exist")
        return list()
    valuations = list()
    for file in os.listdir(input_dir):
        with open(os.path.join(input_dir, file), "r") as f:
            valuations.append(f.read())
    return valuations

# parse valuation and returns neg, pos valuations
def parse_valuation(neg: List[str], pos: List[str]) -> Tuple[List[Dict[int, int]], List[Dict[int, int]]]:
    neg_vals = list()
    pos_vals = list()
    for valuation in neg:
        groups: List[Dict[int, int]] = list()
        in_group = False
        val_map: Dict[int, int] = dict()
        for line in valuation.split("\n"):
            if line.startswith("#") or len(line) < 3:
                continue
            if line.startswith("[begin]"):
                in_group = True
                val_map = dict()
            elif line.startswith("[end]"):
                in_group = False
                groups.append(val_map)                
            elif in_group:
                id, val = line.split()
                val_map[int(id)] = int(val)
        # Only last one is negative
        for i in range(len(groups)):
            val_map = groups[i]
            if i < len(groups) - 1:
                pos_vals.append(val_map)
            else:
                neg_vals.append(val_map)
    for valuation in pos:
        groups = list()
        in_group = False
        val_map = dict()
        for line in valuation.split("\n"):
            if line.startswith("#") or len(line) < 3:
                continue
            if line.startswith("[begin]"):
                in_group = True
                val_map = dict()
            elif line.startswith("[end]"):
                in_group = False
                groups.append(val_map)                
            elif in_group:
                id, val = line.split()
                val_map[int(id)] = int(val)
        for val_map in groups:
            pos_vals.append(val_map)
    return neg_vals, pos_vals

def parse_valuations_uni(neg: List[str], pos: List[str]) -> Tuple[List[Dict[int, int]], List[Dict[int, int]]]:
    neg_vals = list()
    pos_vals = list()
    for valuation in neg:
        groups: List[Dict[int, int]] = list()
        val_map: Dict[int, int] = dict()
        for line in valuation.split("\n"):
            if line.startswith("#") or len(line) < 3:
                continue
            if line.startswith("----------------------------"):
                groups.append(val_map)
                val_map = dict() 
            elif line.startswith("__valuation:"):
                value_str = line.removeprefix("__valuation:").strip()
                tokens = value_str.split()
                id = tokens[4].strip()
                val = tokens[5].strip()
                val_map[int(id)] = int(val)
        # Only last one is negative
        for i in range(len(groups)):
            val_map = groups[i]
            if i < len(groups) - 1:
                pos_vals.append(val_map)
            else:
                neg_vals.append(val_map)
    for valuation in pos:
        groups = list()
        in_group = False
        val_map = dict()
        for line in valuation.split("\n"):
            if line.startswith("#") or len(line) < 3:
                continue
            if line.startswith("----------------------------"):
                groups.append(val_map)
                val_map = dict() 
            elif line.startswith("__valuation:"):
                value_str = line[len("__valuation:"):].strip()
                tokens = value_str.split()
                id = tokens[4].strip()
                val = tokens[5].strip()
                val_map[int(id)] = int(val)
        for val_map in groups:
            pos_vals.append(val_map)
    return neg_vals, pos_vals

def filter_duplicate(valuations: List[Dict[int, int]]) -> List[Dict[int, int]]:
    seen = set()
    result = list()
    for val in valuations:
        key = frozenset(val.items())
        if key not in seen:
            seen.add(key)
            result.append(val)
    return result


def get_live_vars(live_vars_file: TextIO) -> Dict[int, LiveVariable]:
    live_vars = dict()
    for line in live_vars_file:
        line = line.strip()
        if len(line) > 2:
            id, name, var_type = line.split()
            live_vars[int(id)] = LiveVariable(int(id), name, var_type)
    return live_vars


def get_lv_file(lv_file: TextIO) -> Set[str]:
    return set(filter(None, map(str.strip, lv_file)))


def calculate_pac(samples: int, hypothesis_space: int, delta: float) -> float:
    if hypothesis_space == 0 or samples == 0:
        return 0
    return (1 / samples) * (math.log(hypothesis_space) + (math.log(1 / delta)))