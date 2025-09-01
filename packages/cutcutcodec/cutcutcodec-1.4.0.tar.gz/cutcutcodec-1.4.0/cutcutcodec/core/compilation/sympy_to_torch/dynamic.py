#!/usr/bin/env python3

"""Torch dynamic evaluation of atomic sympy expression.

It is faster to initialise than the compilated version but it is slower to evaluate.
This dynamic evaluation support broadcasting.

Implemented functions:

    * sympy.Abs
    * sympy.acos
    * sympy.acosh
    * sympy.Add `+`
    * sympy.And
    * sympy.asin
    * sympy.atan
    * sympy.cbrt
    * sympy.cos
    * sympy.cosh
    * sympy.Eq
    * sympy.exp
    * sympy.GreaterThan
    * sympy.im
    * sympy.ITE
    * sympy.LessThan
    * sympy.log
    * sympy.Max
    * sympy.Min
    * sympy.Mul `*`
    * sympy.Or
    * sympy.Piecewise
    * sympy.Pow `/` and `**`
    * sympy.re
    * sympy.sin
    * sympy.sinh
    * sympy.sqrt
    * sympy.StrictGreaterThan
    * sympy.StrictLessThan
    * sympy.tan
    * sympy.tanh
    * sympy.Tuple

Not implemented functions:

    * sympy.Add `+` and `-`
    * sympy.arg
    * sympy.asinh
    * sympy.atan2
    * sympy.atanh
    * sympy.ceiling
    * sympy.Determinant
    * sympy.erf
    * sympy.floor
    * sympy.HadamardProduct
    * sympy.loggamma
    * sympy.MatAdd
    * sympy.Mod `%`
    * sympy.Ne
    * sympy.Not
    * sympy.sign
    * sympy.Trace
"""

import numbers
import typing

from sympy.core.basic import Basic
from sympy.core.numbers import nan, oo
from sympy.functions.elementary.piecewise import Piecewise
import torch


def _dyn_eval(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None
) -> torch.Tensor | numbers.Real | tuple:
    """Recursive replacement of sympy element by numerical elements.

    Parameters
    ----------
    expr : sympy.core.basic.Basic
        The sympy expression to eval.
    input_args : dict[str, torch.Tensor]
        To each variable name present in the expression, associate the numerical value.
    new_var : str, optional
        If provide, complete inplace the dictionary ``input_args``.
        If the variable is already present in the ``input_args``,
        the values of the tensor are changed inplace.
    """
    if expr.is_Atom:
        if expr.is_symbol:
            value = input_args[str(expr)]
            if isinstance(value, torch.Tensor):
                value = value.clone()
        elif expr.is_integer or expr.is_real:
            value = float(expr)
        elif expr.is_complex:
            value = complex(expr)
        elif expr in {nan, oo, -oo, True, False}:
            value = {
                nan: torch.nan,
                oo: torch.inf,
                -oo: -torch.inf,
                True: True,
                False: False,
            }[expr]
        else:
            raise NotImplementedError(f"unknown atomic {expr}")
        if new_var is not None:
            input_args[new_var] = value
        return value
    try:
        func = globals()[f"_{expr.__class__.__name__.lower()}"]
    except KeyError as err:
        raise NotImplementedError(f"no function {expr.__class__.__name__} for {expr}") from err
    return func(expr, input_args, new_var)


