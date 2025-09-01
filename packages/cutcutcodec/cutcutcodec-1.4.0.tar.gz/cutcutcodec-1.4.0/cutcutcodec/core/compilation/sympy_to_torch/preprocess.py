#!/usr/bin/env python3

"""Prepare the work for the Printer, decompose and analyse."""

from collections import OrderedDict
import itertools
import re

from sympy.core.basic import Basic
from sympy.core.containers import Tuple
from sympy.core.numbers import Float, Integer
from sympy.core.symbol import Symbol
from sympy.logic.boolalg import BooleanFalse, BooleanTrue
from sympy.simplify.cse_main import cse
import sympy


def _broadcast(
    symb_expr: list[tuple[Symbol, Basic]], shapes: set[frozenset[Symbol]]
) -> dict[Symbol, frozenset[Symbol]]:
    r"""Find the shape of all the sub vars.

    Complexity o(n).

    Parameters
    ----------
    symb_expr : list[tuple[sympy.core.symbol.Symbol, sympy.core.basic.Basic]]
        The list of symbols and atomic expressions.
    shapes : set[frozenset[sympy.core.symbol.Symbol]]
        The initials shapes. For a more complete description, please refer to
        ``cutcutcodec.core.compilation.sympy_to_torch.preprocess.preprocess``.

    Returns
    -------
    shapes : dict[sympy.core.symbol.Symbol, frozenset[sympy.core.symbol.Symbol]]
        All the shapes, for each intermediate vars, associate the broadcast shape of the tensor.

    Examples
    --------
    >>> from pprint import pprint
    >>> from sympy.abc import c, x
    >>> from sympy import Number, Tuple, sin, symbols
    >>> from cutcutcodec.core.compilation.sympy_to_torch.preprocess import _broadcast
    >>> _, _0, _1, _2, _3, _4, _5, _6, _7, _8, _9, _10, _11 = symbols("_ _:12")
    >>> tree = [(_1, c**(-2)), (_2, 1/x), (_0, _1*_2), (_3, Number(0)), (_6, sin(x)),
    ...         (_5, sin(_6)), (_4, _5 + 1), (_7, c), (_8, c), (_9, x), (_10, x),
    ...         (_11, _0), (_, Tuple(_3, _7, _8, _9, _10, _0, _11, _4))]
    >>> shapes = _broadcast(tree, set())
    >>> pprint({v: sorted(shapes[v], key=str) for v in sorted(shapes, key=str)}, sort_dicts=False)
    {_0: [c, x],
     _1: [c],
     _10: [x],
     _11: [c, x],
     _2: [x],
     _3: [],
     _4: [x],
     _5: [x],
     _6: [x],
     _7: [c],
     _8: [c],
     _9: [x],
     c: [c],
     x: [x]}
    >>> shapes = _broadcast(tree, {frozenset({c, x})})
    >>> pprint({v: sorted(shapes[v], key=str) for v in sorted(shapes, key=str)}, sort_dicts=False)
    {_0: [c],
     _1: [c],
     _10: [c],
     _11: [c],
     _2: [c],
     _3: [],
     _4: [c],
     _5: [c],
     _6: [c],
     _7: [c],
     _8: [c],
     _9: [c],
     c: [c],
     x: [c]}
    >>>
    """
    # simplification of given shapes, remove single and merge common
    shapes_simplified = []
    for shape in (set(s) for s in shapes if s):
        merge = False
        for shape_ in shapes_simplified:
            if shape & shape_:
                shape_ |= shape  # has to be set, not frozenset for inplace operation
                merge = True
        if not merge:
            shapes_simplified.append(shape)
    shapes_simplified = [frozenset(s) for s in shapes_simplified]

    # parse shapes into dict
    min_of_set = {s: frozenset((min(s, key=str),)) for s in shapes_simplified}
    all_shapes = {symb: min_of_set[s] for s in shapes_simplified for symb in s}

    # exploration of the tree
    for symb, expr in symb_expr:
        if isinstance(expr, Tuple):
            continue
        if (free_symbols := expr.free_symbols):
            all_shapes[symb] = frozenset.union(
                *(all_shapes.get(s, frozenset((s,))) for s in free_symbols)
            )
            for free_symbol in free_symbols:
                all_shapes[free_symbol] = all_shapes.get(free_symbol, frozenset((free_symbol,)))
        else:  # case expr is numbers
            all_shapes[symb] = frozenset()
    return all_shapes


