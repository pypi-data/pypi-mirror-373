# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

from logging import getLogger
from typing import List
import dis
import inspect
import itertools
import struct
import sys

import firefw as fire
from firefw import tracing

logger = getLogger(__name__)


def _is_interactive():
    import __main__

    return not hasattr(__main__, "__file__")


def prohibit_reentrant(func):
    lock = False

    def wrapper(*args, **kwargs):
        nonlocal lock
        assert not lock
        lock = True
        try:
            ret = func(*args, **kwargs)
        finally:
            lock = False
        return ret

    return wrapper


# TODO: Accept multiple values to be evaluated. Those values should be return
# values of the MLIR function created.
#
# Since this function is not well designed on reentrant, we prohibit it.
@prohibit_reentrant
def evaluate(values: List[fire.Value], executor, package=None):
    """evaluates values.

    Args:
        values(List[fire.Value]): values to be evaluated
        executor: function to execute IR

    Returns:
        any: Evaluated result
    """

    if all([v.is_available() for v in values]):
        return [v.get_result() for v in values]

    if len(values) == 0:  # empty
        return []

    if any([v.is_available() for v in values]):
        raise RuntimeError("Some of values are already evaluated")

    with tracing.scope(tracing.Level.VERBOSE, "create_mlir_func"):
        source, input_values, output_values = create_mlir_func(
            values, package=package
        )

    ret = executor(source, input_values, output_values)

    if len(output_values) != len(ret):
        raise RuntimeError("Executor did not return enough number of returns")

    for output_value, obj in zip(output_values, ret):
        output_value.emplace(obj)

    return [v.get_result() for v in values]


# def print_refcounts(outs):
#     for value in outs:
#         if value.get_bound_obj() is None:
#             continue
#         # logger.debug('%s type=%s', value, type(value.get_bound_obj()))
#         # gc.collect()
#         logger.debug('%s#%x(#%x) refcount(obj)=%d %d refcount(value)=%d %d',
#                      value, id(value), id(value.get_bound_obj()),
#                      sys.getrefcount(value.get_bound_obj()),
#                      len(gc.get_referrers(value.get_bound_obj())),
#                      sys.getrefcount(value), len(gc.get_referrers(value)))
#         # logger.debug('Value.__dict__=%x', id(value.__dict__))
#
#         referrers = gc.get_referrers(value.get_bound_obj())
#         pretty = pprint.PrettyPrinter()
#         for r in referrers:
#             logger.debug('%s %x', type(r), id(r))
#             logger.debug(pretty.pformat(r))


def get_refcounts(outs):
    def get_refcount(value):
        obj = value.get_bound_obj()
        # might be None if originally there is circular reference
        # and gc takes place in between
        if obj is None:
            return 0

        try:
            # Don't call obj._fire_getrefcount which may cause fallback
            fn = object.__getattribute__(obj, "_fire_getrefcount")
            logger.debug("call _fire_getrefcount for %s", value)
            cnt = fn()

            # -2: remove reference from __self__ of fn and from this method
            assert cnt > 0
            return cnt - 2
        except AttributeError:
            # value.get_bound_obj() has not `_fire_getrefcount`
            pass

        # -2: remove reference from the argument of sys.getrefcount
        return sys.getrefcount(obj) - 2

    def is_bound(value):
        # the object must be alive if two consecutive checks result not None
        # GT: 4138#issuecomment-117087
        is_dead = value.get_bound_obj() is None
        if not is_dead:
            is_dead = value.get_bound_obj() is None
        return not is_dead

    return {v: get_refcount(v) for v in outs if is_bound(v)}


def frame_generator(frame):
    """A generator of frame objects for the given frame and all outer
    frames.

    Unlike inspect.getouterframes() which returns FrameInfo objects,
    this generator returns frame objects.

    """

    while frame is not None:
        yield frame
        frame = frame.f_back


