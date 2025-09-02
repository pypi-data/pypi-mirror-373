# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import sys
import ast
import operator
import numpy as np
from typing import ChainMap
from functools import reduce

from pandas.core.computation.expr import (
    _preparse,
    _compose,
    _replace_locals,
    _replace_booleans,
    _rewrite_assign,
)
from pandas.core.computation.parsing import clean_backtick_quoted_toks

BACKTICK_QUOTED_STRING = 100
LOCAL_TAG = "__pd_eval_local_"


def _in(x, y):
    """
    Compute the vectorized membership of ``x in y`` if possible, otherwise
    use Python.
    """
    try:
        return x.isin(y)
    except AttributeError:
        # if is_list_like(x):
        #     try:
        #         return y.isin(x)
        #     except AttributeError:
        #         pass
        return x in y


def _not_in(x, y):
    """
    Compute the vectorized membership of ``x not in y`` if possible,
    otherwise use Python.
    """
    try:
        return ~x.isin(y)
    except AttributeError:
        # if is_list_like(x):
        #     try:
        #         return ~y.isin(x)
        #     except AttributeError:
        #         pass
        return x not in y


CMP_OPS_SYMS = (">", "<", ">=", "<=", "==", "!=", "in", "not in")
_cmp_ops_funcs = (
    operator.gt,
    operator.lt,
    operator.ge,
    operator.le,
    operator.eq,
    operator.ne,
    _in,
    _not_in,
)
_cmp_ops_dict = dict(zip(CMP_OPS_SYMS, _cmp_ops_funcs))

BOOL_OPS_SYMS = ("&", "|", "and", "or")
_bool_ops_funcs = (operator.and_, operator.or_, operator.and_, operator.or_)
_bool_ops_dict = dict(zip(BOOL_OPS_SYMS, _bool_ops_funcs))

ARITH_OPS_SYMS = ("+", "-", "*", "/", "**", "//", "%")
_arith_ops_funcs = (
    operator.add,
    operator.sub,
    operator.mul,
    operator.truediv,
    operator.pow,
    operator.floordiv,
    operator.mod,
)
_arith_ops_dict = dict(zip(ARITH_OPS_SYMS, _arith_ops_funcs))

_binary_ops_dict = {}
for d in (_cmp_ops_dict, _bool_ops_dict, _arith_ops_dict):
    _binary_ops_dict.update(d)

UNARY_OPS_SYMS = ("+", "-", "~", "not")
_unary_ops_funcs = (
    operator.pos,
    operator.neg,
    operator.invert,
    operator.invert,
)
_unary_ops_dict = dict(zip(UNARY_OPS_SYMS, _unary_ops_funcs))

DEFAULT_GLOBALS = {
    # "Timestamp": Timestamp,
    # "datetime": datetime.datetime,
    # "True": True,
    # "False": False,
    "list": list,
    "tuple": tuple,
    "inf": np.inf,
    "Inf": np.inf,
}


