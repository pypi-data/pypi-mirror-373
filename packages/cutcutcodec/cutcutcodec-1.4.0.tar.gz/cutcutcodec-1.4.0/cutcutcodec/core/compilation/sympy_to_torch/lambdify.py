#!/usr/bin/env python3

"""Convert a sympy expression into a torch function.

It is the main entry point.
The preprocessing is delegated to the
``cutcutcodec.core.compilation.sympy_to_torch.preprocess`` module.
The compilation is delegated to the
``cutcutcodec.core.compilation.sympy_to_torch.printer`` module.
"""

import hashlib
import importlib
import logging
import numbers
import pathlib
import re
import subprocess
import sys
import tempfile
import typing
import uuid

from sympy.core.basic import Basic
from sympy.core.containers import Tuple
from sympy.core.symbol import Symbol
from sympy.printing import latex
import torch

from cutcutcodec.core.compilation.sympy_to_torch.dynamic import _dyn_eval
from cutcutcodec.core.compilation.sympy_to_torch.preprocess import evalf, preprocess
from cutcutcodec.core.compilation.sympy_to_torch.printer import _printer
from cutcutcodec.core.exceptions import CompilationError
from cutcutcodec.core.opti.cache.singleton import MetaSingleton
from cutcutcodec.utils import get_compilation_rules


def _cast_lambdify_c(
    func: callable, input_args: dict[str, numbers.Real | torch.Tensor]
) -> torch.Tensor | tuple[torch.Tensor]:
    """Cast the tensors into flat c continuous numpy array and cast back before return.

    Parameters
    ----------
    func : callable
        The C func from ``cutcutcodec.core.compilation.sympy_to_torch.lamdbify._lambdify_c``.
    input_args : dict[str, torch.Tensor]
        The named args to give to the function.

    Returns
    -------
    tuple
        The ouput tensors of func, homogeneous with the input tensors.

    Raises
    ------
    cutcutcodec.core.exceptions.CompilationError
        If func raise RuntimeError or TypeError or
        if the arguments are not conformed.

    Examples
    --------
    >>> import numpy as np
    >>> import torch
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _cast_lambdify_c
    >>> def func(tensor):
    ...     print("c_contiguous:", tensor.flags["C_CONTIGUOUS"])
    ...     print("shape:", tensor.shape)
    ...     return tensor
    ...
    >>> arg = torch.full((3, 4), .0j).real
    >>> arg.is_contiguous()
    False
    >>> _cast_lambdify_c(func, {"x": arg})
    c_contiguous: True
    shape: (12,)
    tensor([[0., 0., 0., 0.],
            [0., 0., 0., 0.],
            [0., 0., 0., 0.]])
    >>>
    """
    # basic verification, raise exception as soon as possible
    if any(a.requires_grad for a in input_args.values() if isinstance(a, torch.Tensor)):
        raise CompilationError("gradient is not supported by this compiled C function")
    if any(a.device.type != "cpu" for a in input_args.values() if isinstance(a, torch.Tensor)):
        raise CompilationError("other device than cpu is not supproted by this compiled C function")
    if not input_args:
        raise CompilationError("the compiled C function has to take at least one argument")

    # sorted args
    args = [input_args[k] for k in sorted(input_args)]

    # converts types if necessary so that all arguments have the same dtype.
    all_dtypes = {a.dtype for a in args if isinstance(a, torch.Tensor)}
    all_dtypes |= {
        torch.float32 if isinstance(a, numbers.Real) else torch.complex64
        for a in args if not isinstance(a, torch.Tensor)
    }
    dtype = max(all_dtypes, key=lambda d: (d.is_complex, d.itemsize))
    if not (dtype.is_complex or dtype.is_floating_point):  # if int
        dtype = torch.float32
    args = [
        a.to(dtype, copy=False) if isinstance(a, torch.Tensor) else torch.tensor(a, dtype=dtype)
        for a in args
    ]

    # broadcast shape
    try:
        args = torch.broadcast_tensors(*args)
    except RuntimeError as err:
        raise CompilationError("the input tensor shapes are incompatible") from err
    shape = args[0].shape

    # cast into numpy
    args = [a.numpy(force=True).ravel() for a in args]

    # eval function
    try:
        out = func(*args)
    except (RuntimeError, TypeError) as err:
        raise CompilationError(f"failed to excecute the c func with {input_args}") from err

    # cast into torch, dtype is concervative
    if isinstance(out, tuple):
        return tuple(torch.from_numpy(o).reshape(shape) for o in out)
    return torch.from_numpy(out).reshape(shape)