def get_frames(skip=0):
    """Get an iterator of frame objects.

    By default, this function returns an iterator of frame objects
    without a frame of this function itself. If `skip` is a positive
    integer, the first `skip` frames are skipped. If `skip` is
    negative, this function may behave unexpectedly.

    """

    f = inspect.currentframe()
    try:
        if f is None:  # pragma: no cover
            # if inspect.currentframe() is unavailable
            stack = inspect.stack()
            del stack[:1]
            frames = iter(info.frame for info in stack)
        else:
            frames = frame_generator(f.f_back)
    finally:
        del f

    # consume frames
    next(itertools.islice(frames, skip, skip), None)
    return frames


# TODO: Review with complex module tree. And consider to receive user_frame
# from user.
def find_user_frame(outs, fire_user_module_name):
    """Find user stack frame

    Fire is typically used by a library. Here a "fire user" means the library,
    and just a "user" means a user of the library. This function tries to find
    stack frame of a "user".
    """
    assert fire_user_module_name is not None

    logger.debug(
        "find_user_frame: fire_user_module_name=%s", fire_user_module_name
    )

    found_fire_user_frame = False

    # Skip frames inside this file from find_user_frame() to evaluate()
    for frame in get_frames(4):
        frame_module_name = frame.f_globals["__name__"]
        # logger.debug(
        #     "find_user_frame: frame_module_name=%s lineno=%d",
        #     frame_module_name,
        #     frame.f_lineno,
        # )
        if frame_module_name.startswith(fire_user_module_name):
            # frame is belong to fire user module
            found_fire_user_frame = True
        elif found_fire_user_frame:
            # other frame after finding a fire user frame should be a user
            # frame
            # logger.debug("find_user_frame: found user frame")
            return frame
        else:
            # other frame before findind a fire user frame should be fire
            assert frame_module_name.startswith("firefw")
            pass

    return None


_backedge_insts = None


def get_backedge_insts():
    """Return instruction opcodes which are considered as backedges."""

    global _backedge_insts

    if _backedge_insts is None:
        opnames = [
            "JUMP_BACKWARD",  # from python3.11
            "JUMP_BACKWARD_NO_INTERRUPT",  # from python3.11
        ]

        _backedge_insts = [dis.opmap[op] for op in opnames if op in dis.opmap]

        # before python3.11, absolute jump is used. For safety, it is handled as a
        # backedge. After python3.11 dis.hasjabs is empty.
        _backedge_insts += dis.hasjabs

    return _backedge_insts


def find_later_uses(user_frame):
    """
    Return list of local names which are loaded after the last bytecode, i.e.
    f_lasti. If unknown, None will be returned.
    """

    later_uses = set()
    has_backedge = False
    bytecode = dis.Bytecode(user_frame.f_code)
    # dis.dis(user_frame.f_code)
    # print(user_frame.f_lasti)

    insts_accessing_locals = [
        dis.opmap["LOAD_NAME"],
        dis.opmap["LOAD_FAST"],
    ]

    backedge_insts = get_backedge_insts()

    # bytecode between f_lasti and the end of the frame will be checked to find
    # reference to local name.
    for inst in bytecode:
        if inst.offset >= user_frame.f_lasti:
            if inst.opcode in backedge_insts:
                logger.debug("backedge: %s", inst)
                has_backedge = True
                break
            if inst.opcode in insts_accessing_locals:
                later_uses.add(inst.argval)

    logger.debug(
        "later_uses: %s has_backedge: %s", list(set(later_uses)), has_backedge
    )

    if has_backedge:
        later_uses = None

    return later_uses