def _expr_to_atomic(expr: Basic, *, _symbols=None) -> list[tuple[Symbol, Basic]]:
    """Apply ``cse`` and split the sub patterns.

    Sum and product expressions can contain more than 2 terms.

    Parameters
    ----------
    expr : sympy.core.basic.Basic
        The sympy expression to split.

    Returns
    -------
    replacements : list of (Symbol, expression) pairs
        All of the common subexpressions that were replaced.
        All subexpressions are atomic.

    Examples
    --------
    >>> from pprint import pprint
    >>> from sympy.abc import c, x
    >>> from sympy import Tuple, sin
    >>> from cutcutcodec.core.compilation.sympy_to_torch.preprocess import _expr_to_atomic
    >>> exp = Tuple(0, c, c, x, x, c**-2/x, c**-2/x, sin(sin(x)) + 1)
    >>> pprint(_expr_to_atomic(exp))
    [(_1, c**(-2)),
     (_2, 1/x),
     (_0, _1*_2),
     (_5, sin(x)),
     (_4, sin(_5)),
     (_3, _4 + 1),
     (_6, 0),
     (_7, c),
     (_8, c),
     (_9, x),
     (_10, x),
     (_11, _0),
     (_, (_6, _7, _8, _9, _10, _0, _11, _3))]
    >>>
    """
    # initialisation
    if _symbols is None:
        _symbols = iter(Symbol(f"_{i}") for i in itertools.count())
        rep, last = cse(expr, symbols=_symbols, order="none", list=False)  # fastest as possible
        rep.append(((Symbol("_") if isinstance(expr, Tuple) else next(_symbols)), last))
    else:  # if cse is already called
        rep = [(next(_symbols), expr)]

    # main
    atom_rep = []
    for var, sub_expr in rep:
        if sub_expr.is_Atom:
            atom_rep.append((var, sub_expr))
            continue
        subs = {}
        for arg in sub_expr.args:
            if (
                arg in subs  # we don't do the same calculs several times
                or arg.is_Atom  # replace if sub expr is not atomic
            ):
                continue
            atom_rep += _expr_to_atomic(arg, _symbols=_symbols)
            subs[arg] = (
                atom_rep.pop(-1)[1] if isinstance(atom_rep[-1][1], Tuple) else atom_rep[-1][0]
            )
        if subs:
            sub_expr = sub_expr.xreplace(subs)
        # make sure no duplicate and no intermediate variables
        if isinstance(sub_expr, Tuple) and str(var) == "_":
            args = []  # this ensures the independence of the output variables
            for arg in sub_expr.args:
                if arg in args or not re.fullmatch(r"_\d+", str(arg)):
                    atom_rep.append((next(_symbols), arg))
                    args.append(atom_rep[-1][0])
                else:
                    args.append(arg)
            sub_expr = Tuple(*args)
        atom_rep.append((var, sub_expr))

    return atom_rep


