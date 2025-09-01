#!/usr/bin/env python3

"""C implementation of all atomic operations, helper for ``printer``."""

from fractions import Fraction
import collections
import re

from sympy.core.basic import Atom
from sympy.core.numbers import Integer, One, Rational
from sympy.core.power import Pow
from sympy.core.relational import Equality
from sympy.core.symbol import Symbol
from sympy.functions.elementary.complexes import im as sympy_im, re as sympy_re
from sympy.logic.boolalg import BooleanFalse, BooleanTrue

from cutcutcodec.core.exceptions import CompilationError


def atom2str(elem: Atom, indexing: collections.defaultdict[Symbol, str], c_type: str) -> str:
    """Help for `_print_atomic`."""
    if elem.is_symbol:
        return f"{elem}{indexing[elem]}"
    if elem.is_number:
        if c_type in {"float", "double", "long double"}:
            if elem.is_real or elem.is_integer:
                suffix = {"float": "f", "double": "", "long double": "L"}[c_type]
                return f"{float(elem)}{suffix}"
            raise CompilationError(f"impossible to compile {elem} as C type {c_type}")
        if c_type in {"float complex", "double complex", "long double complex"} and elem.is_complex:
            suffix = {
                "float complex": "f", "double complex": "", "long double complex": "L"
            }[c_type]
            return (
                f"({float(sympy_re(elem))}{suffix} + {float(sympy_im(elem))}{suffix} * _Complex_I)"
            )
        raise CompilationError(f"failed to compile {elem} in C")
    if isinstance(elem, BooleanTrue):
        return "1"
    if isinstance(elem, BooleanFalse):
        return "0"
    raise CompilationError(f"{elem} should be atomic but is not")