def filter_outputs_by_frame(user_frame, refcounts):
    """Filter the output value which are bound only to local variables and
    those are never referred after the evaluation.

    Args:
        user_frame: stack frame where evaluation is started
        refcounts: dictionaly of value and its refcount
    """

    logger.debug("filter_outputs_by_frame")

    # for n, v in user_frame.f_locals.items():
    #     logger.debug('user_frame: %s #%x', n, id(v))

    f_locals = user_frame.f_locals
    outputs = []
    value_local_names = {}

    for value, refcount in refcounts.items():
        # value referenced by the weakref might have been deleted
        # during the update of the cache in user_frame.f_locals
        # GT: issues/4138#issuecomment-116992
        obj = value.get_bound_obj()
        if obj is None:
            logger.debug(f"[{value._explain()}] {refcount=}")
            continue

        assert refcount >= 1

        referrers = set()
        for name, var in f_locals.items():
            if var is obj:  # if local_name refers obj
                referrers.add(name)

        assert len(referrers) <= refcount

        if len(referrers) == refcount:
            logger.debug(
                "output %s#%x(#%x) is bound only to local vars: %s.",
                value,
                id(value),
                id(obj),
                referrers,
            )
            value_local_names[value] = referrers
        else:
            logger.debug(
                "output %s#%x(#%x) is referred from non-locals"
                " (output for safety)",
                value,
                id(value),
                id(obj),
            )
            outputs += [value]

    logger.debug("lineno=%d lasti=%d", user_frame.f_lineno, user_frame.f_lasti)
    logger.debug("is_interactive=%s", _is_interactive())

    # None means later uses are unknown
    later_uses = find_later_uses(user_frame) if not _is_interactive() else None

    if later_uses is None:
        outputs += value_local_names.keys()
    else:
        for value, names in value_local_names.items():
            # if value is referred after evaluation, it should be an output.
            if later_uses.intersection(names):
                outputs += [value]

    logger.debug(
        "filter_outputs_by_frame: outputs: %s",
        ", ".join([str(v) for v in outputs]),
    )

    return outputs


def pickup_outputs(outs, package) -> List[fire.Value]:
    """Pickup values that should be results of the function.

    Args:
        value: The value which a caller want to evaluate.
        outs: output values of ops to be executed.

    Returns:
        [Value]: function results.

    This method first picks values which are bound to user-side objects. Then
    checks if the values are referred after evaluation.

    If an output value is never referred after evaluation, we do not have to
    return a result of such value. It improves opportunity of optimizations.
    This function finds such value and removes those from output values.
    """

    # Running gc might minimize refcounts, but it is costly, we do not run.
    # gc.collect()

    refcounts = get_refcounts(outs)
    logger.debug(
        "pickup_outputs: refcounts: %s%s",
        ", ".join([f"{k}:{refcounts[k]}" for k in list(refcounts)[:100]]),
        "..." if len(refcounts) > 100 else "",
    )

    refcounts = {val: cnt for val, cnt in refcounts.items() if cnt > 0}
    # logger.debug('%s', type(outs))
    # logger.debug('%s', type(refcounts))
    # logger.debug('pickup_outputs: len(outs)=%d -> len(outputs)=%d',
    #              len(outs), len(refcounts))

    logger.debug("pickup_outputs: len(refcounts)=%s", len(refcounts))
    # If outputs has only one value, it should be a function result.
    # we avoid costly filter using stack frames.
    if len(refcounts) > 1:
        frame = find_user_frame(outs, fire_user_module_name=package)
        # frame = None
        if frame is not None:
            outputs = filter_outputs_by_frame(frame, refcounts)
        else:
            logger.debug("pickup_outputs: frame not found")
            outputs = refcounts.keys()
    else:
        outputs = refcounts.keys()

    return list(outputs)


def get_ops(op, ops, opsset, indent=""):
    """Returns ops which are required to evaluate op recursively"""
    # logger.debug('get_ops: %s%s', indent, op)

    for op0 in op.deps:
        # logger.debug('get_ops: %sdepends on: %s', indent, str(op0))
        if op0 not in opsset:
            evaluated = [v.is_available() for v in op0.outs]
            # all true or all false
            # assert all(evaluated) or not any(evaluated)
            if not any(evaluated):
                get_ops(op0, ops, opsset, indent + "  ")

    # logger.debug('get_ops: %s>> append %s', indent, op.opcode)
    ops.append(op)
    opsset.add(op)

    return ops