def _get_args(symb_expr: list[tuple[Symbol, Basic]]) -> tuple[set[Symbol], set[Symbol]]:
    """Search the parameters and islotate wich one are changing inplace.

    Complexity o(n).

    Parameters
    ----------
    symb_expr : list[tuple[sympy.core.symbol.Symbol, sympy.core.basic.Basic]]
        The list of symbols and atomic expressions.

    Returns
    -------
    all_args : set[sympy.core.symbol.Symbol]
        All the input arguments
    args_no_safe : set[sympy.core.symbol.Symbol]
        The subset of arguments that is not read-only.
        These arguments are modified inplace in the function
        If the value of these arguments has to be concerved,
        then a copy of these arguments should be passed to the function.
    alloc : set[sympy.core.symbol.Symbol]
        All the internal sub vars

    Examples
    --------
    >>> from pprint import pprint
    >>> from sympy.abc import c, x
    >>> from sympy import Number, Tuple, sin, symbols
    >>> from cutcutcodec.core.compilation.sympy_to_torch.preprocess import _get_args
    >>> _, _0, _1, _2, _3, _4, _5, _6, _7, _8, _9, _10, _11 = symbols("_ _:12")
    >>> tree = [(_1, c**(-2)), (_2, 1/x), (_0, _1*_2), (_3, Number(0)), (_6, sin(x)),
    ...         (_5, sin(_6)), (_4, _5 + 1), (_7, c), (_8, c), (_9, x), (_10, x),
    ...         (_11, _0), (_, Tuple(_3, _7, _8, _9, _10, _0, _11, _4))]
    >>> args, no_safe, alloc = _get_args(tree)
    >>> sorted(args, key=str)
    [c, x]
    >>> sorted(no_safe, key=str)
    []
    >>> sorted(alloc, key=str)
    [_, _0, _1, _10, _11, _2, _3, _4, _5, _6, _7, _8, _9]
    >>>
    """
    all_args, no_safe, alloc = set(), set(), set()
    for symb, expr in symb_expr:
        symbs = expr.free_symbols
        all_args |= symbs - alloc
        if symb in all_args and expr != symb:
            no_safe.add(symb)
        else:
            alloc.add(symb)
    return all_args, no_safe, alloc


def _isolate_cst_dyn(
    symb_expr: list[tuple[Symbol, Basic]], cst_args: set[Symbol]
) -> tuple[list[tuple[Symbol, Basic]], list[tuple[Symbol, Basic]]]:
    """Isolate the constant subexpressions.

    Complexity o(n).

    Parameters
    ----------
    symb_expr : list[tuple[sympy.core.symbol.Symbol, sympy.core.basic.Basic]]
        Returned value of ``_expr_to_atomic``.
    cst_args : set[sympy.core.symbol.Symbol]
        The constants input parameters.
        The subexpressions of this parameters will be cached.

    Returns
    -------
    cst_tree : list[tuple[sympy.core.symbol.Symbol, sympy.core.basic.Basic]]
        The graph to compute the constant sub expressions.
        The last value is a ``sympy.core.containers.Tuple``.
    dyn_tree : list[tuple[sympy.core.symbol.Symbol, sympy.core.basic.Basic]]
        The main tree containing only dynamic expressions.

    Examples
    --------
    >>> from pprint import pprint
    >>> from sympy.abc import c, x
    >>> from sympy import Number, Tuple, sin, symbols
    >>> from cutcutcodec.core.compilation.sympy_to_torch.preprocess import _isolate_cst_dyn
    >>> _, _0, _1, _2, _3, _4, _5, _6, _7, _8, _9, _10, _11 = symbols("_ _:12")
    >>> tree = [(_1, c**(-2)), (_2, 1/x), (_0, _1*_2), (_3, Number(0)), (_6, sin(x)),
    ...         (_5, sin(_6)), (_4, _5 + 1), (_7, c), (_8, c), (_9, x), (_10, x),
    ...         (_11, _0), (_, Tuple(_3, _7, _8, _9, _10, _0, _11, _4))]
    >>> cst, dyn = _isolate_cst_dyn(tree, {c})
    >>> pprint(cst)
    [(_1, c**(-2)), (_7, c), (_8, c), (_, (_1, _7, _8))]
    >>> pprint(dyn)
    [(_2, 1/x),
     (_0, _1*_2),
     (_3, 0),
     (_6, sin(x)),
     (_5, sin(_6)),
     (_4, _5 + 1),
     (_9, x),
     (_10, x),
     (_11, _0),
     (_, (_3, _7, _8, _9, _10, _0, _11, _4))]
    >>>
    """
    # detection of cst sub expressions
    csts = set()  # contains all the cst sub symbols
    for symb, expr in symb_expr:
        if (
            not expr.is_number
            and not isinstance(expr, BooleanTrue)
            and not isinstance(expr, BooleanFalse)
            and all(s in cst_args or s in csts for s in expr.free_symbols)
        ):
            csts.add(symb)

    # split the constant and the dynamic sub graphs
    cst_tree = []
    dyn_tree = []
    for symb, expr in symb_expr:
        if symb in csts:  # if the expression is constant
            cst_tree.append((symb, expr))
        else:
            dyn_tree.append((symb, expr))

    # special case all the tree is constant
    if not dyn_tree:
        dyn_tree.append((Symbol("_"), symb_expr[-1][0]))

    # selection of usefull cst symbols
    final_csts = set()
    for symb, expr in dyn_tree:
        for sub_symb in expr.free_symbols:
            if sub_symb in csts and sub_symb not in final_csts:  # we keep the statics parts
                final_csts.add(sub_symb)
    cst_tree.append((Symbol("_"), Tuple(*sorted(final_csts, key=str))))

    return cst_tree, dyn_tree