def _comp(
    out: Symbol,
    indexing: collections.defaultdict[Symbol, str],
    c_type: str,
    operation: str,
    *parts: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C comparaison operation, with module comparaison for complex numbers."""
    out_str = atom2str(out, indexing, "bool")
    if len(parts) != 2:
        raise ValueError(f"failed to print the function {operation} with {len(parts)} arguments")
    e_1 = atom2str(parts[0], indexing, c_type)
    e_2 = atom2str(parts[1], indexing, c_type)
    cfunc = {
        "float": "_",
        "double": "_",
        "long double": "_",
        "float complex": "crealf(_)*crealf(_) + cimagf(_)*cimagf(_)",
        "double complex": "creal(_)*creal(_) + cimagl(_)*cimagl(_)",
        "long double complex": "creall(_)*creall(_) + cimagl(_)*cimagl(_)",
    }[c_type]
    code = [f"{out_str} = {cfunc.replace('_', e_1)} {operation} {cfunc.replace('_', e_2)};"]
    return set(), set(), code


def c_abs(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, arg: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C abs operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.complexes import Abs
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, Abs(x))], {}, {x}))
    >>> func(np.array([np.nan, -np.inf, -2., 2., np.inf]))
    array([nan, inf,  2.,  2., inf])
    >>> func(np.array([3+4j, -3+4j, 3-4j, -3-4j]))
    array([5.+0.j, 5.+0.j, 5.+0.j, 5.+0.j])
    >>>
    """
    cfunc = {
        "float": "fabsf",
        "double": "fabs",
        "long double": "fabsl",
        "float complex": "(float complex)fabsf",
        "double complex": "(double complex)cabs",
        "long double complex": "(long double complex)fabsl",
    }[c_type]
    code = f"{atom2str(out, indexing, c_type)} = {cfunc}({atom2str(arg, indexing, c_type)});"
    return set(), set(), [code]


def c_add(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, *parts: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C + operation.

    Examples
    --------
    >>> from collections import defaultdict
    >>> from sympy.abc import x, y, z
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic
    >>> _print_atomic(1 + x, x, defaultdict(lambda: ""), "float")
    (set(), set(), ['x += 1.0f;'])
    >>> _print_atomic(1 + x, y, defaultdict(lambda: ""), "float")
    (set(), set(), ['y = 1.0f + x;'])
    >>> _print_atomic(1 + x + y, z, defaultdict(lambda: ""), "float")
    (set(), set(), ['z = 1.0f + x;', 'z += y;'])
    >>>
    """
    out_str = atom2str(out, indexing, c_type)
    if len(parts) == 0:
        parts = (Integer(0),)
    if len(parts) == 1:
        return set(), set(), [f"{out_str} = {atom2str(parts[0], indexing, c_type)};"]
    try:
        ind = parts.index(out)
    except ValueError:
        code_lines = [
            f"{out_str} = "
            f"{atom2str(parts[0], indexing, c_type)} + {atom2str(parts[1], indexing, c_type)};"
        ]
        parts = parts[2:]
    else:
        code_lines = []
        parts = tuple(p for i, p in enumerate(parts) if i != ind)
    code_lines.extend([f"{out_str} += {atom2str(p, indexing, c_type)};" for p in parts])
    return set(), set(), code_lines


def c_atan(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, arg: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C atan operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.trigonometric import atan
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, atan(x))], {}, {x}))
    >>> func(np.array([np.nan]))
    array([nan])
    >>> func(np.array([-np.inf, -1.0, 0.0, 1.0, np.inf])) / np.pi
    array([-0.5 , -0.25,  0.  ,  0.25,  0.5 ])
    >>>
    """
    if (cfunc := {
        "float": "atanf",
        "double": "atan",
        "long double": "atanl",
    }.get(c_type, None)) is None:
        raise CompilationError(f"atan is not implemented for {c_type}")
    code = f"{atom2str(out, indexing, c_type)} = {cfunc}({atom2str(arg, indexing, c_type)});"
    return set(), set(), [code]


def c_cos(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, arg: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C cos operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.trigonometric import cos
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, cos(x))], {}, {x}))
    >>> func(np.array([np.nan]))
    array([nan])
    >>> func(np.array([0., 0.78539816, 2.35619449, 3.14159265, 3.92699082, 5.49778714, 6.28318531]))
    array([ 1.        ,  0.70710678, -0.70710678, -1.        , -0.70710678,
            0.70710678,  1.        ])
    >>> func(np.array([1+1j]))
    array([0.83373003-0.98889771j])
    >>>
    """
    cfunc = {
        "float": "cosf",
        "double": "cos",
        "long double": "cosl",
        "float complex": "ccosf",
        "double complex": "ccos",
        "long double complex": "ccosl",
    }[c_type]
    code = f"{atom2str(out, indexing, c_type)} = {cfunc}({atom2str(arg, indexing, c_type)});"
    return set(), set(), [code]


def c_equality(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, *parts: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C == operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.core.relational import Equality
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, Equality(x, 0))], {}, {x}))
    >>> func(np.array([-np.inf, -1.0, 0.0, 1.0, np.inf]))
    array([0., 0., 1., 0., 0.])
    >>>
    """
    out_str = atom2str(out, indexing, "bool")
    if len(parts) != 2:
        raise ValueError(f"failed to print the function equality with {len(parts)} arguments")
    e_1 = atom2str(parts[0], indexing, c_type)
    e_2 = atom2str(parts[1], indexing, c_type)
    code = [f"{out_str} = {e_1} == {e_2};"]
    return set(), set(), code