# TODO: Not sure that this check is always safe.
# Note that returning True is safe.
def should_byte_encode(value: str):
    return "\\" in repr(value)


def create_constant(typ, value, name):
    if typ == "i1":
        i = 1 if value else 0
        return f"{name} = tfrt.constant.i1 {i}"
    if typ == "i32":
        return f"{name} = tfrt.constant.i32 {value}"
    if typ == "i64":
        return f"{name} = tfrt.constant.i64 {value}"
    if typ == "ui64":
        return f"{name} = tfrt.constant.ui64 {value}"
    if typ == "f32":
        hex_value = hex(struct.unpack(">L", struct.pack(">f", value))[0])
        return f"{name} = tfrt.constant.f32 {hex_value} // {value}"
    if typ == "f64":
        hex_value = hex(struct.unpack(">Q", struct.pack(">d", value))[0])
        return f"{name} = tfrt.constant.f64 {hex_value} // {value}"
    if typ == "!tfrt.string":
        # MLIR does not fully support escape sequences in string literals. In
        # such case, string will be byte encode.
        # While string can be always encoded, it is used as is when allowed for
        # better visibility in IR.
        if should_byte_encode(value):
            escaped = "".join([f"\\{x:02x}" for x in value.encode()])
            comment = f" // {repr(value)}"
        else:
            # Since text will be surrounded by double quotes, double quates in
            # a string should be escaped.
            escaped = value.replace('"', '\\"')
            comment = ""
        return (
            f'{name} = "fire.get_string"() {{ value = "{escaped}" }}'
            f" : () -> !tfrt.string{comment}"
        )
    return f"// UNHANDLED CONSTANT: {name} : {type(value)}"


def is_embeddable_constant(value: fire.Value):
    embeddables = ["f32", "f64", "i1", "i32", "i64", "ui64", "!tfrt.string"]
    return value.mlir_type in embeddables


def convert_to_mlir_op(op: fire.core.Operation, unique_ins):
    # logger.debug('create_mlir_op: %s', op)
    ins = []
    attrs = []
    for v in op.ins:
        if v.is_attr():
            attrs += [v]
        elif v.is_available():
            key = id(v.get_result())
            assert key in unique_ins
            ins += [unique_ins[key].name()]
        else:
            ins += [v.name()]
    ins = ", ".join(ins)

    in_types = ", ".join([v.mlir_type for v in op.ins if not v.is_attr()])
    lhs = ""
    out_types = ""
    if op.outs:
        outs = ", ".join([v.name() for v in op.outs])
        out_types = "-> (" + ", ".join(v.mlir_type for v in op.outs) + ")"
        lhs = f"{outs} = "

    if attrs:
        cont = [
            f"{v.name()} = {v.get_result()} : {v.type().mlir_type}"
            for v in attrs
        ]
        attrs = " { " + ", ".join(cont) + " }"
    else:
        attrs = ""

    return f'{lhs}"{op.opcode}"({ins}){attrs} :({in_types}) {out_types}'