def _abs(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic abs operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan, -torch.inf, -2., 2., torch.inf])}
    >>> _dyn_eval(abs(x), input_args, "x")
    tensor([nan, inf, 2., 2., inf])
    >>> _ is input_args["x"]
    True
    >>> input_args = {"x": torch.tensor([3+4j, -3+4j, 3-4j, -3-4j])}
    >>> _dyn_eval(abs(x), input_args, "x")
    tensor([5.+0.j, 5.+0.j, 5.+0.j, 5.+0.j])
    >>> _ is input_args["x"]
    True
    >>>
    """
    input_val = _dyn_eval(expr.args[0], input_args)
    try:
        abs_value = torch.abs(input_val, out=input_args.get(new_var, None))
    except RuntimeError:
        abs_value = torch.abs(input_val)
    abs_value = abs_value.to(input_val.dtype)
    if new_var is not None:
        input_args[new_var] = abs_value
    return abs_value


def _acos(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    input_val = _dyn_eval(expr.args[0], input_args)
    out = None
    if new_var is not None:
        if (out := input_args.get(new_var, None)) is not None:
            if out.shape != input_val.shape or out.dtype != input_val.dtype:
                out = None
    acos_value = torch.acos(input_val, out=out)
    if new_var is not None:
        input_args[new_var] = acos_value
    return acos_value


def _acosh(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    input_val = _dyn_eval(expr.args[0], input_args)
    out = None
    if new_var is not None:
        if (out := input_args.get(new_var, None)) is not None:
            if out.shape != input_val.shape or out.dtype != input_val.dtype:
                out = None
    acosh_value = torch.acosh(input_val, out=out)
    if new_var is not None:
        input_args[new_var] = acosh_value
    return acosh_value


def _add(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic + operation.

    Examples
    --------
    >>> from sympy.abc import x, y
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([[0.0], [1.0]]), "y": torch.tensor([[2.0, 4.0]])}
    >>> _dyn_eval(1 + x + y, input_args, "z")
    tensor([[3., 5.],
            [4., 6.]])
    >>> _ is input_args["z"]
    True
    >>>
    """
    args = [_dyn_eval(a, input_args) for a in expr.args]
    args.sort(key=(lambda x: torch.numel(x) if isinstance(x, torch.Tensor) else 1))
    sum_value = sum(args, start=args.pop(0))
    if new_var is not None:
        input_args[new_var] = sum_value
    return sum_value


def _and(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    args = [_dyn_eval(a, input_args) for a in expr.args]
    args.sort(key=(lambda x: torch.numel(x) if isinstance(x, torch.Tensor) else 1))
    max_value = args.pop(0)
    for item in args:
        max_value = torch.logical_and(max_value, item)
    if new_var is not None:
        input_args[new_var] = max_value
    return max_value


def _asin(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    input_val = _dyn_eval(expr.args[0], input_args)
    out = None
    if new_var is not None:
        if (out := input_args.get(new_var, None)) is not None:
            if out.shape != input_val.shape or out.dtype != input_val.dtype:
                out = None
    asin_value = torch.asin(input_val, out=out)
    if new_var is not None:
        input_args[new_var] = asin_value
    return asin_value


def _atan(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic atan operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.trigonometric import atan
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan])}
    >>> _dyn_eval(atan(x), input_args, "x")
    tensor([nan])
    >>> _ is input_args["x"]
    True
    >>> input_args = {"x": torch.tensor([-torch.inf, -1.0, 0.0, 1.0, torch.inf])}
    >>> _dyn_eval(atan(x), input_args, "x")
    tensor([-1.5708, -0.7854,  0.0000,  0.7854,  1.5708])
    >>> torch.div(_, torch.pi, out=_)
    tensor([-0.5000, -0.2500,  0.0000,  0.2500,  0.5000])
    >>> _ is input_args["x"]
    True
    >>>
    """
    input_val = _dyn_eval(expr.args[0], input_args)
    try:
        cos_value = torch.atan(input_val, out=input_args.get(new_var, None))
    except RuntimeError:
        cos_value = torch.atan(input_val)
    if new_var is not None:
        input_args[new_var] = cos_value
    return cos_value


def _cos(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic cos operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.trigonometric import cos
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan])}
    >>> _dyn_eval(cos(x), input_args, "x")
    tensor([nan])
    >>> _ is input_args["x"]
    True
    >>> input_args = {"x": torch.tensor([0., 0.78540, 2.35620, 3.14160, 3.92700, 5.49779, 6.28319])}
    >>> _dyn_eval(cos(x), input_args, "x")
    tensor([ 1.0000,  0.7071, -0.7071, -1.0000, -0.7071,  0.7071,  1.0000])
    >>> _ is input_args["x"]
    True
    >>> input_args = {"x": torch.tensor([1+1j])}
    >>> _dyn_eval(cos(x), input_args, "x")
    tensor([0.8337-0.9889j])
    >>>
    """
    input_val = _dyn_eval(expr.args[0], input_args)
    try:
        cos_value = torch.cos(input_val, out=input_args.get(new_var, None))
    except RuntimeError:
        cos_value = torch.cos(input_val)
    if new_var is not None:
        input_args[new_var] = cos_value
    return cos_value


