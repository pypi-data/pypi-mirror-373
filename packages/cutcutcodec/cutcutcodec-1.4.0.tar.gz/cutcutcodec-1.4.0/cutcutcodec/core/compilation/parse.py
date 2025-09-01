#!/usr/bin/env python3

"""Extracting information from string."""

from fractions import Fraction
import math
import numbers
import tokenize

from sympy.core.basic import Basic
from sympy.core.symbol import Symbol
from sympy.core.sympify import sympify, SympifyError
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication


def parse_to_number(number: str | numbers.Real) -> Fraction | float:
    """Convert the number into fraction, or inf float.

    Raises
    ------
    ValueError
        If is not correct.

    Examples
    --------
    >>> import math
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.parse import parse_to_number
    >>> parse_to_number("0")
    Fraction(0, 1)
    >>> parse_to_number("2/3")
    Fraction(2, 3)
    >>> parse_to_number("-1e-3")
    Fraction(-1, 1000)
    >>> parse_to_number(1)
    Fraction(1, 1)
    >>> parse_to_number(1.0)
    Fraction(1, 1)
    >>> parse_to_number("inf")
    inf
    >>> parse_to_number("oo")
    inf
    >>> parse_to_number(math.inf)
    inf
    >>> parse_to_number("1k")
    Fraction(1000, 1)
    >>> parse_to_number("2.3M")
    Fraction(2300000, 1)
    >>>
    """
    if isinstance(number, str):
        number = number.replace("k", "e3").replace("M", "e6")
        try:
            return Fraction(number)
        except ValueError as err_frac:
            number = number.replace("oo", "inf")
            try:
                return float(number)
            except ValueError as err_float:
                raise err_float from err_frac
    if isinstance(number, numbers.Real):
        try:
            return Fraction(number)
        except OverflowError:
            return math.inf if number > 0 else -math.inf
    raise TypeError(f"only str and numbers type can be cast, not {number.__class__.__name__}")


def parse_to_sympy(
    expr: str | Basic | numbers.Complex, symbols: dict[str, Symbol] = None
) -> Basic:
    """Convert the expression in sympy compilable expression.

    Parameters
    ----------
    expr : str or sympy.Expr
        The string representation of the equation.
        Some operators like multiplication can be implicit.
    symbols : dict[str, sympy.Symbol]
        A dictionary of local variables to use when parsing.

    Returns
    -------
    sympy.core.expr.Expr
        The version sympy of the expression.

    Raises
    ------
    SyntaxError
        If the entered expression does not allow to properly define an equation.

    Examples
    --------
    >>> from cutcutcodec.core.compilation.parse import parse_to_sympy
    >>> parse_to_sympy(0)
    0
    >>> parse_to_sympy("1/2 + 1/2*cos(2pi(t - i*j))")
    1*cos(2*pi*(-i*j + t))/2 + 1/2
    >>>
    """
    if symbols is not None:
        assert isinstance(symbols, dict), symbols.__class__.__name__
        assert all(isinstance(k, str) for k in symbols), symbols
    if isinstance(expr, str):
        if not expr:
            raise SyntaxError("impossible to parse an empty expr")
        transformations = standard_transformations + (implicit_multiplication,)
        try:
            expr = parse_expr(
                expr, local_dict=symbols, transformations=transformations, evaluate=False
            )
        except (SympifyError, tokenize.TokenError, TypeError) as err:
            raise SyntaxError(f"failed to parse {expr}") from err
    elif isinstance(expr, numbers.Complex):
        expr = sympify(expr, locals=symbols, evaluate=True)
    if not isinstance(expr, Basic):
        raise SyntaxError(f"need to be expression, not {expr.__class__.__name__}")
    try:
        str(expr)
    except AttributeError as err:  # ex "1+()"
        raise SyntaxError("expression parsing is corrupted") from err
    return expr