def _limit_realoc(
    symb_expr: list[tuple[Symbol, Basic]],
    broadcasted_shapes: dict[Symbol, frozenset[Symbol]],
    safe: set[Symbol],
) -> dict[Symbol, set[Symbol]]:
    """Optimises memory by reusing as many old variables as possible.

    Complexity o(n**2).
    The ``sympy.core.containers.Tuple`` expressions are not considered.

    Parameters
    ----------
    symb_expr : list[tuple[sympy.core.symbol.Symbol, sympy.core.basic.Basic]]
        The list of symbols and atomic expressions.
    broadcasted_shapes : dict[sympy.core.symbol.Symbol, frozenset[sympy.core.symbol.Symbol]]
        For each var, associate the broadcasted shape,
        Output of ``cutcutcodec.core.compilation.sympy_to_torch.preprocess._broadcast``.
    safe : set[sympy.core.symbol.Symbol]
        The variables to keep safe. For a more complete description, please refer to
        ``cutcutcodec.core.compilation.sympy_to_torch.preprocess.preprocess``.

    Returns
    -------
    alloc : dict[sympy.core.symbol.Symbol, set[sympy.core.symbol.Symbol]]
        The intermediate variables to be declared and their respective dimensions.
    symb_expr : list[tuple[sympy.core.symbol.Symbol, sympy.core.basic.Basic]]
        The new equivalent tree that minimize the realocation and take care of the shapes.

    Examples
    --------
    >>> from pprint import pprint
    >>> from sympy.abc import c, x
    >>> from sympy import Number, Tuple, sin, symbols
    >>> from cutcutcodec.core.compilation.sympy_to_torch.preprocess import _broadcast, _limit_realoc
    >>> _, _0, _1, _2, _3, _4, _5, _6, _7, _8, _9, _10, _11 = symbols("_ _:12")
    >>> tree = [(_1, c**(-2)), (_2, 1/x), (_0, _1*_2), (_3, Number(0)), (_6, sin(x)),
    ...         (_5, sin(_6)), (_4, _5 + 1), (_7, c), (_8, c), (_9, x), (_10, x),
    ...         (_11, _0), (_, Tuple(_3, _7, _8, _9, _10, _0, _11, _4))]
    >>> alloc, tree = _limit_realoc(tree, _broadcast(tree, set()), {c, x})
    >>> pprint({v: sorted(alloc[v], key=str) for v in sorted(alloc, key=str)}, sort_dicts=False)
    {_0: [c, x], _1: [c], _10: [x], _11: [c, x], _2: [x], _3: [], _8: [c], _9: [x]}
    >>> pprint(tree)
    [(_1, c**(-2)),
     (_2, 1/x),
     (_0, _1*_2),
     (_3, 0),
     (_2, sin(x)),
     (_2, sin(_2)),
     (_2, _2 + 1),
     (_1, c),
     (_8, c),
     (_9, x),
     (_10, x),
     (_11, _0),
     (_, (_3, _1, _8, _9, _10, _0, _11, _2))]
    >>> alloc, tree = _limit_realoc(tree, _broadcast(tree, {frozenset({c, x})}), set())
    >>> pprint({v: sorted(alloc[v], key=str) for v in sorted(alloc, key=str)}, sort_dicts=False)
    {_0: [c], _1: [c], _11: [c], _2: [c], _3: [], _9: [c]}
    >>> pprint(tree)
    [(_1, c**(-2)),
     (_2, 1/x),
     (_0, _1*_2),
     (_3, 0),
     (_2, sin(x)),
     (_2, sin(_2)),
     (_2, _2 + 1),
     (_1, c),
     (_9, x),
     (_11, _0),
     (_, (_3, _1, c, _9, x, _0, _11, _2))]
    >>>
    """
    args, _, _ = _get_args(symb_expr)

    # at each step, find the new free sub symbols
    used = [set()]
    for _, expr in reversed(symb_expr):
        used.insert(0, used[0] | expr.free_symbols)
    all_new_free: list[set[Symbol]] = (  # each step, the new free vars o(n**2)
        [(u1-u2)-safe for u1, u2 in zip(used[:-1], used[1:])]
    )

    # replacement line by line
    new_tree: list[tuple[Symbol, Basic]] = []  # the new tree with substitutions
    free: set[Symbol] = set()  # the free symbols at the current step i
    subs: dict[Symbol, Symbol] = {}  # each old name, associate the new one
    for new_free, (old_symb, old_expr) in zip(all_new_free, symb_expr):
        # replace old vars by new
        symb = subs.get(old_symb, old_symb)
        expr = old_expr.xreplace(subs)
        free |= {subs.get(s, s) for s in new_free}
        # particular case
        if isinstance(old_expr, Tuple):  # particular case of tuple, end of tree
            new_tree.append((symb, expr))
            break
        # selection of the new substitution variable
        # to disable W0640, the following code work, but is is safe here
        # symbs = {f for f in free if broadcasted_shapes[f] == broadcasted_shapes[symb]}
        # criteria = {s: ((s != expr), (not str(s).startswith("_")), str(s)) for s in symbs}
        # symb = min(symbs, key=criteria.get, default=symb)
        symb = min(
            {f for f in free if broadcasted_shapes[f] == broadcasted_shapes[symb]},
            key=lambda s: (
                (s != expr), (not str(s).startswith("_")), str(s)  # pylint: disable=W0640
            ),
            default=symb,
        )
        if symb != expr:
            new_tree.append((symb, expr))
        # updates the context
        free -= {symb}
        subs[old_symb] = symb
        subs = {o: subs.get(n, n) for o, n in subs.items()}
        broadcasted_shapes = {subs.get(s, s): v for s, v in broadcasted_shapes.items()}

    # search for allocated variables and their size
    alloc = {a: s for a, s in broadcasted_shapes.items() if a not in args}
    return alloc, new_tree