def _cosh(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    input_val = _dyn_eval(expr.args[0], input_args)
    out = None
    if new_var is not None:
        if (out := input_args.get(new_var, None)) is not None:
            if out.shape != input_val.shape or out.dtype != input_val.dtype:
                out = None
    cosh_value = torch.cosh(input_val, out=out)
    if new_var is not None:
        input_args[new_var] = cosh_value
    return cosh_value


def _equality(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Eval an equality.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.core.relational import Equality
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan, -torch.inf, -1.0, 0.0, 1.0, torch.inf])}
    >>> _dyn_eval(Equality(x, 0), input_args, "x")
    tensor([False, False, False,  True, False, False])
    >>>
    """
    res = _dyn_eval(expr.args[0], input_args) == _dyn_eval(expr.args[1], input_args)
    if new_var is not None:
        input_args[new_var] = res
    return res


def _exp(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic exp operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.trigonometric import exp
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan])}
    >>> _dyn_eval(exp(x), input_args, "x")
    tensor([nan])
    >>> _ is input_args["x"]
    True
    >>> input_args = {"x": torch.tensor([-torch.inf, -1.0, 0.0, 1.0, torch.inf])}
    >>> _dyn_eval(exp(x), input_args, "x")
    tensor([0.0000, 0.3679, 1.0000, 2.7183,    inf])
    >>> _ is input_args["x"]
    True
    >>> input_args = {"x": torch.tensor([1+1j])}
    >>> _dyn_eval(exp(x), input_args, "x")
    tensor([1.4687+2.2874j])
    >>>
    """
    input_val = _dyn_eval(expr.args[0], input_args)
    # try:
    #     exp_value = torch.exp(input_val, out=input_args.get(new_var, None))
    # except RuntimeError:
    exp_value = torch.exp(input_val)
    if new_var is not None:
        input_args[new_var] = exp_value
    return exp_value


def _greaterthan(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Eval an inequality.

    Examples
    --------
    >>> from sympy.abc import x
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan, -torch.inf, -1.0, 0.0, 1.0, torch.inf])}
    >>> _dyn_eval(x >= 0, input_args, "x")
    tensor([False, False, False,  True,  True,  True])
    >>>
    """
    res = _dyn_eval(expr.args[0], input_args) >= _dyn_eval(expr.args[1], input_args)
    if new_var is not None:
        input_args[new_var] = res
    return res


def _im(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    im_value = _dyn_eval(expr.args[0], input_args).imag
    if str(expr.args[0]) != new_var:
        im_value = im_value.clone()
    if new_var is not None:
        input_args[new_var] = im_value
    return im_value


def _ite(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    args = [_dyn_eval(a, input_args) for a in expr.args]
    assert len(args) == 3, args
    ite_value = torch.where(*args)
    if new_var is not None:
        input_args[new_var] = ite_value
    return ite_value


def _lessthan(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Eval an inequality.

    Examples
    --------
    >>> from sympy.abc import x
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan, -torch.inf, -1.0, 0.0, 1.0, torch.inf])}
    >>> _dyn_eval(x <= 0, input_args, "x")
    tensor([False,  True,  True,  True, False, False])
    >>>
    """
    res = _dyn_eval(expr.args[0], input_args) <= _dyn_eval(expr.args[1], input_args)
    if new_var is not None:
        input_args[new_var] = res
    return res