def c_exp(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, arg: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C exp operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.trigonometric import exp
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, exp(x))], {}, {x}))
    >>> func(np.array([np.nan]))
    array([nan])
    >>> func(np.array([-np.inf, -1.0, 0.0, 1.0, np.inf]))
    array([0.        , 0.36787944, 1.        , 2.71828183,        inf])
    >>> func(np.array([1+1j]))
    array([1.46869394+2.28735529j])
    >>>
    """
    cfunc = {
        "float": "expf",
        "double": "exp",
        "long double": "expl",
        "float complex": "cexpf",
        "double complex": "cexp",
        "long double complex": "cexpl",
    }[c_type]
    code = f"{atom2str(out, indexing, c_type)} = {cfunc}({atom2str(arg, indexing, c_type)});"
    return set(), set(), [code]


def c_greaterthan(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, *parts: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C >= operation, with module comparaison for complex numbers.

    Examples
    --------
    >>> from sympy.abc import x
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, x >= 0)], {}, {x}))
    >>> func(np.array([-np.inf, -1.0, 0.0, 1.0, np.inf]))
    array([0., 0., 1., 1., 1.])
    >>>
    """
    return _comp(out, indexing, c_type, ">=", *parts)


def c_lessthan(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, *parts: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C <= operation, with module comparaison for complex numbers.

    Examples
    --------
    >>> from sympy.abc import x
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, x <= 0)], {}, {x}))
    >>> func(np.array([-np.inf, -1.0, 0.0, 1.0, np.inf]))
    array([1., 1., 1., 0., 0.])
    >>>
    """
    return _comp(out, indexing, c_type, "<=", *parts)


def c_log(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, arg: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C log operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.exponential import log
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, log(x))], {}, {x}))
    >>> func(np.array([np.nan]))
    array([nan])
    >>> func(np.array([0.0, 1.0, np.e, np.inf]))
    array([-inf,   0.,   1.,  inf])
    >>>
    """
    cfunc = {
        "float": "logf",
        "double": "log",
        "long double": "logl",
        "float complex": "clogf",
        "double complex": "clog",
        "long double complex": "clogl",
    }[c_type]
    code = f"{atom2str(out, indexing, c_type)} = {cfunc}({atom2str(arg, indexing, c_type)});"
    return set(), set(), [code]