def _rename(
    symb_expr: list[tuple[Symbol, Basic]], subs: dict[Symbol, Symbol], *, return_subs=False
) -> list[tuple[Symbol, Basic]]:
    """Replace and rename the symbols in canonical order.

    Complexity o(n).

    Parameters
    ----------
    symb_expr : list[tuple[sympy.core.symbol.Symbol, sympy.core.basic.Basic]]
        The list of symbols and atomic expressions.
    subs : dict[sympy.core.symbol.Symbol, sympy.core.symbol.Symbol]
        The replacement name of some symbols.
    return_subs : boolean, defaul=False
        If set to True, return the dictionary of the substitutions.

    Returns
    -------
    new_tree : list[tuple[sympy.core.symbol.Symbol, sympy.core.basic.Basic]]
        The renamed elements.

    Examples
    --------
    >>> from pprint import pprint
    >>> from sympy.abc import c, x
    >>> from sympy import Number, Tuple, sin, symbols
    >>> from cutcutcodec.core.compilation.sympy_to_torch.preprocess import _rename
    >>> _, _0, _1, _2, _3, _4, _5, _6, _7, _8, _9, _10, _11 = symbols("_ _:12")
    >>> tree = [(_1, c**(-2)), (_2, 1/x), (_0, _1*_2), (_3, Number(0)), (_6, sin(x)),
    ...         (_5, sin(_6)), (_4, _5 + 1), (_7, c), (_8, c), (_9, x), (_10, x),
    ...         (_11, _0), (_, Tuple(_3, _7, _8, _9, _10, _0, _11, _4))]
    >>> pprint(_rename(tree, {}))
    [(_0, c**(-2)),
     (_1, 1/x),
     (_2, _0*_1),
     (_3, 0),
     (_4, sin(x)),
     (_5, sin(_4)),
     (_6, _5 + 1),
     (_7, c),
     (_8, c),
     (_9, x),
     (_10, x),
     (_11, _2),
     (_, (_3, _7, _8, _9, _10, _2, _11, _6))]
    >>> tree = [(_1, c**(-2)), (_2, 1/x), (_0, _1*_2), (_3, Number(0)), (_2, sin(x)),
    ...         (_2, sin(_2)), (_2, _2 + 1), (_1, c), (_9, x), (_11, _0),
    ...         (_, Tuple(_3, _1, c, _9, x, _0, _11, _2))]
    >>> pprint(_rename(tree, {}))
    [(_0, c**(-2)),
     (_1, 1/x),
     (_2, _0*_1),
     (_3, 0),
     (_1, sin(x)),
     (_1, sin(_1)),
     (_1, _1 + 1),
     (_0, c),
     (_4, x),
     (_5, _2),
     (_, (_3, _0, c, _4, x, _2, _5, _1))]
    >>>
    """
    subs_local = subs.copy()
    renamed_tree = []
    symbols = iter(Symbol(f"_{i}") for i in itertools.count())

    for symb, expr in symb_expr:
        if symb not in subs_local and re.fullmatch(r"_\d+", str(symb)):
            subs_local[symb] = next(symbols)
        renamed_tree.append((subs_local.get(symb, symb), expr.xreplace(subs_local)))

    if return_subs:
        return subs_local, renamed_tree
    return renamed_tree


