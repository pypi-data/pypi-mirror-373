from collections.abc import Callable
import warnings

import numpy as np
from scipy.optimize import curve_fit, OptimizeWarning
import sympy as sp
from uncertainties import ufloat
from uncertainties.core import Variable


def convert_sympy_formula_to_numpy_func(formula: str, scale: str = "linear"):
    """Convert a sympy formula string to a numerical function.

    Args:
        formula (str): The sympy formula string. Should only use functions available in numpy.
        scale (str): If 'linear' formula is computed as is. If 'log' the log of the formula is computed.

    Returns:
        Callable: A function that computes the input formula.
    """
    sympy_formula = sp.sympify(formula, evaluate=False)

    if scale == "log":
        sympy_formula = sp.expand_log(sp.log(sympy_formula), force=True)

    # discover symbols and reorder them
    free_symbols = sympy_formula.free_symbols

    # independent variables
    ind_symb = []
    # the fitting parameters
    params = []

    for s in free_symbols:
        if str(s).startswith("p_") and str(s)[2:].isdigit():
            params.append(str(s))
        else:
            ind_symb.append(str(s))

    params.sort(key=lambda x: int(str(x)[2:]))

    func = sp.lambdify(
        args=ind_symb + params, expr=sympy_formula, modules="numpy", dummify=False
    )

    return func


def fit_data(
    xs: list[float],
    ys: list[float],
    es: list[float],
    fit_ansatz: Callable,
    fit_param_bounds: tuple[list, list],
    fit_y_scale: str,
    SNR_threshold: float = 5,
    Abs_threshold: float = np.inf,
    verbose: bool = False,
) -> tuple[Variable, ...]:
    """Fit given data using the given ansatz.

    Uses scipy's curve_fit with method='trf'.

    Args:
        xs (list[float]): The independent variable data.
        ys (list[float]): The dependent variable data.
        es (list[float]): The uncertainity in the dependent variable.
        fit_ansatz (Callable): The fit function.
        fit_param_bounds (tuple[list, list]): The bounds for the fit parameters.
        fit_y_scale (str): Either 'linear' or 'log'. If 'log' then ys is scaled to log(ys) before fit.
        SNR_threshold (float, optional): The signal-to-noise threshold below which data is discarded. Defaults to 5.
        Abs_threshold (float, optional): The error rate above which the data is discarded. Defaults to infinity.
        verbose (bool, optional): Whether to print info. Defaults to False.

    Raises:
        ValueError: If xs, ys and es don't have the same length.
        ValueError: If at least two points not provided, or less than two points remain after filtering.

    Returns:
        tuple[Variable, ...]: The fit parameters as uncertainities Variable types. Use p.nominal_value and p.std_dev to
            access the stored values.
    """
    if len(xs) != len(ys) or len(xs) != len(es):
        raise ValueError("xs, ys and es don't have the same length.")
    if len(xs) < 2:
        raise ValueError("Fitting cannot work without at least two points.")

    # convert data into np array and sort
    xs, ys, es = (np.array(_) for _ in [xs, ys, es])
    inds = np.argsort(xs)
    xs, ys, es = (_[inds] for _ in [xs, ys, es])

    # Do SNR threshold filtering
    if SNR_threshold is not None:
        inds = np.where(ys / es > SNR_threshold)[0]
        if verbose:
            print(
                "Fit is ignoring (SNR-based): ",
                xs[np.where(ys / es <= SNR_threshold)[0]],
            )
        xs, ys, es = (_[inds] for _ in [xs, ys, es])

    # Do Abs threshold filtering
    if Abs_threshold is not None:
        inds = np.where(ys < Abs_threshold)[0]
        if verbose:
            print("Fit is ignoring (Abs-based): ", xs[np.where(ys >= Abs_threshold)[0]])

        xs, ys, es = (_[inds] for _ in [xs, ys, es])

    if len(xs) < 2:
        raise ValueError(
            "After filtering, less than two points remain. Fitting not possible."
        )

    if fit_y_scale == "linear":
        ys_scaled = ys
    elif fit_y_scale == "log":
        ys_scaled = np.log(ys)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            p_opt, p_cov = curve_fit(
                fit_ansatz,
                xs,
                ys_scaled,
                sigma=es / ys,
                bounds=fit_param_bounds,
                method="trf",
            )

            if len(w):
                raise RuntimeError

        except RuntimeError:
            raise RuntimeError("Covariance of the parameters can not be estimated.")

    mean = np.array(p_opt)
    std = np.sqrt(np.diagonal(p_cov))
    return tuple(ufloat(m, s) for m, s in zip(mean, std))
