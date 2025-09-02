# Copyright (c) 2023 NEC Corporation. All Rights Reserved.


import firefw as fire

ARITHMETIC_BINOPS = [
    "add",
    "div",
    "floordiv",
    "mod",
    "mul",
    "pow",
    "sub",
    "truediv",
]
INPLACE_ARITHMETIC_BINOPS = [f"i{op}" for op in ARITHMETIC_BINOPS]
REV_ARITHMETIC_BINOPS = [f"r{op}" for op in ARITHMETIC_BINOPS]
COMPARISON_BINOPS = ["eq", "ge", "gt", "le", "lt", "ne"]
LOGICAL_BINOPS = ["and", "or", "xor"]
INPLACE_LOGICAL_BINOPS = ["iand", "ior", "ixor"]
REV_LOGICAL_BINOPS = ["rand", "ror", "rxor"]

INPLACE_BINOPS = INPLACE_ARITHMETIC_BINOPS + INPLACE_LOGICAL_BINOPS

_binop_vector_vector = {}
_binop_vector_scalar = {}
_binop_table_vector = {}
_binop_table_table = {}
_binop_table_scalar = {}


def is_inplace_binop(op: str):
    return op in INPLACE_BINOPS


def get_binop_vector_scalar(op):
    return _binop_vector_scalar.get(op)


def get_binop_vector_vector(op):
    return _binop_vector_vector.get(op)


def get_binop_table_scalar(op):
    return _binop_table_scalar.get(op)


def get_binop_table_vector(op):
    return _binop_table_vector.get(op)


def get_binop_table_table(op):
    return _binop_table_table.get(op)


# Because current ir.py does not provide opcode for binops, those are created
# here, and stored into dictionaries for the convenience of users.
def _build_binop_opcodes():
    # This function must be consistent with opdefs/fireducks.td

    for op in ARITHMETIC_BINOPS + REV_ARITHMETIC_BINOPS + COMPARISON_BINOPS:
        _binop_vector_vector[op] = fire.Opcode(f"fireducks.{op}.vector.vector")
        _binop_vector_scalar[op] = fire.Opcode(f"fireducks.{op}.vector.scalar")
        _binop_table_scalar[op] = fire.Opcode(f"fireducks.{op}.table.scalar")
        _binop_table_table[op] = fire.Opcode(f"fireducks.{op}.table.table")
        _binop_table_vector[op] = fire.Opcode(f"fireducks.{op}.table.vector")

    # TODO: implement logical binops for table_scalar, table_table,
    # table_vector
    for op in LOGICAL_BINOPS:
        _binop_vector_scalar[op] = fire.Opcode(f"fireducks.{op}.vector.scalar")
        _binop_vector_vector[op] = fire.Opcode(f"fireducks.{op}.vector.vector")

    # IR does not have rev logical binops.
    # registering (rand, ror, rxor) as (and, or, xor) respectively
    for op in REV_LOGICAL_BINOPS:
        _op = op[1:]
        _binop_vector_scalar[op] = _binop_vector_scalar[_op]
        _binop_vector_vector[op] = _binop_vector_vector[_op]


_build_binop_opcodes()