def evalf(expr: Basic, prec: int = 37, simplify: bool = False) -> Basic:
    """Numerical eval and simplification of the expression.

    Parameters
    ----------
    expr : sympy.Expr
        The sympy expression to symplify as numerical evaluable.
    prec : int, default=37
        The number of decimals, to comply with the standards, you can use the following values:
        * float128 -> 37
        * float64 -> 18
        * float32 -> 10
    simplify : boolean, default=False
        If set to True, it tries to simplify the expression
        in order to improve the numerical evaluation.

    Returns
    -------
    sympy.Expr
        The quite equivalent expression with floats.

    Examples
    --------
    >>> import sympy
    >>> from cutcutcodec.core.compilation.sympy_to_torch.preprocess import evalf
    >>> evalf(sympy.pi)
    3.141592653589793238462643383279502884
    >>> evalf(sympy.sin(sympy.sin(1)))
    0.7456241416655578888931510704303837921
    >>> evalf(sympy.sqrt(2))
    1.414213562373095048801688724209698079
    >>> evalf(sympy.sympify("-2.0*x"))
    -2.0*x
    >>> evalf(sympy.sympify("(x/(2.0*x+2.0))**100.0"))
    (x/(2.0*x + 2.0))**100.0
    >>> evalf(sympy.sympify("sqrt(x)"))
    x**0.5
    >>>
    """
    assert isinstance(expr, Basic), expr.__class__.__name__
    assert isinstance(prec, int), prec.__class__.__name__
    assert prec >= 1, prec
    assert isinstance(simplify, bool), simplify.__class__.__name__

    # to numerical
    if isinstance(expr, Tuple):
        return Tuple(*map(evalf, expr))
    sub = expr.atoms(sympy.Float, sympy.NumberSymbol, sympy.Rational) - expr.atoms(Integer)
    expr = expr.xreplace({s: s.evalf(n=prec) for s in sub})
    expr = expr.evalf(n=prec)
    sub = {s: round(s) for s in expr.atoms(Float)}  # float to int
    sub = {s: i for s, i in sub.items() if float(s) in {-1.0, 0.0, 1.0}}
    expr = expr.xreplace(sub)

    # simplification
    if not simplify:
        return expr
    expr = sympy.rcollect(expr, *sorted(expr.atoms(sympy.Float, sympy.Symbol), key=str))
    expr = sympy.trigsimp(expr)
    expr = sympy.logcombine(expr, force=True)
    expr = sympy.powsimp(expr, force=True, deep=True)
    return expr


