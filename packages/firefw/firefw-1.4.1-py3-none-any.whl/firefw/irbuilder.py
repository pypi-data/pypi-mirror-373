# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

from logging import getLogger
from typing import List
import firefw as fire

from firefw.core import (
    ChainType,
    MergeChainsOp,
    NewChainOp,
)

logger = getLogger(__name__)


def infer_type(x):
    if isinstance(x, bool):
        return fire.Type("i1")
    elif isinstance(x, float):
        return fire.Type("f64")
    elif isinstance(x, int):
        return fire.Type("i64")
    elif isinstance(x, str):
        return fire.Type("!tfrt.string")
    raise RuntimeError(f"Can not infer type: {type(x)}")


def _get_ops_with_any_inputs_in(ops, values: List[fire.Value]):
    ret = []
    for op in ops:
        if [v for v in op.ins if v in values]:
            ret += [op]
    return ret


def create_deps(ops, ins, implicit_defs):
    deps = []
    # add flow dependency
    for value in ins:
        if not value.is_available():
            deps += [value.get_def()]

    # add anti-depedency
    if implicit_defs:
        anti_deps = _get_ops_with_any_inputs_in(ops, implicit_defs)
        deps += [op for op in anti_deps if op not in deps]

    return deps


class IRBuilder:
    def __init__(self):
        self.__ops = []
        self.__no = 0

    def get_ops(self):
        return self.__ops

    def remove_ops(self, ops):
        logger.debug("IRBuilder.remove_ops: before %d", len(self.__ops))
        self.__ops = [op for op in self.__ops if op not in ops]
        logger.debug("IRBuilder.remove_ops: after %d", len(self.__ops))

        for op in self.__ops[:100]:
            logger.debug("IRBuilder.remove_ops: %s", op)
        if len(self.__ops) > 100:
            logger.debug("IRBuilder.remove_ops: ...")

    def get_or_create_input_chain(self, dep_ops):
        chains = [
            ch
            for ch in [op.find_output_chain() for op in dep_ops]
            if ch is not None
        ]

        if len(chains) == 0:
            # create new chain if all depending ops have no chain but this op
            # requires and input chain
            ch = self.build_op(NewChainOp, [ChainType], []).outs[0]
        elif len(chains) == 1:
            ch = chains[0]
        elif len(chains) > 1:
            ch = self.build_op(MergeChainsOp, [ChainType], chains).outs[0]

        return ch

    def build_op(
        self, opcode, out_types, ins, implicit_defs=[], chaining=False
    ):
        """builds new operation.

        Args:
            opcode(fire.Opcode): opcode of new operation
            out_types(list[str]): output types
            ins(list[Any]): input of new operation
            implicit_defs(list[fire.Value]): Values implicitly defined by the
                                             op
            chaining(bool) : See comment above

        Returns:
            fire.Operation: new operation
        """

        # logger.debug('build_op: %s', opcode)

        def wrap(x):
            if isinstance(x, fire.Value):
                return x
            return self.make_available_value(x, infer_type(x))

        ins = [wrap(v) for v in ins]
        deps = create_deps(self.__ops, ins, implicit_defs)

        # FIXME: chaining is required if one of the inputs are multable(#593).
        # This predicate should check types of inputs. But since we have ops
        # that does not support a chain at the moment, we have an option.

        # chaining
        if chaining:
            ch = self.get_or_create_input_chain(deps)
            ins += [ch]
            deps += [ch.get_def()]
            out_types += [ChainType]

        outs = [self.new_value(t, "v") for t in out_types]
        op = fire.core.Operation(self, opcode, outs, ins, deps)

        for value in outs:
            value.set_def(op)

        self.__ops += [op]
        logger.debug("build_op: %s", op)
        return op

    def make_available_value(self, x, typ):
        v = self.new_value(typ, "c")
        v.emplace(x)
        return v

    def get_ops_with_any_inputs_in(self, values: List[fire.Value]):
        return _get_ops_with_any_inputs_in(self.__ops, values)

    def new_value(self, typ, prefix: str):
        name = f"%{prefix}{self.__no}"
        self.__no += 1
        return fire.Value(typ, name)

    def new_attr(self, typ, name, value):
        v = fire.Value(typ, name, is_attr=True)
        v.emplace(value)
        return v
