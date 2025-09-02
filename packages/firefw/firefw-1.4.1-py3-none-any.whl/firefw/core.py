# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

"""FIRE Runtime module
"""

# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring

from logging import getLogger

import weakref

logger = getLogger(__name__)


class Opcode:
    """Opcode of IR

    You can define your own opcode.
    """

    def __init__(self, opcode):
        """Constructor.

        Args:
            opcode(str) : Name of opcode
        """
        self.__opcode = opcode

    def __str__(self):
        return self.__opcode

    @property
    def name(self):
        return self.__opcode


class Type:
    def __init__(self, mlir_type, is_mutable=False):
        assert isinstance(mlir_type, str)
        self._mlir_type = mlir_type
        self._is_mutable = is_mutable

    @property
    def mlir_type(self):
        return self._mlir_type

    def is_mutable(self):
        return self._is_mutable


class Value:
    """Value is a placeholder for a result of deferred computation."""

    def __init__(self, ty: Type, name: str, is_attr: bool = False):
        assert isinstance(ty, Type)  # FIXME: no more required?
        self.__is_available = False
        self.__def_op = None
        self.__type = ty
        self.__name = name
        self.__bound_to = None
        self.__is_attr = is_attr

    @property
    def mlir_type(self):
        return self.__type.mlir_type

    def type(self):
        return self.__type

    def is_attr(self):
        return self.__is_attr

    def isType(self, ty):
        return self.__type == ty

    # TODO: Rename to get?
    def get_result(self):
        """Returns a result of deferred computation.

        This method has to be called when :func:`is_available` is true.
        """
        assert self.is_available()
        return self.__result

    def emplace(self, result):
        logger.debug("Value.emplace: %s %s#%x", self, type(result), id(result))
        assert not self.__is_available
        self.__result = result
        self.__is_available = True
        # once result is computed, resetting def_op to None to avoid
        # memory leak issue due to circular reference: GT #2664
        self.__def_op = None

    def _explain(self):
        ret = self.__name
        if self.__def_op is not None:
            ret += " : " + self.get_def().opcode.name
        return ret

    def is_available(self):
        """Returns True if this value is already evaluated."""
        return self.__is_available

    def set_def(self, op):
        # logger.debug('fire.Value.set_def: op=%s', op.opcode)
        self.__def_op = op

    def get_def(self):
        """Returns an operation which defines this value."""
        assert self.__def_op is not None
        return self.__def_op

    def set_name(self, name):
        self.__name = name

    def bind(self, obj):
        logger.debug(
            "Value.bind: self=%s to %s.%s#%x",
            self,
            type(obj).__module__,
            type(obj).__name__,
            id(obj),
        )
        assert self.__bound_to is None
        # using weakref to solve memory leak issue: GT #2664
        self.__bound_to = weakref.ref(obj)
        logger.debug(f"{self._explain()} -> {self.__bound_to} created")

    def unbind(self):
        assert self.__bound_to is not None
        tmp = self.__bound_to()
        self.__bound_to = None
        return tmp

    def get_bound_obj(self):
        # either the value is not yet bound or already has been unbound
        if self.__bound_to is None:
            return None
        return self.__bound_to()

    def name(self):
        assert self.__name is not None
        return self.__name

    def __str__(self):
        return self.__name or f"Value#{id(self):x}"


class Operation:
    """Operation class.

    Args:
       opcode(fire.Opcode): opcode
       outs(list[fire.Value]): outputs
       ins(list[any]): inputs
       deps(list[Operation]): ops on which this op depends
    """

    def __init__(self, builder, opcode, outs, ins, deps):
        self.__builder = builder
        self.__opcode = opcode
        self.__outs = outs
        self.__ins = ins
        self.__deps = deps

    #        logger.debug('fire.Operation.__init__: %s len(outs)=%d',
    #                     opcode, len(outs))

    @property
    def opcode(self):
        return self.__opcode

    @property
    def builder(self):
        return self.__builder

    @property
    def outs(self):
        return self.__outs

    @property
    def ins(self):
        return self.__ins

    @property
    def deps(self):
        return self.__deps

    def find_output_chain(self):
        # output chain must be last output
        if self.__outs and self.__outs[-1].isType(ChainType):
            return self.__outs[-1]
        return None

    @property
    def input_chain(self):
        return self.__input_chain

    def __str__(self):
        ins = ", ".join([str(a) for a in self.__ins[:100]])
        if len(self.__ins) > 100:
            ins += ", ..."
        if self.__outs:
            outs = ", ".join([str(o) for o in self.__outs])
            return f"{outs} = {self.__opcode}({ins})"
        return f"{self.__opcode}({ins})"


# builtin types and ops
ChainType = Type("!tfrt.chain")
MergeChainsOp = Opcode("tfrt.merge.chains")
NewChainOp = Opcode("tfrt.new.chain")