def preprocess(
    expr: Basic, cst_args: set[Symbol], shapes: set[frozenset[Symbol]], safe: set[Symbol]
) -> tuple[list[tuple[Symbol, Basic]], dict[Symbol, set[Symbol]], list[tuple[Symbol, Basic]]]:
    """Decompose and analyse the expression for the printer.

    Parameters
    ----------
    expr : sympy.core.basic.Basic
        The complete sympy expression to compile.
    cst_args : set[sympy.core.symbol.Symbol], optional
        Arguments that change infrequently enough to be cached.
    shapes : set[frozenset[sympy.core.symbol.Symbol]], optional
        If some parameters have the same shape, it is possible to give this information
        in order to find a more optimal solution for limited the allocations.
        It variable represents the set of all tensor subsets with the same shapes.
        For example, {frozenset({a, b, c}), frozenset({x, y})} means that
        a, b, and c are the same shape, and x and y as well.
    safe : set[sympy.core.symbol.Symbol]
        A subset of arguments that should definitely not be modified in place
        or returned without a copy. The variables provided to this set are safe.
        Arguments not present in this set can be reused internally in order to optimize memory.

    Returns
    -------
    tree : dict
        cst_args : set[sympy.core.symbol.Symbol]
            All the inputs arguments required for the cst tree input.
        cst_alloc : dict[sympy.core.symbol.Symbol, set[sympy.core.symbol.Symbol]]
            The intermediate variables to be declared and their respective dimensions for cst tree.
        cst_tree : list[tuple[sympy.core.symbol.Symbol, None | sympy.core.basic.Basic]]
            Each steps of the cached function.
        dyn_args : set[sympy.core.symbol.Symbol]
            All the inputs arguments required for the dyn tree input.
        dyn_alloc : dict[sympy.core.symbol.Symbol, set[sympy.core.symbol.Symbol]]
            The intermediate variables to be declared and their respective dimensions for dyn tree.
        dyn_tree : list[tuple[sympy.core.symbol.Symbol, None | sympy.core.basic.Basic]]
            Each steps of the main function.

    Examples
    --------
    >>> from pprint import pprint
    >>> from sympy.abc import c, x
    >>> from sympy import Tuple, sin
    >>> from cutcutcodec.core.compilation.sympy_to_torch.preprocess import preprocess
    >>> exp = Tuple(0, c, c, x, x, c**-2/x, c**-2/x, sin(sin(x)) + 1)
    >>> def print_tree(tree):
    ...     print(
    ...         "cst_alloc:",
    ...         {
    ...             s: sorted(tree["cst_alloc"][s], key=str)
    ...             for s in sorted(tree["cst_alloc"], key=str)
    ...         }
    ...     )
    ...     print("cst_tree:")
    ...     pprint(tree["cst_tree"])
    ...     print(
    ...         "dyn_alloc:",
    ...         {
    ...             s: sorted(tree["dyn_alloc"][s], key=str)
    ...             for s in sorted(tree["dyn_alloc"], key=str)
    ...         }
    ...     )
    ...     print("dyn_tree:")
    ...     pprint(tree["dyn_tree"])
    ...
    >>> tree = preprocess(exp, {c}, set(), {c, x})
    >>> print_tree(tree)
    cst_alloc: {_cst_0: [c], _cst_1: [c], _cst_2: [c]}
    cst_tree:
    [(_cst_0, c**(-2)), (_cst_1, c), (_cst_2, c), (_, (_cst_0, _cst_1, _cst_2))]
    dyn_alloc: {_0: [x], _1: [c, x], _2: [], _3: [x], _4: [x], _5: [c, x]}
    dyn_tree:
    [(_0, 1/x),
     (_1, _0*_cst_0),
     (_0, sin(x)),
     (_0, sin(_0)),
     (_0, _0 + 1),
     (_2, 0),
     (_3, x),
     (_4, x),
     (_5, _1),
     (_, (_2, _cst_1, _cst_2, _3, _4, _1, _5, _0))]
    >>> tree = preprocess(exp, set(), {frozenset({c, x})}, set())
    >>> print_tree(tree)
    cst_alloc: {c: [c], x: [c]}
    cst_tree:
    [(_, ())]
    dyn_alloc: {_0: [c], _1: [c], _2: [], _3: [c], _4: [c], _5: [c]}
    dyn_tree:
    [(_0, c**(-2)),
     (_1, 1/x),
     (_0, _0*_1),
     (_1, sin(x)),
     (_1, sin(_1)),
     (_1, _1 + 1),
     (_2, 0),
     (_3, c),
     (_4, x),
     (_5, _0),
     (_, (_2, _3, c, _4, x, _0, _5, _1))]
    >>>
    """
    assert isinstance(expr, Basic), expr.__class__.__name__
    assert isinstance(cst_args, set), cst_args.__class__.__name__
    assert all(isinstance(s, Symbol) for s in cst_args), cst_args
    assert cst_args.issubset(expr.free_symbols), f"{cst_args} not in {expr}"
    assert isinstance(shapes, set), shapes.__class__.__name__
    assert all(isinstance(g, frozenset) for g in shapes), shapes
    assert all(isinstance(v, Symbol) for g in shapes for v in g), shapes
    assert isinstance(safe, set), safe
    assert all(isinstance(s, Symbol) for s in safe), safe

    # decompose and split
    atomic_tree = _expr_to_atomic(evalf(expr))  # decompose to atomic steps
    cst_tree, dyn_tree = _isolate_cst_dyn(atomic_tree, cst_args)  # isolate the cachable operations

    # optimise cst tree
    names = cst_tree[-1][1]
    cst_args, _, _ = _get_args(cst_tree[:-1])
    cst_alloc, cst_tree = _limit_realoc(cst_tree, _broadcast(cst_tree, shapes), safe=cst_args)
    names = OrderedDict(zip(names, cst_tree[-1][1]))
    subs, cst_tree = _rename(
        cst_tree,
        {
            s: Symbol(f"_cst_{i}")
            for i, s in enumerate(cst_tree[-1][1])
            if re.fullmatch(r"_\d+", str(s))
        },
        return_subs=True
    )
    names = dict(zip(names, cst_tree[-1][1]))
    cst_alloc = {subs.get(symb, symb): shape for symb, shape in cst_alloc.items()}

    # optimize dyn tree
    dyn_tree = _rename(dyn_tree, names, return_subs=False)
    dyn_alloc, dyn_tree = _limit_realoc(
        dyn_tree, _broadcast(cst_tree[:-1]+dyn_tree, shapes), safe=(safe | set(names.values()))
    )
    subs, dyn_tree = _rename(dyn_tree, {n: n for n in names.values()}, return_subs=True)
    dyn_alloc = {subs.get(symb, symb): shape for symb, shape in dyn_alloc.items()}

    # analyse parameters and safety
    dyn_args, _, dyn_alloc_symbs = _get_args(dyn_tree)
    dyn_alloc = {symb: shape for symb, shape in dyn_alloc.items() if symb in dyn_alloc_symbs}

    # combine all the informations
    return {
        "cst_args": cst_args,
        "cst_alloc": cst_alloc,
        "cst_tree": cst_tree,
        "dyn_args": dyn_args,
        "dyn_alloc": dyn_alloc,
        "dyn_tree": dyn_tree,
    }