def _lambdify_c(code: str) -> callable:
    """Compile the C source code and import the func.

    Parameters
    ----------
    code : str
        The C source code, output of the
        ``cutcutcodec.core.compilation.sympy_to_torch.printer._printer`` function.

    Returns
    -------
    func : callable
        The python callable compiled function, corresponding to the given c code.

    Raises
    ------
    cutcutcodec.core.exceptions.CompilationError
        If gcc failed to compile the source code.

    Examples
    --------
    >>> from pprint import pprint
    >>> from sympy.abc import c, x
    >>> from sympy import Number, Tuple, sin, symbols
    >>> import numpy as np
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
    >>> from cutcutcodec.core.compilation.sympy_to_torch.printer import _printer
    >>> _, _0, _1, _2, _3, _4, _5 = symbols("_ _:6")
    >>> tree = [(_0, c**(-2)), (_1, 1/x), (_2, _0*_1), (_3, Number(0)), (_1, sin(x)), (_1, sin(_1)),
    ...         (_1, _1 + 1), (_0, c), (_4, x), (_5, _2), (_, Tuple(_3, _0, c, _4, x, _2, _5, _1))]
    >>> alloc = {_0: {c}, _1: {c}, _2: {c}, _3: {c}, _4: {c}, _5: {c}}
    >>> args = {c, x}
    >>> code = _printer(tree, alloc, args)
    >>> func = _lambdify_c(code)
    >>> pprint(func(np.array([-1.0, 1.0]), np.array([-2.0, 2.0])))
    (array([0., 0.]),
     array([-1.,  1.]),
     array([-1.,  1.]),
     array([-2.,  2.]),
     array([-2.,  2.]),
     array([-0.5,  0.5]),
     array([-0.5,  0.5]),
     array([0.21092766, 1.78907234]))
    >>>
    """
    name = f"lambdify_{uuid.uuid4().hex}"
    filename = pathlib.Path(tempfile.gettempdir()) / f"{name}.so"

    # compilation
    comp_rules = get_compilation_rules()
    gcc_insructions = [
        "gcc",
        "-o", str(filename),  # output file
        "-xc", "-",  # c language, no link, from stdin
        "-Wall",  # display all warnings
        "-pipe",  # use RAM rather than tempfile
        "-fPIC",  # emit position-independent code
        "-shared",  # produce a shared object which can then be linked with other objects
        f"-L{sys.base_prefix}/lib",
        f"-I{sys.base_prefix}/include/python{sys.version_info.major}.{sys.version_info.minor}",
        *(f"-D{mac_in}={mac_out}" for mac_in, mac_out in comp_rules["define_macros"]),
        *(f"-I{inc}" for inc in comp_rules["include_dirs"]),  # extra include
        *comp_rules["extra_compile_args"],
    ]
    try:
        subprocess.run(
            gcc_insructions, input=code.encode("utf-8"), check=True, capture_output=False
        )
    except subprocess.CalledProcessError as err:
        raise CompilationError("failed to compile the C code with gcc", code) from err

    # import
    spec = importlib.util.spec_from_file_location("lambdify", filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # clean
    filename.unlink()

    return module.lambdify


class Lambdify(metaclass=MetaSingleton):
    r"""Convert a sympy expression into an evaluable torch function.

    Attributes
    ----------
    args : list[str]
        The ordered names of the input arguments of this function (readonly).

    Examples
    --------
    >>> from sympy import I, cos, exp, im, re, sqrt, sin, symbols
    >>> from torch import linspace, tensor
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import Lambdify
    >>>
    >>> # case of Faucault pendulum
    >>> # angular earth speed, latitude, gravity, pendulum length, time
    >>> omega, theta, g, l, t = symbols("omega theta g l t", real=True)
    >>> z0, v0 = symbols("z_0 v_0", complex=True)  # initial position and speed
    >>> w0 = sqrt(sqrt(g/l)**2 + omega**2*sin(theta)**2)
    >>> z = exp(-I*omega*sin(theta*t)) * (
    ...     z0*(cos(w0*t) + I*(omega*sin(theta)/w0)*sin(w0*t)) + (v0/w0)*sin(w0*t)
    ... )
    >>> func = Lambdify(
    ...     [z, z.diff(t)], cst_args={omega, theta, g, l}, shapes={(omega, theta, g, l), (z0, v0)}
    ... )
    >>> print(func)
    \begin{aligned}
    \textbf{def}~f\left(g, l, omega, t, theta, v_0, z_0\right): \\
    \quad x_{cst_3} \leftarrow \sin{\left(\theta \right)} \\
    \quad x_{cst_0} \leftarrow \frac{1}{l} \\
    \quad x_{cst_0} \leftarrow g x_{cst_0} \\
    \quad x_{cst_1} \leftarrow x_{cst_3}^{2} \\
    \quad x_{cst_2} \leftarrow \omega^{2} \\
    \quad x_{cst_1} \leftarrow x_{cst_1} x_{cst_2} \\
    \quad x_{cst_0} \leftarrow x_{cst_0} + x_{cst_1} \\
    \quad x_{cst_0} \leftarrow x_{cst_0}^{0.5} \\
    \quad x_{cst_1} \leftarrow \frac{1}{x_{cst_0}} \\
    \quad x_{cst_2} \leftarrow i \omega \\
    \quad x_{cst_3} \leftarrow x_{cst_2} x_{cst_3} \\
    \quad x_0 \leftarrow t x_{cst_0} \\
    \quad x_1 \leftarrow \sin{\left(x_{0} \right)} \\
    \quad x_2 \leftarrow x_{1} x_{cst_1} \\
    \quad x_0 \leftarrow \cos{\left(x_{0} \right)} \\
    \quad x_3 \leftarrow t \theta \\
    \quad x_4 \leftarrow \sin{\left(x_{3} \right)} \\
    \quad x_4 \leftarrow - x_{4} x_{cst_2} \\
    \quad x_4 \leftarrow e^{x_{4}} \\
    \quad x_5 \leftarrow v_{0} x_{2} \\
    \quad x_2 \leftarrow x_{2} x_{cst_3} \\
    \quad x_2 \leftarrow x_{0} + x_{2} \\
    \quad x_6 \leftarrow x_{2} z_{0} \\
    \quad x_6 \leftarrow x_{5} + x_{6} \\
    \quad x_6 \leftarrow x_{4} x_{6} \\
    \quad x_5 \leftarrow v_{0} x_{0} \\
    \quad x_0 \leftarrow x_{0} x_{cst_3} \\
    \quad x_1 \leftarrow - x_{1} x_{cst_0} \\
    \quad x_0 \leftarrow x_{0} + x_{1} \\
    \quad x_7 \leftarrow x_{0} z_{0} \\
    \quad x_7 \leftarrow x_{5} + x_{7} \\
    \quad x_7 \leftarrow x_{4} x_{7} \\
    \quad x_0 \leftarrow \cos{\left(x_{3} \right)} \\
    \quad x_5 \leftarrow - \theta x_{0} x_{6} x_{cst_2} \\
    \quad x_7 \leftarrow x_{5} + x_{7} \\
    \quad \textbf{return}~\left[ x_{6}, \  x_{7}\right]
    \end{aligned}
    >>>
    >>> # parameters of the pantheon pendulum in Paris
    >>> position, speed = func(
    ...     linspace(0, (23*3600+56*60+4)/4, 1_000_000),  # a tour in 23h 56min 4s
    ...     g=tensor(9.81), l=tensor(67.0), omega=tensor(7.292115e-5), theta=tensor(0.8524362),
    ...     v_0=tensor(1+0j), z_0=tensor(0j),
    ... )
    >>> print(position)
    tensor([ 0.0000+0.0000e+00j,  0.0215-2.8842e-08j,  0.0431-1.1534e-07j,
             ..., -2.1698+4.9477e-05j, -2.1583+4.6581e-05j,
            -2.1453+4.3373e-05j])
    >>> print(speed)
    tensor([1.0000+0.0000e+00j, 1.0000-2.6776e-06j, 0.9999-5.3531e-06j,
             ..., 0.5574-1.4082e-04j, 0.5639-1.4032e-04j,
            0.5711-1.3967e-04j])
    >>>
    """

    def __init__(self, expr: Basic, **kwargs):
        """Initialise and create the class.

        Parameters
        ----------
        expr : sympy.core.basic.Basic
            The sympy expression of the function.
        cst_args : typing.Iterable[sympy.core.symbol.Symbol], optional
            Arguments that change infrequently enough to be cached.
            The subexpressions computed from this parameters will be cached as well.
            If the parameters change frequently, don't specify them in ``cst_args``,
            This will slow down the function.
        shapes : set[frozenset[sympy.core.symbol.Symbol]], optional
            If some parameters have the same shape, it is possible to give this information
            in order to find a more optimal solution for limited the allocations.
            It variable represents the set of all tensor subsets with the same shapes.
            For example, {frozenset({a, b, c}), frozenset({x, y})} means that
            a, b, and c are the same shape, and x and y as well.
        compile : boolean, default=True
            The default behavior is to translate the expression into C,
            compile it with gcc, import the compiled version and then use this function.
            If any of these steps fail, the calculation is performed dynamically via pytorch only.
            If False, the function is evaluated dynamically only. No compilation is performed.
            It's faster to instantiate the first time but it's generally slower to evaluate.
        safe : boolean or set[sympy.core.symbol.Symbol], default=True
            If True, the default behavior, then the tensors provided as input are not modified.
            This helps avoid unpleasant surprises but it is slower in certain cases.
            If False, no preventive copy is made.
            It is the fastest but the tensors provided as input can be modified in place.
            It is possible to be more precise by selecting only the variables to preserve,
            in this case, provide all the variables to be preserved.
        """
        # verifications
        assert set(kwargs).issubset({"cst_args", "shapes", "compile", "safe"}), kwargs
        if isinstance(expr, (list, tuple, set, frozenset)):
            assert all(isinstance(e, Basic) for e in expr), expr
            self._cast = type(expr)
            expr = Tuple(*expr)
        else:
            assert isinstance(expr, Basic), expr.__class__.__name__
            self._cast = None
        assert not any(str(a).startswith("_") for a in expr.free_symbols), (
            "in order to avoid a conflict with the internal autogereted vars, "
            f"the symbols {expr.free_symbols} must not start with '_'"
        )
        if kwargs.get("cst_args", None) is None:
            kwargs["cst_args"] = set()
        else:
            assert isinstance(kwargs["cst_args"], typing.Iterable), \
                kwargs["cst_args"].__class__.__name__
            kwargs["cst_args"] = set(kwargs["cst_args"])
            assert all(isinstance(a, Symbol) for a in kwargs["cst_args"]), kwargs["cst_args"]
            assert kwargs["cst_args"].issubset(expr.free_symbols), (
                expr.free_symbols, kwargs["cst_args"]
            )
        if kwargs.get("shapes", None) is None:
            kwargs["shapes"] = set()
        else:
            assert isinstance(kwargs["shapes"], typing.Iterable), kwargs["shapes"]
            kwargs["shapes"] = list(kwargs["shapes"])
            assert all(isinstance(s, typing.Iterable) for s in kwargs["shapes"]), kwargs["shapes"]
            kwargs["shapes"] = {frozenset(s) for s in kwargs["shapes"]}
            assert all(isinstance(v, Symbol) for s in kwargs["shapes"] for v in s), kwargs["shapes"]
            assert all(s.issubset(expr.free_symbols) for s in kwargs["shapes"]), (
                expr.free_symbols, kwargs["shapes"]
            )
        if "compile" in kwargs:
            assert isinstance(kwargs["compile"], bool), kwargs["compile"].__class__.__name__
        if kwargs.get("safe", None) in {None, True}:
            kwargs["safe"] = expr.free_symbols
        elif kwargs["safe"] is False:
            kwargs["safe"] = set()
        else:
            assert isinstance(kwargs["safe"], typing.Iterable), kwargs["safe"]
            kwargs["safe"] = set(kwargs["safe"])
            assert all(isinstance(s, Symbol) for s in kwargs["safe"]), kwargs["safe"]
            assert kwargs["safe"].issubset(expr.free_symbols), (expr.free_symbols, kwargs["safe"])

        # internal attributes
        self._tree = {"expr": expr, "shapes": kwargs["shapes"]}
        self._cst_cache = None

        # preprocessing
        self._tree |= preprocess(
            evalf(expr), cst_args=kwargs["cst_args"], shapes=kwargs["shapes"], safe=kwargs["safe"]
        )

        # args
        self._tree["args_str"] = set(
            map(
                str,
                (
                    self._tree["cst_args"]
                    | {a for a in self._tree["dyn_args"] if not str(a).startswith("_")}
                )
            )
        )

        # kernel compiled function
        self._tree["dyn_code"] = None
        self._tree["dyn_func"] = None
        if (
            kwargs.get("compile", True)
            and (
                len(self._tree["dyn_tree"]) != 1
                or self._tree["dyn_tree"][0][0] != self._tree["dyn_tree"][0][1]
            )
            and self._tree["dyn_args"]
        ):  # if compilation is required
            try:
                self._tree["dyn_code"] = _printer(
                    self._tree["dyn_tree"], self._tree["dyn_alloc"], self._tree["dyn_args"]
                )
                self._tree["dyn_func"] = _lambdify_c(self._tree["dyn_code"])
            except CompilationError as err:
                logging.warning("failed to compile in C because %s", err)

    def __str__(self, name: str = "f") -> str:
        """Return a pseudo-code of the function as a LaTeX aligned block."""
        assert isinstance(name, str), type(name).__name__

        lines = []

        def escape(symb: str) -> str:
            """Adapt symbol name to regex."""
            symb = str(symb)
            if symb.startswith("_"):
                symb = f"x{symb}"  # "_..." give "x_..."
            if symb.endswith("_"):
                symb = f"{symb[:-1]}\\_"  # ""..._" give r"...\x"
            return re.sub(r'_(\w{2,})', r'_{\1}', symb)  # "_xx" or "_abc123" give "_{xx}", not "_x"

        # function signature
        lines.append(rf"\textbf{{def}}~{name}\left({', '.join(map(str, self.args))}\right): \\")

        # constants section
        if self._tree["cst_tree"][-1][1]:
            for symb, expr in self._tree["cst_tree"][:-1]:
                expr = expr.subs({s: Symbol(escape(s)) for s in expr.free_symbols})
                lines.append(rf"\quad {escape(symb)} \leftarrow {latex(expr)} \\")

        for symb, expr in (
            self._tree["dyn_tree"] if self._cast is None else self._tree["dyn_tree"][:-1]
        ):
            expr = expr.subs({s: Symbol(escape(s)) for s in expr.free_symbols})
            lines.append(rf"\quad {escape(symb)} \leftarrow {latex(expr)} \\")

        # return
        if self._cast is None:
            ret = self._tree["dyn_tree"][-1][0]
            lines.append(rf"\quad \textbf{{return}}~{escape(ret)}")
        else:
            ret_expr = self._tree["dyn_tree"][-1][1]
            ret_expr = ret_expr.subs({s: Symbol(escape(s)) for s in ret_expr.free_symbols})
            ret_expr = self._cast(ret_expr)
            lines.append(rf"\quad \textbf{{return}}~{latex(ret_expr)}")

        return r"\begin{aligned}" + "\n" + "\n".join(lines) + "\n" + r"\end{aligned}"

    def __call__(
        self, *args: torch.Tensor, **kwargs: dict[str, torch.Tensor]
    ) -> torch.Tensor | typing.Iterable[torch.Tensor]:
        """Evaluate the expression and return the numerical result.

        Parameters
        ----------
        *args : tuple
            The numerical value of the symbol in the expression.
            You can name the argument using ``**kwargs``.
        **kwargs : dict
            To each variable name present in the expression, associate the numerical value.
            You don't have to name the argument, you can use ``*arg``.

        Returns
        -------
        result
            The numerical value of the expression evaluated with the given input parameters.
        """
        # get all requiered args and named it
        input_args = {}
        for arg_name, value in kwargs.items():
            if arg_name in self._tree["args_str"]:
                input_args[arg_name] = value
            else:
                logging.warning("the argument %s is provided but not used", arg_name)
        left = self._tree["args_str"] - input_args.keys()
        if len(args) > len(left):
            logging.warning("the %d last arguments are ignored", len(args)-len(left))
        for i, arg_name in enumerate(sorted(left)):
            try:
                input_args[arg_name] = args[i]
            except IndexError as err:
                raise ValueError(f"the argument {arg_name} is missing") from err

        # verification type
        assert all(isinstance(a, torch.Tensor) for a in input_args.values()), \
            f"the arguments can only be a torch tensor, given args are {input_args}"

        # compute the expression
        out = self.forward(**input_args)

        # number/tensor/iterable cast
        if self._cast is None:
            if isinstance(out, numbers.Real):
                return torch.tensor(out, dtype=torch.float64)
            if isinstance(out, numbers.Complex):
                return torch.tensor(out, dtype=torch.complex128)
            return out
        return self._cast(
            o
            if isinstance(o, torch.Tensor) else
            (
                torch.tensor(o, dtype=torch.float64)
                if isinstance(o, numbers.Real) else
                torch.tensor(o, dtype=torch.complex128)
            )
            for o in out
        )

    def _cst_tree_func(self, input_args: numbers.Number | torch.Tensor) -> tuple[torch.Tensor]:
        """Dynamic evaluation of the constant tree.

        This function is cached once.

        Parameters
        ----------
        input_args : dict[str, torch.Tensor]
            For each symbol name present in the original equation, associate the numerical tensor.

        Returns
        -------
        tuple[torch.Tensor]
            The differents usefull constants for the compiled main function.
        """
        # case no args for optimisation
        if not self._tree["cst_args"]:
            if self._cst_cache is None:
                buff = {}
                out = ()
                for new_var, expr in self._tree["cst_tree"]:
                    out = _dyn_eval(expr, buff, str(new_var))
                self._cst_cache = out
            return self._cst_cache

        # compute args hash
        hash_compactor = hashlib.md5(usedforsecurity=False)
        for arg in sorted(map(str, self._tree["cst_args"])):
            hash_compactor.update(str(input_args[arg].dtype).encode())
            hash_compactor.update(str(input_args[arg].shape).encode())
            hash_compactor.update(input_args[arg].numpy(force=True))
        args_hash = hash_compactor.digest()

        # compute the constant part of the expression if it is not already done
        if self._cst_cache is None or self._cst_cache[0] != args_hash:
            # dynamic evaluation
            input_args = input_args.copy()  # to prevent changing hyperparameter in place
            out = ()
            for new_var, expr in self._tree["cst_tree"]:
                out = _dyn_eval(expr, input_args, str(new_var))
            self._cst_cache = (args_hash, out)

        # restitution
        return self._cst_cache[1]

    def _dyn_tree_func(
        self, dyn_args: numbers.Number | torch.Tensor
    ) -> numbers.Number | torch.Tensor | tuple[torch.Tensor]:
        """Evaluate the dynamic tree.

        This function is not cached

        Parameters
        ----------
        dyn_args : dict[str, torch.Tensor]
            For each symbol name present in the dynamic tree as argument,
            associate the numerical tensor. Only the usefull arguments had to be present, not more.

        Returns
        -------
        tuple[torch.Tensor]
            The result of the dynamic tree.
        """
        out = None
        if self._tree["dyn_func"] is not None:
            try:
                out = _cast_lambdify_c(self._tree["dyn_func"], dyn_args)
            except CompilationError as err:
                logging.warning(
                    "failed to eval the C code with the args %s because %s", dyn_args, err
                )
                for symb, expr in self._tree["dyn_tree"]:  # pure torch evaluation
                    out = _dyn_eval(expr, dyn_args, str(symb))
        else:
            for symb, expr in self._tree["dyn_tree"]:  # pure torch evaluation
                out = _dyn_eval(expr, dyn_args, str(symb))
        return out

    @property
    def args(self) -> list[str]:
        """Return the ordered names of the input arguments of this function."""
        return sorted(self._tree["args_str"])

    def forward(
        self, **input_args: dict[str, numbers.Number | torch.Tensor]
    ) -> numbers.Number | torch.Tensor | tuple[torch.Tensor]:
        """Fast evaluation of the expression.

        No casts and verifications are performed here.
        For more flexible and safer use, please use the
        ``cutcutcodec.core.compilation.sympy_to_torch.lambdify.Lambify.__call__`` function.

        Parameters
        ----------
        **input_args : dict[str]
            To each variable name present in the expression, associate the numerical value.
            All arguments have to be provided.

        Returns
        -------
        result
            The direct result of the underground function with compute the expression.
        """
        cst_out = self._cst_tree_func(input_args)
        cst_args = dict(zip(map(str, self._tree["cst_tree"][-1][1]), cst_out))
        dyn_args = input_args | cst_args  # order cst_args takes priority
        dyn_args = {str(s): dyn_args[str(s)] for s in self._tree["dyn_args"]}
        return self._dyn_tree_func(dyn_args)
