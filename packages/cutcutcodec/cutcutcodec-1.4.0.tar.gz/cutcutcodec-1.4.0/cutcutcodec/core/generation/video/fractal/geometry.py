#!/usr/bin/env python3

"""Deduce the missing vars with a given set."""

from sympy.core.basic import Basic
from sympy.core.relational import Equality
from sympy.core.symbol import Symbol
from sympy.sets.sets import EmptySet
from sympy.solvers.solveset import linsolve


SYMBOLS = {
    # references
    "i_min": Symbol("i_min", real=True),
    "j_min": Symbol("j_min", real=True),
    "i_max": Symbol("i_max", real=True),
    "j_max": Symbol("j_max", real=True),

    # others
    "x_min": Symbol("x_min", real=True),
    "y_min": Symbol("y_min", real=True),
    "x_max": Symbol("x_max", real=True),
    "y_max": Symbol("y_max", real=True),

    "i_center": Symbol("i_center", real=True),
    "j_center": Symbol("j_center", real=True),
    "x_center": Symbol("x_center", real=True),
    "y_center": Symbol("y_center", real=True),

    "i_size": Symbol("i_size", real=True),
    "j_size": Symbol("j_size", real=True),
    "x_size": Symbol("x_size", real=True),
    "y_size": Symbol("y_size", real=True),
}

EQUATIONS = [
    Equality(SYMBOLS["x_min"], SYMBOLS["j_min"]),
    Equality(SYMBOLS["y_min"], SYMBOLS["i_max"]),
    Equality(SYMBOLS["x_max"], SYMBOLS["j_max"]),
    Equality(SYMBOLS["y_max"], SYMBOLS["i_min"]),
    Equality(SYMBOLS["i_center"], SYMBOLS["i_min"]/2 + SYMBOLS["i_max"]/2),
    Equality(SYMBOLS["j_center"], SYMBOLS["j_min"]/2 + SYMBOLS["j_max"]/2),
    Equality(SYMBOLS["x_center"], SYMBOLS["x_min"]/2 + SYMBOLS["x_max"]/2),
    Equality(SYMBOLS["y_center"], SYMBOLS["y_min"]/2 + SYMBOLS["y_max"]/2),
    Equality(SYMBOLS["i_size"], SYMBOLS["i_max"] - SYMBOLS["i_min"]),
    Equality(SYMBOLS["j_size"], SYMBOLS["j_max"] - SYMBOLS["j_min"]),
    Equality(SYMBOLS["x_size"], SYMBOLS["x_max"] - SYMBOLS["x_min"]),
    Equality(SYMBOLS["y_size"], SYMBOLS["y_max"] - SYMBOLS["y_min"]),
]


def deduce_all_bounds(**bounds: dict[str, Basic]) -> dict[str, Basic]:
    """Solve the system for extracting the values of the i, j bounds.

    Parameters
    ----------
    **bounds : dict[str, sympy.code.basic.Basic]
        The values of the given vars.
        The considerated keys are the keys presents in the ``SYMBOLS`` dict.

    Returns
    -------
    all_bounds : dict[str, sympy.code.basic.Basic]
        The expressions associated to all the values of ``SYMBOLS`` keys.

    Raises
    ------
    ValueError
        If input is not valid or if the linear system is inconsistent.

    Examples
    --------
    >>> from sympy.core.symbol import Symbol
    >>> from sympy.core.sympify import sympify
    >>> from cutcutcodec.core.generation.video.fractal.geometry import deduce_all_bounds
    >>> solutions = deduce_all_bounds(
    ...     x_center=Symbol("t", real=True, positive=True)/2,
    ...     y_center=sympify(1),
    ...     x_size=sympify(2),
    ...     y_size=1 + Symbol("t", real=True, positive=True)**2,
    ... )
    >>> solutions["i_min"]
    t**2/2 + 3/2
    >>> solutions["i_max"]
    1/2 - t**2/2
    >>> solutions["j_min"]
    t/2 - 1
    >>> solutions["j_max"]
    t/2 + 1
    >>>
    """
    assert all(n in SYMBOLS for n in bounds), f"{set(bounds) - set(SYMBOLS)} are not allowed"
    assert all(isinstance(e, Basic) for e in bounds.values()), bounds
    assert len(bounds) == 4, f"only 4 expressions are required, not {len(bounds)}"

    new_eqs = [Equality(SYMBOLS[name], expr) for name, expr in bounds.items()]
    ordered_symbs = list(SYMBOLS)  # not list(SYMBOLS.values()) for frozen order
    if (sols := linsolve(EQUATIONS + new_eqs, [SYMBOLS[s] for s in ordered_symbs])) is EmptySet:
        raise ValueError(f"not enouth provided informations for solving bounds {new_eqs}")
    return dict(zip(ordered_symbs, sols.args[0]))