def _log(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    input_val = _dyn_eval(expr.args[0], input_args)
    out = None
    if new_var is not None:
        if (out := input_args.get(new_var, None)) is not None:
            if out.shape != input_val.shape or out.dtype != input_val.dtype:
                out = None
    log_value = torch.log(input_val, out=out)
    if new_var is not None:
        input_args[new_var] = log_value
    return log_value


def _max(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic maximum operation.

    Examples
    --------
    >>> from sympy.abc import x, y
    >>> from sympy.functions.elementary.miscellaneous import Max
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([[0.0], [2.0]]), "y": torch.tensor([[1.0, 4.0]])}
    >>> _dyn_eval(Max(x, y), input_args, "z")
    tensor([[1., 4.],
            [2., 4.]])
    >>> _ is input_args["z"]
    True
    >>>
    """
    args = [_dyn_eval(a, input_args) for a in expr.args]
    args.sort(key=(lambda x: torch.numel(x) if isinstance(x, torch.Tensor) else 1))
    args = [a if isinstance(a, torch.Tensor) else torch.tensor(a) for a in args]
    max_value = args.pop(0)
    for item in args:
        max_value = torch.maximum(max_value, item)
    if new_var is not None:
        input_args[new_var] = max_value
    return max_value


def _min(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    args = [_dyn_eval(a, input_args) for a in expr.args]
    args.sort(key=(lambda x: torch.numel(x) if isinstance(x, torch.Tensor) else 1))
    args = [a if isinstance(a, torch.Tensor) else torch.tensor(a) for a in args]
    min_value = args.pop(0)
    for item in args:
        min_value = torch.minimum(min_value, item)
    if new_var is not None:
        input_args[new_var] = min_value
    return min_value


def _mul(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic * operation.

    Examples
    --------
    >>> from sympy.abc import x, y
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([[0.0], [1.0]]), "y": torch.tensor([[2.0, 4.0]])}
    >>> _dyn_eval(2 * x * y, input_args, "z")
    tensor([[0., 0.],
            [4., 8.]])
    >>> _ is input_args["z"]
    True
    >>>
    """
    args = [_dyn_eval(a, input_args) for a in expr.args]
    args.sort(key=(lambda x: torch.numel(x) if isinstance(x, torch.Tensor) else 1))
    mul_value = args.pop(0)
    for item in args:
        mul_value = mul_value * item
    if new_var is not None:
        input_args[new_var] = mul_value
    return mul_value


def _or(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic | operation.

    Examples
    --------
    >>> from sympy.abc import x, y
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([[0], [1]]), "y": torch.tensor([[0, 1]])}
    >>> _dyn_eval(x | y, input_args, "z")
    tensor([[0, 1],
            [1, 1]])
    >>> _ is input_args["z"]
    True
    >>>
    """
    args = [_dyn_eval(a, input_args) for a in expr.args]
    args.sort(key=(lambda x: torch.numel(x) if isinstance(x, torch.Tensor) else 1))
    or_value = args.pop(0)
    for item in args:
        or_value = or_value | item
    if new_var is not None:
        input_args[new_var] = or_value
    return or_value


def _piecewise(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic ** operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.piecewise import Piecewise
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan, -torch.inf, -1.0, 0.0, 1.0, torch.inf])}
    >>> _dyn_eval(Piecewise((0, x < 0), (x, True)), input_args, "x")
    tensor([nan, 0., 0., 0., 1., inf])
    >>>
    """
    val_true, cond = expr.args[0]
    val_false = _dyn_eval(Piecewise(*expr.args[1:]), input_args)
    out = torch.where(_dyn_eval(cond, input_args), _dyn_eval(val_true, input_args), val_false)
    if new_var is not None:
        input_args[new_var] = out
    return out


def _pow(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic ** operation.

    Examples
    --------
    >>> from sympy.abc import x, y
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([[2.0], [4.0]]), "y": torch.tensor([[0.5, 2.0]])}
    >>> _dyn_eval(x**y, input_args, "z")
    tensor([[ 1.4142,  4.0000],
            [ 2.0000, 16.0000]])
    >>> _ is input_args["z"]
    True
    >>> _dyn_eval(x**.5, input_args, "x")  # sqrt
    tensor([[1.4142],
            [2.0000]])
    >>> _dyn_eval(x**-1, input_args, "x")  # 1/x
    tensor([[0.7071],
            [0.5000]])
    >>>
    """
    base, exp = _dyn_eval(expr.base, input_args), _dyn_eval(expr.exp, input_args)
    pow_value = None
    if isinstance(exp, numbers.Real):
        if exp == -1:
            pow_value = torch.div(1, base)
        elif exp == .5:
            pow_value = torch.sqrt(base)
    if pow_value is None:
        pow_value = torch.pow(base, exp)
    if new_var is not None:
        input_args[new_var] = pow_value
    return pow_value


def _re(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    re_value = _dyn_eval(expr.args[0], input_args).real
    if str(expr.args[0]) != new_var:
        re_value = re_value.clone()
    if new_var is not None:
        input_args[new_var] = re_value
    return re_value


def _sign(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    arg = _dyn_eval(expr.args[0], input_args)
    out = None
    if new_var is not None:
        if (out := input_args.get(new_var, None)) is not None:
            if out.shape != arg.shape or out.dtype != arg.dtype:
                out = None
    if arg.dtype.is_floating_point:
        sign_value = torch.sign(arg, out=out)
    else:
        sign_value = torch.where(arg == 0, torch.zeros_like(arg), arg/abs(arg), out=out)
    if new_var is not None:
        input_args[new_var] = sign_value
    return sign_value


def _sin(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Dynamic sin operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.trigonometric import sin
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan])}
    >>> _dyn_eval(sin(x), input_args, "x")
    tensor([nan])
    >>> _ is input_args["x"]
    True
    >>> input_args = {"x": torch.tensor([0.78540, 1.57080, 2.35619, 3.92699, 4.71239, 5.49779])}
    >>> _dyn_eval(abs(x), input_args, "x")
    tensor([0.7854, 1.5708, 2.3562, 3.9270, 4.7124, 5.4978])
    >>> _ is input_args["x"]
    True
    >>> input_args = {"x": torch.tensor([1+1j])}
    >>> _dyn_eval(sin(x), input_args, "x")
    tensor([1.2985+0.6350j])
    >>>
    """
    input_val = _dyn_eval(expr.args[0], input_args)
    try:
        sin_value = torch.sin(input_val, out=input_args.get(new_var, None))
    except RuntimeError:
        sin_value = torch.sin(input_val)
    if new_var is not None:
        input_args[new_var] = sin_value
    return sin_value


def _sinh(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    input_val = _dyn_eval(expr.args[0], input_args)
    out = None
    if new_var is not None:
        if (out := input_args.get(new_var, None)) is not None:
            if out.shape != input_val.shape or out.dtype != input_val.dtype:
                out = None
    sinh_value = torch.sinh(input_val, out=out)
    if new_var is not None:
        input_args[new_var] = sinh_value
    return sinh_value


def _strictgreaterthan(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Eval an inequality.

    Examples
    --------
    >>> from sympy.abc import x
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan, -torch.inf, -1.0, 0.0, 1.0, torch.inf])}
    >>> _dyn_eval(x > 0, input_args, "x")
    tensor([False, False, False, False,  True,  True])
    >>>
    """
    res = _dyn_eval(expr.args[0], input_args) > _dyn_eval(expr.args[1], input_args)
    if new_var is not None:
        input_args[new_var] = res
    return res


def _strictlessthan(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    """Eval an inequality.

    Examples
    --------
    >>> from sympy.abc import x
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
    >>> input_args = {"x": torch.tensor([torch.nan, -torch.inf, -1.0, 0.0, 1.0, torch.inf])}
    >>> _dyn_eval(x < 0, input_args, "x")
    tensor([False,  True,  True, False, False, False])
    >>>
    """
    res = _dyn_eval(expr.args[0], input_args) < _dyn_eval(expr.args[1], input_args)
    if new_var is not None:
        input_args[new_var] = res
    return res


def _tan(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    input_val = _dyn_eval(expr.args[0], input_args)
    out = None
    if new_var is not None:
        if (out := input_args.get(new_var, None)) is not None:
            if out.shape != input_val.shape or out.dtype != input_val.dtype:
                out = None
    tan_value = torch.tan(input_val, out=out)
    if new_var is not None:
        input_args[new_var] = tan_value
    return tan_value


def _tanh(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    input_val = _dyn_eval(expr.args[0], input_args)
    out = None
    if new_var is not None:
        if (out := input_args.get(new_var, None)) is not None:
            if out.shape != input_val.shape or out.dtype != input_val.dtype:
                out = None
    tanh_value = torch.tanh(input_val, out=out)
    if new_var is not None:
        input_args[new_var] = tanh_value
    return tanh_value


def _tuple(
    expr: Basic, input_args: dict[str, torch.Tensor], new_var: typing.Optional[str] = None,
) -> torch.Tensor | numbers.Real:
    if new_var is None:
        return tuple(_dyn_eval(a, input_args) for a in expr)
    input_args[new_var] = _tuple(expr, input_args)
    return input_args[new_var]