class QueryParser(ast.NodeVisitor):
    binary_ops = CMP_OPS_SYMS + BOOL_OPS_SYMS + ARITH_OPS_SYMS
    binary_op_nodes = (
        "Gt",
        "Lt",
        "GtE",
        "LtE",
        "Eq",
        "NotEq",
        "In",
        "NotIn",
        "BitAnd",
        "BitOr",
        "And",
        "Or",
        "Add",
        "Sub",
        "Mult",
        "Div",
        "Pow",
        "FloorDiv",
        "Mod",
    )
    binary_op_nodes_map = dict(zip(binary_ops, binary_op_nodes))

    unary_ops = UNARY_OPS_SYMS
    unary_op_nodes = "UAdd", "USub", "Invert", "Not"
    unary_op_nodes_map = dict(zip(unary_ops, unary_op_nodes))

    def __init__(self, df, level, local_dict=None, **kwargs):
        self._df = df
        frame = sys._getframe(level)
        self.scope = ChainMap(
            local_dict or frame.f_locals.copy(), frame.f_globals.copy()
        )
        self.quoted = ChainMap()

        for bin_op in self.binary_ops:
            bin_node = self.binary_op_nodes_map[bin_op]
            setattr(
                self,
                f"visit_{bin_node}",
                lambda node, bin_op=bin_op: _binary_ops_dict[bin_op],
            )

        for unary_op in self.unary_ops:
            unary_node = self.unary_op_nodes_map[unary_op]
            setattr(
                self,
                f"visit_{unary_node}",
                lambda node, unary_op=unary_op: _unary_ops_dict[unary_op],
            )

    def _clean_backtick_quoted_toks(self, token):
        ret = clean_backtick_quoted_toks(token)
        if ret != token:
            before_toknum, before_tokval = token
            after_toknum, after_tokval = ret
            self.quoted[after_tokval] = before_tokval
        return ret

    def visit(self, node, **kwargs):
        if isinstance(node, str):
            clean = _preparse(
                node,
                f=_compose(
                    _replace_locals,
                    _replace_booleans,
                    _rewrite_assign,
                    self._clean_backtick_quoted_toks,
                ),
            )
            node = ast.parse(clean)
        method = "visit_" + type(node).__name__
        visitor = getattr(self, method)
        return visitor(node, **kwargs)

    def visit_Module(self, node, **kwargs):
        if len(node.body) != 1:
            raise SyntaxError("only a single expression is allowed")
        expr = node.body[0]
        return self.visit(expr, **kwargs)

    def visit_Expr(self, node, **kwargs):
        return self.visit(node.value, **kwargs)

    def visit_BinOp(self, node, **kwargs):
        left = self.visit(node.left, side="left")
        right = self.visit(node.right, side="right")
        op = self.visit(node.op)
        return op(left, right)

    def visit_UnaryOp(self, node, **kwargs):
        if isinstance(node.op, ast.UAdd):
            return self.visit(node.operand)
        operand = self.visit(node.operand)
        op = self.visit(node.op)
        return op(operand)

    def visit_Name(self, node, **kwargs):
        name = node.id

        if name.startswith(LOCAL_TAG):
            local_name = name.replace(LOCAL_TAG, "")
            return self.scope[local_name]

        if name in DEFAULT_GLOBALS:
            return DEFAULT_GLOBALS[name]

        if name in self.quoted:
            name = self.quoted[name]

        return self._df.__getitem__(name)

    def visit_Constant(self, node, **kwargs):
        return node.n

    def visit_List(self, node, **kwargs):
        return [self.visit(e) for e in node.elts]

    visit_Tuple = visit_List

    def visit_Call(self, node, side=None, **kwargs):
        res = self.visit(node.func)

        new_args = [self.visit(arg) for arg in node.args]
        for key in node.keywords:
            if not isinstance(key, ast.keyword):
                # error: "expr" has no attribute "id"
                raise ValueError(
                    f"keyword error in function call '{node.func.id}'"
                )  # type: ignore[attr-defined]

            if key.arg:
                kwargs[key.arg] = self.visit(key.value).value

        return res(*new_args, **kwargs)

    def translate_In(self, op):
        return op

    def visit_Compare(self, node, **kwargs):
        ops = node.ops
        comps = node.comparators

        # base case: we have something like a CMP b
        if len(comps) == 1:
            op = self.translate_In(ops[0])
            binop = ast.BinOp(op=op, left=node.left, right=comps[0])
            return self.visit(binop)

        # recursive case: we have a chained comparison, a CMP b CMP c, etc.
        left = node.left
        values = []
        for op, comp in zip(ops, comps):
            new_node = self.visit(
                ast.Compare(
                    comparators=[comp], left=left, ops=[self.translate_In(op)]
                )
            )
            left = comp
            values.append(new_node)
        return self.visit(ast.BoolOp(op=ast.And(), values=values))

    def _try_visit_binop(self, bop):
        if isinstance(bop, ast.AST):
            return self.visit(bop)
        return bop

    def visit_BoolOp(self, node, **kwargs):
        def visitor(x, y):
            lhs = self._try_visit_binop(x)
            rhs = self._try_visit_binop(y)
            op = self.visit(node.op)
            return op(lhs, rhs)

        operands = node.values
        return reduce(visitor, operands)