def c_max(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, *parts: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C maximum operation.

    Examples
    --------
    >>> from collections import defaultdict
    >>> from sympy.abc import x, y
    >>> from sympy.functions.elementary.miscellaneous import Max
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic
    >>> _print_atomic(Max(2, x), x, defaultdict(lambda: ""), "float")
    (set(), set(), ['x = 2.0f > x ? 2.0f : x;'])
    >>> _print_atomic(Max(2, x), y, defaultdict(lambda: ""), "float complex")  # doctest: +ELLIPSIS
    (set(), set(), ['y = (crealf((2.0f + 0.0f * _Complex_I))... ? (2.0f + 0.0f * _Complex_I) : x;'])
    >>> _print_atomic(Max(2, x, y), x, defaultdict(lambda: ""), "float")
    (set(), set(), ['x = 2.0f > x ? 2.0f : x;', 'x = x > y ? x : y;'])
    >>>
    """
    out_str = atom2str(out, indexing, c_type)
    if len(parts) == 0:
        raise ValueError("failed to print the function maximum with 0 arguments")
    if len(parts) == 1:
        return set(), set(), [f"{out_str} = {atom2str(parts[0], indexing, c_type)};"]
    e_1 = atom2str(parts[0], indexing, c_type)
    e_2 = atom2str(parts[1], indexing, c_type)
    rel = {
        "float": "_",
        "double": "_",
        "long double": "_",
        "float complex": "(crealf(_)*crealf(_) + cimagf(_)*cimagf(_))",
        "double complex": "(creal(_)*creal(_) + cimag(_)*cimag(_))",
        "long double complex": "(creall(_)*creall(_) + cimagl(_)*cimagl(_))",
    }[c_type]
    code = [f"{out_str} = {rel.replace('_', e_1)} > {rel.replace('_', e_2)} ? {e_1} : {e_2};"]
    while len(parts) > 2:
        parts = (out,) + parts[2:]
        code.extend(c_max(out, indexing, c_type, *parts)[2])
    return set(), set(), code


def c_min(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, *parts: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C minimum operation."""
    out_str = atom2str(out, indexing, c_type)
    if len(parts) == 0:
        raise ValueError("failed to print the function maximum with 0 arguments")
    if len(parts) == 1:
        return set(), set(), [f"{out_str} = {atom2str(parts[0], indexing, c_type)};"]
    e_1 = atom2str(parts[0], indexing, c_type)
    e_2 = atom2str(parts[1], indexing, c_type)
    rel = {
        "float": "_",
        "double": "_",
        "long double": "_",
        "float complex": "(crealf(_)*crealf(_) + cimagf(_)*cimagf(_))",
        "double complex": "(creal(_)*creal(_) + cimag(_)*cimag(_))",
        "long double complex": "(creall(_)*creall(_) + cimagl(_)*cimagl(_))",
    }[c_type]
    code = [f"{out_str} = {rel.replace('_', e_1)} < {rel.replace('_', e_2)} ? {e_1} : {e_2};"]
    while len(parts) > 2:
        parts = (out,) + parts[2:]
        code.extend(c_max(out, indexing, c_type, *parts)[2])
    return set(), set(), code


def c_mul(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, *parts: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C * operation.

    Examples
    --------
    >>> from collections import defaultdict
    >>> from sympy.abc import x, y, z
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic
    >>> _print_atomic(2 * x, x, defaultdict(lambda: ""), "float")
    (set(), set(), ['x *= 2.0f;'])
    >>> _print_atomic(2 * x, y, defaultdict(lambda: ""), "float")
    (set(), set(), ['y = 2.0f * x;'])
    >>> _print_atomic(2 * x * y, z, defaultdict(lambda: ""), "float")
    (set(), set(), ['z = 2.0f * x;', 'z *= y;'])
    >>>
    """
    out_str = atom2str(out, indexing, c_type)
    if len(parts) == 0:
        parts = (Integer(1),)
    if len(parts) == 1:
        return set(), set(), [f"{out_str} = {atom2str(parts[0], indexing, c_type)};"]
    try:
        ind = parts.index(out)
    except ValueError:
        code_lines = [
            f"{out_str} = "
            f"{atom2str(parts[0], indexing, c_type)} * {atom2str(parts[1], indexing, c_type)};"
        ]
        parts = parts[2:]
    else:
        code_lines = []
        parts = tuple(p for i, p in enumerate(parts) if i != ind)
    code_lines.extend([f"{out_str} *= {atom2str(p, indexing, c_type)};" for p in parts])
    return set(), set(), code_lines


def c_pow(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, base: Atom, exp: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C ** operation.

    Examples
    --------
    >>> from collections import defaultdict
    >>> from sympy.abc import x, y, z
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>>
    >>> _print_atomic(x**y, z, defaultdict(lambda: ""), "float")
    (set(), set(), ['z = powf(x, y);'])
    >>> _print_atomic(1/x, z, defaultdict(lambda: ""), "float")
    (set(), set(), ['z = 1.0f / x;'])
    >>> _print_atomic(x**2, y, defaultdict(lambda: ""), "float")
    (set(), set(), ['y = x * x;'])
    >>> _print_atomic(x**.5, y, defaultdict(lambda: ""), "float")
    (set(), set(), ['y = sqrtf(x);'])
    >>> _print_atomic(x**(1/3), y, defaultdict(lambda: ""), "float")
    (set(), set(), ['y = cbrtf(x);'])
    >>> _print_atomic(x**(-7/2), y, defaultdict(lambda: ""), "double")
    (set(), {_buf}, ['y = x * x;', '_buf = x * y;', 'y *= y;', 'y *= _buf;', 'y = 1.0 / sqrt(y);'])
    >>>
    >>> func = _lambdify_c(_printer([(x, x**y)], {}, {x, y}))
    >>> func(
    ...     np.array([2.0   , np.nan, 0.0, 0.0,  0.0, -0.0,    2.0,     2.0]),
    ...     np.array([np.nan,    2.0, 0.0, 1.0, -1.0, -1.0, np.inf, -np.inf])
    ... )
    array([ nan,  nan,   1.,   0.,  inf, -inf,  inf,   0.])
    >>> func(np.array([1+1j]), np.array([1+1j]))
    array([0.27395725+0.58370076j])
    >>> func = _lambdify_c(_printer([(x, x**2)], {}, {x}))
    >>> func(np.array([np.nan, -np.inf, -2.0, -1.0, 1.0, 2.0, np.inf]))
    array([nan, inf,  4.,  1.,  1.,  4., inf])
    >>> func = _lambdify_c(_printer([(x, 1/x)], {}, {x}))
    >>> func(np.array([np.nan, -np.inf, -2.0, -1.0, -0.0, 0.0, 1.0, 2.0, np.inf]))
    array([ nan, -0. , -0.5, -1. , -inf,  inf,  1. ,  0.5,  0. ])
    >>> func = _lambdify_c(_printer([(x, x**.5)], {}, {x}))
    >>> func(np.array([np.nan, -np.inf, -1.0, 0.0, 1.0, 4.0, np.inf]))
    array([nan, nan, nan,  0.,  1.,  2., inf])
    >>> func = _lambdify_c(_printer([(x, x**(1/3))], {}, {x}))
    >>> func(np.array([np.nan, -np.inf, -8.0, -1.0, 0.0, 1.0, 8.0, np.inf]))
    array([ nan, -inf,  -2.,  -1.,   0.,   1.,   2.,  inf])
    >>> func = _lambdify_c(_printer([(x, x**(-7/2))], {}, {x}))
    >>> func(np.array([0.820335356007638]))
    array([2.])
    >>>
    """
    out_str = atom2str(out, indexing, c_type)

    if exp.is_number:
        exp_frac = Fraction(float(exp)).limit_denominator()

        # a**-b <=> 1/(a**b)
        if exp_frac.denominator <= 3 and exp_frac < 0:
            context, alloc, lines = c_pow(out, indexing, c_type, base, -exp)
            if (match := re.search(r" = (?P<inst>.+);$", lines[-1])) is not None:
                lines[-1] = (
                    f"{out_str} = {atom2str(One(), indexing, c_type)} / {match['inst']};"
                    if re.fullmatch(r"\S+(?:[\(\[].*[\)\]])?", match["inst"]) else
                    f"{out_str} = {atom2str(One(), indexing, c_type)} / ({match['inst']});"
                )
            else:
                lines.append(f"{out_str} = {atom2str(One(), indexing, c_type)}/{out_str};")
            return context, alloc, lines

        # a**(n/m) <=> (a**n)**(1/m)
        if (
            cfunc := {  # a**(1/2) <=> sqrt(a) or a**(1/3) <=> cbrt(a)
                (2, "float"): "sqrtf",
                (2, "double"): "sqrt",
                (2, "long double"): "sqrtl",
                (2, "float complex"): "csqrtf",
                (2, "double complex"): "csqrt",
                (2, "long double complex"): "csqrtl",
                (3, "float"): "cbrtf",
                (3, "double"): "cbrt",
                (3, "long double"): "cbrtl",
            }.get((exp_frac.denominator, c_type), None)
        ) is not None:
            context, alloc, lines = c_pow(out, indexing, c_type, base, Rational(exp_frac.numerator))
            if (match := re.search(r" = (?P<inst>.+);$", lines[-1])) is not None:
                lines[-1] = f"{out_str} = {cfunc}({match['inst']});"
            else:
                lines.append(f"{out_str} = {cfunc}({out_str});")
            return context, alloc, lines

        # a**n, n integer, use a**n <=> (a**2)**(n/2)
        if exp_frac.denominator == 1:
            return c_pow_pos_integer(out, indexing, c_type, base, Integer(exp_frac.numerator))

    # general case
    cfunc = {
        "float": "powf",
        "double": "pow",
        "long double": "powl",
        "float complex": "cpowf",
        "double complex": "cpow",
        "long double complex": "cpowl",
    }[c_type]
    return (
        set(),
        set(),
        [
            f"{out_str} = {cfunc}("
            f"{atom2str(base, indexing, c_type)}, {atom2str(exp, indexing, c_type)});"
        ],
    )


def c_pow_pos_integer(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, base: Atom, exp: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """Manage the special case of power where the exponant is a positive integer.

    Examples
    --------
    >>> from collections import defaultdict
    >>> from sympy.abc import x, y
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import c_pow_pos_integer
    >>>
    >>> # case allocation in new var
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 0)
    (set(), set(), ['y = 1.0f;'])
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 1)
    (set(), set(), ['y = x;'])
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 2)
    (set(), set(), ['y = x * x;'])
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 3)
    (set(), set(), ['y = x * x;', 'y *= x;'])
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 4)
    (set(), set(), ['y = x * x;', 'y *= y;'])
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 5)
    (set(), set(), ['y = x * x;', 'y *= y;', 'y *= x;'])
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 6)
    (set(), {_buf}, ['y = x * x;', '_buf = y;', 'y *= y;', 'y *= _buf;'])
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 7)
    (set(), {_buf}, ['y = x * x;', '_buf = x * y;', 'y *= y;', 'y *= _buf;'])
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 8)
    (set(), set(), ['y = x * x;', 'y *= y;', 'y *= y;'])
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 9)
    (set(), set(), ['y = x * x;', 'y *= y;', 'y *= y;', 'y *= x;'])
    >>> c_pow_pos_integer(y, defaultdict(lambda: ""), "float", x, 10)
    (set(), {_buf}, ['y = x * x;', '_buf = y;', 'y *= y;', 'y *= y;', 'y *= _buf;'])
    >>>
    >>> # case allocation inplace
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 0)
    (set(), set(), ['x = 1.0f;'])
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 1)
    (set(), set(), ['x = x;'])
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 2)
    (set(), set(), ['x *= x;'])
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 3)
    (set(), {_buf}, ['_buf = x;', 'x *= x;', 'x *= _buf;'])
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 4)
    (set(), set(), ['x *= x;', 'x *= x;'])
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 5)
    (set(), {_buf}, ['_buf = x;', 'x *= x;', 'x *= x;', 'x *= _buf;'])
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 6)
    (set(), {_buf}, ['x *= x;', '_buf = x;', 'x *= x;', 'x *= _buf;'])
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 7)
    (set(), {_buf}, ['_buf = x;', 'x *= x;', '_buf *= x;', 'x *= x;', 'x *= _buf;'])
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 8)
    (set(), set(), ['x *= x;', 'x *= x;', 'x *= x;'])
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 9)
    (set(), {_buf}, ['_buf = x;', 'x *= x;', 'x *= x;', 'x *= x;', 'x *= _buf;'])
    >>> c_pow_pos_integer(x, defaultdict(lambda: ""), "float", x, 10)
    (set(), {_buf}, ['x *= x;', '_buf = x;', 'x *= x;', 'x *= x;', 'x *= _buf;'])
    >>>
    """
    if exp in {0, 1}:
        return c_mul(out, indexing, c_type, *([base]*exp))
    context, alloc, lines = set(), set(), []

    # formal general code
    symb_code = []
    buf = Symbol("_buf")
    state = {out: base, buf: Integer(1)}
    while exp > 1:
        if exp % 2:  # odd exponant
            symb_code.append(Equality(
                buf,
                (
                    (state[buf] if state[buf].is_Atom else buf)
                    * (state[out] if state[out].is_Atom else out)
                )
            ))
            state[buf] = state[buf] * state[out]
            state[out] = state[out].subs(state, simultaneous=True)
        symb_code.append(Equality(out, (state[out] if state[out].is_Atom else out)**2))
        state[out] = state[out] * state[out]
        state[buf] = state[buf].subs(state, simultaneous=True)
        exp //= 2
    symb_code.append(
        Equality(
            out,
            (
                (state[out] if state[out].is_Atom else out)
                * (state[buf] if state[buf].is_Atom else buf)
            )
        )
    )

    # simplify
    symb_code = [eq for eq in symb_code if isinstance(eq, Equality)]  # remove `x = x` lines
    if any(buf in eq.args[1].free_symbols for eq in symb_code):
        alloc.add(buf)
    else:  # if buf is not used
        symb_code = [eq for eq in symb_code if eq.args[0] != buf]  # remove `buf = ...` lines
    # remove first item of var declaration
    buf = {  # at each line index, associate the new declared var
        i: eq.args[0] for i, eq in enumerate(symb_code) if eq.args[0] not in eq.args[1].free_symbols
    }
    buf = set.union(  # the index to remove
        set(), *(set([i for i, v_ in buf.items() if v_ is v][:-1]) for v in set(buf.values()))
    )
    symb_code = [eq for i, eq in enumerate(symb_code) if i not in buf]

    # # verification
    # state = {base: base}
    # for equ in symb_code:
    #     state[equ.args[0]] = equ.args[1].xreplace(state)
    # print(state[out])

    # convert into C code
    for var, buf in (eq.args for eq in symb_code):
        if buf.is_Atom:
            new_context, new_alloc, new_lines = c_mul(var, indexing, c_type, buf)
        elif isinstance(buf, Pow):
            new_context, new_alloc, new_lines = c_mul(var, indexing, c_type, *([buf.base]*buf.exp))
        else:  # case Mul
            new_context, new_alloc, new_lines = c_mul(var, indexing, c_type, *buf.args)
        context |= new_context
        alloc |= new_alloc
        lines.extend(new_lines)

    return context, alloc, lines


def c_sin(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, arg: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C sin operation.

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.functions.elementary.trigonometric import sin
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, sin(x))], {}, {x}))
    >>> func(np.array([np.nan]))
    array([nan])
    >>> func(np.array([0.78539816, 1.57079633, 2.35619449, 3.92699082, 4.71238898, 5.49778714]))
    array([ 0.70710678,  1.        ,  0.70710678, -0.70710678, -1.        ,
           -0.70710678])
    >>> func(np.array([1+1j]))
    array([1.29845758+0.63496391j])
    >>>
    """
    cfunc = {
        "float": "sinf",
        "double": "sin",
        "long double": "sinl",
        "float complex": "csinf",
        "double complex": "csin",
        "long double complex": "csinl",
    }[c_type]
    code = f"{atom2str(out, indexing, c_type)} = {cfunc}({atom2str(arg, indexing, c_type)});"
    return set(), set(), [code]


def c_strictgreaterthan(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, *parts: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C > operation, with module comparaison for complex numbers.

    Examples
    --------
    >>> from sympy.abc import x
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, x > 0)], {}, {x}))
    >>> func(np.array([-np.inf, -1.0, 0.0, 1.0, np.inf]))
    array([0., 0., 0., 1., 1.])
    >>>
    """
    return _comp(out, indexing, c_type, ">", *parts)


def c_strictlessthan(
    out: Symbol, indexing: collections.defaultdict[Symbol, str], c_type: str, *parts: Atom
) -> tuple[set[str], set[Symbol], list[str]]:
    """C < operation, with module comparaison for complex numbers.

    Examples
    --------
    >>> from sympy.abc import x
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _print_atomic, _printer
    >>> func = _lambdify_c(_printer([(x, x < 0)], {}, {x}))
    >>> func(np.array([-np.inf, -1.0, 0.0, 1.0, np.inf]))
    array([1., 1., 0., 0., 0.])
    >>>
    """
    return _comp(out, indexing, c_type, "<", *parts)