def create_mlir_ops(values, package):
    """
    Args:
        values:         values to be evaluated.

    Returns:
        mlir_ops:      ops in function body as array of  string in mlir format.
        input_values:  values given as function arguments.
        output_values: values returned as function results.
    """
    assert len(values) > 0
    root_ops = [v.get_def() for v in values]

    logger.debug("create_mlir_ops: start to collect ops to be evaluated")
    ops = []
    opsset = set()
    for op in root_ops:
        if op not in ops:
            ops = get_ops(op, ops, opsset)
    logger.debug("create_mlir_ops: finish to collect ops to be evaluated")

    # Since ops going to be evaluated are not needed to evaluated again,
    # those are removed from a builder.
    # We use builder of first value because all ops have the same builder.
    builder = values[0].get_def().builder
    builder.remove_ops(opsset)

    ins = [v for op in ops for v in op.ins]
    outs = [v for op in ops for v in op.outs]

    # Different input values might have the same result.  We instantiates one
    # value for each result. unique_ins collects values having the same result.
    unique_ins = {}
    for v in [v for v in ins if v.is_available() and not v.is_attr()]:
        key = id(v.get_result())
        if key not in unique_ins:
            unique_ins[key] = v

    logger.debug(
        "create_mlir_ops: outs: (%s) %s%s",
        len(outs),
        [str(v) for v in outs[:100]],
        "" if len(outs) < 100 else "...",
    )

    # Decide output_values
    output_values = pickup_outputs(outs, package)

    logger.debug(
        "create_mlir_ops: output_values: (%s) %s%s",
        len(output_values),
        [str(v) for v in output_values[:100]],
        "" if len(output_values) < 100 else "...",
    )

    # pickup_outputs does not pickup values which are not bound to user
    # objects. But `value` is requested to be
    # evaluated by a user of this method, it is added to output_values.
    for v in values:
        if v not in output_values:
            output_values += [v]

    # Add values which are inputs of remaining ops in irbuilder, which are
    # created but not required to evaluate `values`. Such ops might be evaluate
    # afterward, the values have to be returned.
    # Ex:
    #   v0 = op0(...)
    #   v1 = op1(v0, ...)
    #   v2 = op2(v0, ...)
    # When evaluating v2, `v1 = op1(v0, ...)` is not evaluated because v2 does
    # not depend on v1. v0 have to be returned because it might be used when
    # op1 is evaluated.
    for op in builder.get_ops():
        tmp = [v for v in outs if v in op.ins and v not in output_values]
        output_values += tmp

    # Add all outputs of ops which output values in output_values.
    for ov in output_values:
        op = ov.get_def()
        tmp = [v for v in op.outs if v not in output_values]
        output_values += tmp

    # Embed inputs to IR or add to input_values
    input_values = []
    load_const_ops = []
    for v in unique_ins.values():
        if is_embeddable_constant(v):
            load_const_ops.append(
                create_constant(v.mlir_type, v.get_result(), v.name())
            )
        else:
            input_values.append(v)

    mlir_ops = load_const_ops
    for op in ops:
        mlir_ops.append(convert_to_mlir_op(op, unique_ins))

    logger.debug(
        "create_mlir_ops: input_values: (%d) %s%s",
        len(input_values),
        [str(v) for v in input_values[:100]],
        "..." if len(input_values) > 100 else "",
    )
    logger.debug(
        "create_mlir_ops: output_values: (%d) %s%s",
        len(output_values),
        [str(v) for v in output_values[:100]],
        "..." if len(output_values) > 100 else "",
    )

    return mlir_ops, input_values, output_values


# TODO: Move to irbuilder.py?
def create_mlir_func(values, *, fname="main", package=None):
    logger.debug("create_mlir_func")

    mlir_ops, input_values, output_values = create_mlir_ops(values, package)

    # Create Function

    formal_args = ", ".join(
        [f"{v.name()}: {v.mlir_type}" for v in input_values]
    )
    return_values = ", ".join([f"{v.name()}" for v in output_values])
    return_types = ", ".join([f"{v.mlir_type}" for v in output_values])

    # vim python-mode dose not like `{{`, we use `+ '{'`.
    lines = []
    lines.append(
        f"  func.func @{fname}({formal_args}) -> ({return_types})" + " {"
    )
    lines += ("    " + line for line in mlir_ops)
    lines.append(f"    tfrt.return {return_values} : {return_types}")
    lines.append("  }")

    return "\n".join(lines), input_values, output_values
