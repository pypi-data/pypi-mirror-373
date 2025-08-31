# The MIT License (MIT)
#
# Copyright (c) 2025 Department of Plant and Environmental Science,
# Weizmann Institute of Science.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from typing import (
    Callable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
    Dict,
    Iterable,
)

import cvxpy
import more_itertools
import matplotlib.pyplot as plt  # a standard plotting package for python
import networkx as nx  # package for plotting networks
import numpy as np  # common mathematical functions
import sympy  # SymPy is a Python library for symbolic mathematics
from pynverse import inversefunc
from scipy.linalg import expm  # Compute the matrix exponential of an array
from scipy.optimize import curve_fit, basinhopping, OptimizeResult, Bounds  # non-linear least squares fit a function to data
import pandas as pd
from copy import deepcopy


class CompartmentalModelFittingResults(NamedTuple):
    """Stores the fitting results for Compartmental Models.

    Fields:
        cm:  SymbolicCompartmentalModel
            a CM with the optimal parameters assigned (i.e. w/o free parameters)
        popt: ndarray
            the best fitting parameters
        pcov: ndarray
            the covariance matrix of the best fitting parameters
        rss: float
            Resudial Sum of Squares
        n_params: int
            number of free parameters (variables)
        n_samples: int
            the number of data samples
        delta_aic: float
            the Aikaike information criterion (ΔAIC)
    """

    cm: "SymbolicCompartmentalModel"
    popt: np.ndarray
    pcov: np.ndarray
    rss: float
    n_params: int
    n_samples: int
    delta_aic: float

    @property
    def is_valid(self) -> bool:
        """Test whether the fitted CM is valid (row sums are negative)."""
        return self.cm.is_valid(raise_exception=False)

    @property
    def is_mass_balanced(self) -> bool:
        """Test whether the fitted CM is mass balanced (considering the growth rate)."""
        return self.cm.is_mass_balanced(raise_exception=False)

    @property
    def is_M_mass_balanced(self) -> bool:
        """Test whether the M-matrix of the fitted CM can be mass balanced (
        considering the growth rate)."""
        return self.cm.is_M_mass_balanced(raise_exception=False)

    @property
    def has_delayed_input(self) -> bool:
        """Test whether the fitted CM has a delayed input."""
        return self.cm.has_delayed_input(raise_exception=False)


class PoolWeights(object):
    """Stores pool weights for Compartmental Models."""

    def __init__(self, n_states: int):
        """Initialize a pool weight object.

        Parameters
        ----------
            n_states: int
                number of states

        """
        self.n_states = n_states
        self._weights = sympy.zeros(rows=n_states, cols=1)
        self._weights[-1] = 1.0

    def __deepcopy__(self, memo: dict) -> "PoolWeights":
        """Make a copy of a PoolWeights object."""
        other = PoolWeights(self.n_states)
        other._weights = deepcopy(self._weights, memo)
        return other

    def clone(self) -> "PoolWeights":
        """Make a copy of a PoolWeights object."""
        return deepcopy(self)

    def check_state_index(self, i: int) -> None:
        if not isinstance(i, int):
            raise TypeError("Indices must be integers.")
        if not 0 <= i < self.n_states:
            raise IndexError(
                f"State index ({i}) out of range (n_states = {self.n_states})."
            )

    def __setitem__(self, i: int, value: Union[float, sympy.Expr]) -> None:
        """Set the weight of a single observed pool.

        Parameters
        ----------
            i: int
                index of the observed pool
            value: float
                the value to assign to it

        """
        if not isinstance(i, int):
            raise TypeError("Indices must be integers.")
        if isinstance(value, (int, float)):
            if value < 0:
                raise ValueError("All pool weights must be positive numbers")
        elif not isinstance(value, sympy.Expr):
            raise TypeError("value must be int, float, or a sympy Expr.")
        self.check_state_index(i)
        self._weights[i, 0] = value

    def __getitem__(self, i: int) -> Union[float, sympy.Expr]:
        """Get the weight of a single pool.

        Parameters
        ----------
            i: int
                index of the observed pool

        Returns
        -------
            value: float or sympy.Expr
                the value of the observed pool

        """
        self.check_state_index(i)
        return self._weights[i, 0]

    def subs(self, d: dict) -> None:
        """Apply the sympy.subs() function on the weights.

        Parameters
        ----------
            d: dict
                A dictionary mapping sympy symbols to values
        """
        self._weights = self._weights.subs(d)

    def as_numpy(self, d: Optional[dict] = None) -> np.ndarray:
        """Return the weights as a numpy vector.

        Parameters
        ----------
            d: dict
                A dictionary mapping sympy symbols to values

        Returns
        -------
            w: ndarray
                a numpy vector of the observed weights (normalized to 1)

        """
        if d is None:
            w = self._weights
        else:
            w = self._weights.subs(d)
        return sympy.matrix2numpy(w / sum(w), dtype=float)

    def as_sympy(self) -> sympy.Expr:
        """Return the weights as a sympy.Expr.

        Returns
        -------
            w: sympy.Expr
                a sympy expression of the observed weights (normalized to 1)

        """
        return self._weights / sum(self._weights)

class ContributedTurnovers(object):
    """Stores the contributed turnovers (M-matrix) for Compartmental Models."""

    def __init__(self, n_states: int):
        """Initialize a pool weight object.

        Parameters
        ----------
            n_states: int
                number of states

        """
        self.n_states = n_states
        self._turnovers = sympy.zeros(rows=n_states, cols=n_states)

    def __deepcopy__(self, memo: dict) -> "ContributedTurnovers":
        """Make a copy of a ContributedTurnovers object."""
        other = ContributedTurnovers(self.n_states)
        other._turnovers = deepcopy(self._turnovers, memo)
        return other

    def clone(self) -> "ContributedTurnovers":
        """Make a copy of a ContributedTurnovers object."""
        return deepcopy(self)

    def check_state_index(self, i: int) -> None:
        if not 0 <= i < self.n_states:
            raise IndexError(
                f"State index ({i}) out of range (n_states = {self.n_states})."
            )

    def __setitem__(self, key: Tuple[int, int], value: Union[float, sympy.Expr]) -> None:
        """Set the contributed turnover of one pool to another.

        Parameters
        ----------
            key: Tuple[int, int]
                a tuple containing two indices of the pools (from, to)

            value: Union[float, sympy.Expr]
                the contributed turnover

        """
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError("Key must be a tuple of two integers (row, col).")
        row, col = key
        if not isinstance(row, int) or not isinstance(col, int):
            raise TypeError("Row and column indices must be integers.")
        self.check_state_index(row)
        self.check_state_index(col)

        if isinstance(value, (int, float)):
            if row == col:
                assert value <= 0, "M-matrix diagonal values must be non-positive"
            else:
                assert value >= 0, "M-matrix diagonal values must be non-negative"
        elif not isinstance(value, sympy.Expr):
            raise TypeError("value must be int, float, or a sympy Expr.")

        self._turnovers[row, col] = value

    def __getitem__(self, key: Tuple[int, int]) -> Union[float, sympy.Expr]:
        """Get the contributed turnover of one pool to another.

        Parameters
        ----------
            key: Tuple[int, int]
                a tuple containing two indices of the pools (from, to)

        Returns
        -------
            turnover: Union[float, sympy.Expr]
                the contributed turnover

        """
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError("Key must be a tuple of two integers (row, col).")
        row, col = key
        if not isinstance(row, int) or not isinstance(col, int):
            raise TypeError("Row and column indices must be integers.")
        self.check_state_index(row)
        self.check_state_index(col)
        return self._turnovers[row, col]

    def subs(self, d: dict) -> None:
        """Apply sympy.subs() function on the contributed turnovers.

        Parameters
        ----------
            d: dict
                A dictionary mapping sympy symbols to values

        """
        self._turnovers = self._turnovers.subs(d)

    def as_numpy(self, d: Optional[dict] = None) -> np.ndarray:
        """Return the contributed turnovers as a numpy vector.

        Parameters
        ----------
            d: dict
                A dictionary mapping sympy symbols to values

        Returns
        -------
            M: ndarray
                a numpy matrix of the contributed turnovers

        """
        M = self._turnovers if d is None else self._turnovers.subs(d)
        return sympy.matrix2numpy(M, dtype=float)

    def as_sympy(self) -> sympy.Matrix:
        """Return the contributed turnovers as a sympy matrix.

        Returns
        -------
            M: ndarray
                a sumpy matrix of the contributed turnovers

        """
        return self._turnovers

class SymbolicCompartmentalModel(object):
    """Simulates physical dynamic systems using a compartmental model."""

    def __init__(self, n_states: int, n_params: int = 0):
        """Initialize a symbolic compartmental model."""
        self.n_states = n_states
        self.growth_rate = 0.0
        self._time = sympy.Symbol("t", positive=True, is_re=True)

        # 1-vector for labelling computation. See Appendix eq.(7)
        self._ones = sympy.Matrix(np.ones(self.n_states))

        self._params = [sympy.Symbol(f"p_{i}") for i in range(n_params)]
        self._p0 = np.ones(self.n_params) * 0.5
        self._lbs = np.zeros(self.n_params, dtype=float)
        self._ubs = np.ones(self.n_params, dtype=float)

        self._contributed_turnover_matrix = ContributedTurnovers(n_states)

        # observed pools, fractional distribution -
        # by default, the last pool is the only observed one
        self._observed_pool_weights = PoolWeights(self.n_states)

    @property
    def n_params(self) -> int:
        """Get the number of parameters."""
        return len(self._params)

    def add_parameter(
        self,
        symbol: str = None,
        lb: float = 0.0,
        ub: float = 1.0
    ) -> sympy.Symbol:
        """Add a new parameter to the model.

        Parameters
        ---------
            symbol: str
                The name of the new parameter.
            lb: float
                The lower bound (default: 0.0)
            ub: float
                The upper bound (default: 1.0)

        Return
        ------
            new_param: sympy.Symbol
                The new parameter object.

        """
        if symbol is None:
            symbol = f"p_{self.n_params}"
        new_param = sympy.Symbol(symbol)
        self._params.append(new_param)
        self._p0 = np.array(self._p0.tolist() + [(lb + ub)/2.0])
        self._lbs = np.array(self._lbs.tolist() + [lb])
        self._ubs = np.array(self._ubs.tolist() + [ub])
        return new_param

    def remove_all_parameters(self) -> None:
        """Remove all free parameters from the model."""
        self._params = []
        self._p0 = np.ones(0) * 0.5
        self._lbs = np.zeros(0, dtype=float)
        self._ubs = np.ones(0, dtype=float)

    def __deepcopy__(self, memo: dict) -> "SymbolicCompartmentalModel":
        other = SymbolicCompartmentalModel(self.n_states, self.n_params)
        other.growth_rate = self.growth_rate
        other._p0 = deepcopy(self._p0)
        other._lbs = deepcopy(self._lbs)
        other._ubs = deepcopy(self._ubs)
        other._contributed_turnover_matrix = self._contributed_turnover_matrix.clone()
        other._observed_pool_weights = self._observed_pool_weights.clone()
        return other

    def clone(self) -> "SymbolicCompartmentalModel":
        """Return a copy of the compartmental model."""
        return deepcopy(self)

    def parameterize(self, x: Iterable[float]) -> "SymbolicCompartmentalModel":
        """Return a new compartmental model with set parameters.

        Parameters
        ---------
            x: Iterable[float]
                a list of the parameter values to use

        Returns
        -------
            param_model: SymbolicCompartmentalModel
                a symbolic compartmental model where the parameter
                are replaced with their given values from `x`
        """
        other = self.clone()
        params_dict = self._get_params_dict(x)
        other._observed_pool_weights.subs(params_dict)
        other._contributed_turnover_matrix.subs(params_dict)
        other.remove_all_parameters()
        other._params = []
        return other

    @property
    def growth_rate(self) -> float:
        """Return the growth rate of the compartmental model."""
        return self._growth_rate

    @growth_rate.setter
    def growth_rate(self, mu: float) -> None:
        """Set the growth rate of the compartmental model."""
        if mu < 0:
            raise ValueError("growth rate cannot be a negative number")
        self._growth_rate = mu

    def check_state_index(self, i: int) -> None:
        if not 0 <= i < self.n_states:
            raise IndexError(
                f"State index ({i}) out of range (n_states = {self.n_states})."
            )

    def check_param_index(self, i: int) -> None:
        if not 0 <= i < self.n_params:
            raise IndexError(
                f"Parameter index ({i}) out of range (n_params = {self.n_params})."
            )

    def set_observed_pool_weight(self, i: int, value: Union[float, sympy.Expr]) -> None:
        """Set the weight of a single observed pool."""
        self.check_state_index(i)
        self._observed_pool_weights[i] = value

    @property
    def observed_pool_weights(self) -> "PoolWeights":
        """Get all the observed pool weights."""
        return self._observed_pool_weights

    @observed_pool_weights.setter
    def observed_pool_weights(self, s: Union[Iterable, np.ndarray, sympy.Matrix]) -> None:
        """Set all the observed pool weights."""
        if isinstance(s, sympy.Matrix):
            assert len(s) == self.n_states, \
                "observed pool weights be a vector of size n_states"
            iterator = s.flat()
        elif isinstance(s, np.ndarray):
            assert s.size == self.n_states, \
                "observed pool weights be a vector of size n_states"
            iterator = s.flat
        else:
            iterator = s

        for i, value in enumerate(iterator):
            self.set_observed_pool_weight(i, value)

    @property
    def contributed_turnovers(self) -> "ContributedTurnovers":
        """Get all the contributed turnovers."""
        return self._contributed_turnover_matrix

    @contributed_turnovers.setter
    def contributed_turnovers(self, M: Union[Iterable, np.ndarray, sympy.Matrix]) -> None:
        """Set all the contributed turnovers."""
        if isinstance(M, sympy.Matrix):
            assert M.shape == (self.n_states, self.n_states), \
                "observed pool weights be a vector of size n_states"
            iterator = M.flat()
        elif isinstance(M, np.ndarray):
            assert M.shape == (self.n_states, self.n_states), \
                "observed pool weights be a vector of size n_states"
            iterator = M.flat
        else:
            iterator = more_itertools.flatten(M)

        for i, value in enumerate(iterator):
            self.set_contributed_turnover(int(i / self.n_states), int(i % self.n_states), value)

    def set_contributed_turnover(self, i: int, j: int, value: Union[float, sympy.Expr]) -> None:
        """Set the contributed turnover of a single transition."""
        self.check_state_index(i)
        self.check_state_index(j)
        self._contributed_turnover_matrix[i, j] = value

    def _get_params_dict(
        self, x: Optional[Iterable[float]] = None
    ) -> Dict[sympy.Symbol, float]:
        """Get a dictionary mapping all parameters to values."""
        if self.n_params == 0:
            return dict()
        else:
            assert (
                x is not None
            ), "the input must not be empty if the model has at least one parameter"
            x_list = list(x)
            assert (
                len(x_list) == self.n_params
            ), "the input must have length equal to n_states"
            return dict(zip(self._params, x_list))

    def get_params(self) -> List[sympy.Symbol]:
        """Get the list of parameters (symbols)."""
        return self._params

    def get_param(self, i: int) -> sympy.Symbol:
        """Get a single parameter (symbol)."""
        self.check_param_index(i)
        return self._params[i]

    def set_param_bounds(self, i: int, lb: float = np.nan, ub: float = np.nan) -> None:
        """Set the bounds for one of the parameters."""
        self.check_param_index(i)
        if not np.isnan(lb):
            self._lbs[i] = lb
        if not np.isnan(ub):
            self._ubs[i] = ub
        self._p0[i] = (self._lbs[i] + self._ubs[i]) / 2.0

    def get_param_bounds(self, i: int) -> Tuple[float, float]:
        """Get the bounds for one of the parameters."""
        self.check_param_index(i)
        return float(self._lbs[i]), float(self._ubs[i])

    def display_bounds(self) -> List[Tuple[sympy.core.Rel, sympy.core.Rel]]:
        """Return a list of sympy expressions showing the parameter bounds."""
        return [
            (
                sympy.LessThan(self._lbs[i], self._params[i]),
                sympy.LessThan(self._params[i], self._ubs[i]),
            )
            for i in range(self.n_params)
        ]

    # Below are all the methods that calculate SCM model attributes (like labeling,
    # age, residence-time, etc.)
    # using Sympy.

    def M_sympy(self) -> sympy.Matrix:
        """Get a sympy Matrix representing the contributed turnovers.

        Parameters
        ---------

        Returns
        -------
            M: sympy.Matrix
                The M-matrix containing the contributed turnovers
        """
        return self._contributed_turnover_matrix.as_sympy()

    def s_sympy(self) -> sympy.Expr:
        """Get a sympy Expr representing the observed pool weights.

        Parameters
        ---------

        Returns
        -------
            s: sympy.Expr
                The vector of observed pool weights
        """
        return self._observed_pool_weights.as_sympy()

    def _M_plus_mu_I_sympy(self) -> sympy.Expr:
        """Get a sympy Matrix representing the contributed turnovers with growth removed.

        Parameters
        ---------

        Returns
        -------
            M_plus_mu_I: sympy.Expr
                A matrix containing the contributed turnovers with growth removed
        """
        mu = self.growth_rate
        eye = sympy.eye(self.n_states)
        M = self.M_sympy()
        return M + mu * eye

    def f_sympy(self) -> sympy.Expr:
        """Get a sympy Expr of the system labeling

        Parameters
        ---------

        Returns
        -------
            f: sympy.Expr
                the system labeling curve

        Notes
        -----

        .. math:: f_s(t) = \\mathbf{s}^\\top e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        s = self.s_sympy()
        return (s.T @ self.vf_sympy())[0]

    def fdot_sympy(self) -> sympy.Expr:
        """Get a sympy Expr of the time derivative of the system labeling

        Parameters
        ---------

        Returns
        -------
            fdot : sympy.Expr
                the derivative system labeling curve

        Notes
        -----

        .. math:: \\dot{f}_s(t) = \\mathbf{s}^\\top \\mathbf{M} e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        s = self.s_sympy()
        return (s.T @ self.vfdot_sympy())[0]

    def fddot_sympy(self) -> sympy.Expr:
        """Get a sympy Expr of the 2nd derivative of the system labeling

        Parameters
        ---------

        Returns
        -------
            fddot : sympy.Expr
                the 2nd derivative system labeling curve

        Notes
        -----

        .. math:: \\ddot{f}_s(t) = \\mathbf{s}^\\top \\mathbf{M}^2 e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        s = self.s_sympy()
        return (s.T @ self.vfddot_sympy())[0]

    def vf_sympy(self) -> sympy.Expr:
        """Get a sympy Matrix representing the labeling curve vector.

        Parameters
        ---------

        Returns
        -------
            vf: sympy.Matrix
                the labeling curve vector

        Notes
        -----

        .. math:: \\mathbf{f}(t) = e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        t = self._time
        M = self.M_sympy()
        return (M * t).exp() @ self._ones

    def vfdot_sympy(self) -> sympy.Expr:
        """Get a sympy Matrix representing the time derivative of labeling curve vector.

        Parameters
        ---------

        Returns
        -------
            vfdot: sympy.Matrix
                the time derivative of the labeling curve vector

        Notes
        -----

        .. math:: \\dot{\\mathbf{f}}(t) = \\mathbf{M} e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        t = self._time
        M = self.M_sympy()
        return M @ (M * t).exp() @ self._ones

    def vfddot_sympy(self) -> sympy.Expr:
        """Get a sympy Matrix representing the 2nd derivative of labeling curve vector.

        Parameters
        ---------

        Returns
        -------
            vfddot: sympy.Matrix
                the 2nd derivative of the labeling curve vector

        Notes
        -----

        .. math:: \\ddot{\\mathbf{f}}(t) = \\mathbf{M}^2 e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        t = self._time
        M = self.M_sympy()
        return M @ M @ (M * t).exp() @ self._ones

    def fdot_zero_sympy(self) -> sympy.Expr:
        """Get a sympy Expr of the initial slope of the system labeling curve.

        Parameters
        ---------

        Returns
        -------
            fddot : sympy.Expr
                the initial slope of the system labeling curve

        Notes
        -----

        .. math:: \\ddot{f}_s(t) = \\mathbf{s}^\\top \\mathbf{M}^2 e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        s = self.s_sympy()
        return (s.T @ self.vfdot_zero_sympy())[0]

    def vfdot_zero_sympy(self) -> sympy.Expr:
        """Get a sympy Expr of the initial slope of the labeling curve vector.

        Parameters
        ---------

        Returns
        -------
            vfdot_zero: sympy.Matrix
                the initial slope of the labeling curve vector

        Notes
        -----

        .. math:: \\dot{\\mathbf{f}}(0) = \\mathbf{M} \\mathbf{1}_n

        """
        M = self.M_sympy()
        return M @ self._ones

    def mean_ages_sympy(self) -> sympy.Matrix:
        """Get a sympy Matrix representing the mean ages for all states.

        Parameters
        ---------

        Returns
        -------
            mean_ages: sympy.Matrix
                mean ages of all states

        Notes
        -----

        .. math:: \\mathbb{E}[\\mathcal{A}] = -\\mathbf{M}^{-1} \\mathbf{1}_n

        """
        return -self.M_sympy().inv() @ self._ones

    def mean_age_sympy(self) -> sympy.Expr:
        """Get a sympy Expr of the system mean age.

        Parameters
        ---------

        Returns
        -------
            mean_age : sympy.Expr
                system mean age

        Notes
        -----

        .. math::
            \\mathbb{E}[\\mathcal{A}_s] = \\int_0^\\infty f_s(t) =
            -\\mathbf{s}^\\top \\mathbf{M}^{-1} \\mathbf{1}_n

        """
        return (self.s_sympy().T @ self.mean_ages_sympy())[0]

    def ages_cdf_sympy(self) -> sympy.Expr:
        """Get a sympy Expr of the age CDFs of all states.

        Parameters
        ----------

        Returns
        -------
            ages_cdf : sympy.Expr
                the CDF of the age of all states

        Notes
        -----

        .. math::
            P(\\mathcal{A} \\leq t) = \\mathbf{1}_n - e^{\\mathbf{M} t} \\mathbf{1}_n

        """
        return self._ones - self.vf_sympy()

    def ages_pdf_sympy(self) -> sympy.Expr:
        """Get a sympy Expr of the age PDFs of all states.

        Parameters
        ----------

        Returns
        -------
            ages_pdf : sympy.Expr
                the PDF of the age of all states

        Notes
        -----

        .. math::
            p(\\mathcal{A} = t) = - \\mathbf{M} e^{\\mathbf{M} t} \\mathbf{1}_n

        """
        return -self.vfdot_sympy()

    def age_cdf_sympy(self) -> sympy.Expr:
        """Get a sympy Expr of the system age CDF.

        Parameters
        ----------

        Returns
        -------
            age_cdf : sympy.Expr
                the CDF of the system age

        Notes
        -----

        .. math::
            P(\\mathcal{A}_s \\leq t) = 1 - \\mathbf{s}^\\top e^{\\mathbf{M} t}
            \\mathbf{1}_n

        """
        return 1.0 - self.f_sympy()

    def age_pdf_sympy(self) -> sympy.Expr:
        """Get a sympy Expr of the system age PDF.

        Parameters
        ----------

        Returns
        -------
            age_pdf : sympy.Expr
                the PDF of the system age

        Notes
        -----

        .. math::
            p(\\mathcal{A}_s = t) = - \\mathbf{s}^\\top \\mathbf{M} e^{
            \\mathbf{M} t} \\mathbf{1}_n

        """
        return -self.fdot_sympy()

    def residence_time_cdf_sympy(self, ignore_growth: bool=False) -> sympy.Expr:
        """Get a sympy Expr of the system residence time CDF.

        Parameters
        ----------
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            residence_time : sympy.Expr
                the CDF of the system residence time

        Notes
        -----

        .. math::
            P(\\mathcal{T}_s \\leq t) = 1 - e^{\\mu t} \\mathbf{s}^\\top
            \\mathbf{M} e^{\\mathbf{M} t} \\mathbf{1}_n / \\mathbf{s}^\\top \\mathbf{M}
            \\mathbf{1}_n

        """
        if ignore_growth or self.growth_rate == 0:
            return 1.0 - self.fdot_sympy() / self.fdot_zero_sympy()
        else:
            t = self._time
            M = self.M_sympy()
            s = self.s_sympy()
            M_plus_mu_I = self._M_plus_mu_I_sympy()
            return (
                sympy.RealNumber(1.0)
                - (s.T @ M @ (M_plus_mu_I * t).exp() @ self._ones)[0]
                / self.fdot_zero_sympy()
            )

    def residence_time_pdf_sympy(self, ignore_growth: bool=False) -> sympy.Expr:
        """Get a sympy Expr of the system residence time PDF.

        Parameters
        ----------
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            residence_time : sympy.Expr
                the PDF of the system residence time

        Notes
        -----

        .. math::
            p(\\mathcal{T}_s = t) = - e^{\\mu t} \\mathbf{s}^\\top \\mathbf{M}
            (\\mathbf{M} + \\mu \\mathbf{I}_n)  e^{\\mathbf{M} t} \\mathbf{1}_n /
            \\mathbf{s}^\\top \\mathbf{M} \\mathbf{1}_n

        """
        if ignore_growth or self.growth_rate == 0:
            return -self.fddot_sympy() / self.fdot_zero_sympy()
        else:
            t = self._time
            M = self.M_sympy()
            s = self.s_sympy()
            M_plus_mu_I = self._M_plus_mu_I_sympy()
            return (
                -(s.T @ M @ M_plus_mu_I @ (M_plus_mu_I * t).exp() @ self._ones)[0]
                / self.fdot_zero_sympy()
            )

    def decay_rate_sympy(self, ignore_growth: bool=False) -> sympy.Expr:
        """Get a sympy Expr of the system decay rate.

        Parameters
        ----------
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            rate : sympy.Expr
                the system decay rate

        Notes
        -----

        .. math::
            \\kappa_{deg}(\\mathcal{A}_s) = - \\mathbf{s}^\\top \\mathbf{M}^2
            e^{\\mathbf{M} t} \\mathbf{1}_n / \\mathbf{s}^\\top \\mathbf{M}
            e^{\\mathbf{M} t} \\mathbf{1}_n - \\mu

        """
        if ignore_growth or self.growth_rate == 0:
            return -self.fddot_sympy() / self.fdot_sympy()
        else:
            return -self.fddot_sympy() / self.fdot_sympy() - self.growth_rate

    def mean_residence_time_sympy(self, ignore_growth: bool=False) -> sympy.Expr:
        """Get a sympy Expr of the mean system residence_time.

        Parameters
        ----------
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            residence_time : sympy.Expr
                the mean system residence_time

        Notes
        -----

        .. math::
            \\mathbb{E}[\\mathcal{T}] = - \\mathbf{s}^\\top \\mathbf{M} (
            \\mathbf{M} + \\mu \\mathbf{I}_n)^{-1} \\mathbf{1}_n / \\mathbf{s}^\\top
            \\mathbf{M} \\mathbf{1}_n

        """
        if ignore_growth or self.growth_rate == 0:
            return -1.0 / self.fdot_zero_sympy()
        else:
            M = self.M_sympy()
            s = self.s_sympy()
            inv_M_plus_mu_I = self._M_plus_mu_I_sympy().inv()
            return -(s.T @ M @ inv_M_plus_mu_I @ self._ones)[0] / self.fdot_zero_sympy()

    def expected_decay_rate_sympy(self, ignore_growth: bool=False) -> sympy.Expr:
        """Get a sympy Expr of the expected decay rate.

        Parameters
        ----------
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            rate : sympy.Expr
                the expected decay rate

        Notes
        -----

        .. math::
            \\mathbb{E}[\\kappa_{deg}(\\mathcal{A})] = -\\mathbf{s}^\\top
            \\mathbf{M} \\mathbf{1}_n - \\mu

        """
        if ignore_growth:
            return -self.fdot_zero_sympy()
        else:
            return -self.fdot_zero_sympy() - self.growth_rate

    def as_symbolic(self, key: str) -> sympy.Expr:
        """Return a sympy Expr object representing the specific dynamic attribute.

        Parameters
        ---------
            key: str
                The name of the attribute.

        Returns
        -------
            func_sympy: sympy.Expr
                The sympy expression representing the dynamic attribute.
        """
        try:
            func_sympy = getattr(self, key + "_sympy")
        except AttributeError:
            raise KeyError(f"Unrecognized attribute of Age Balance Analysis: '{key}'")
        return func_sympy()

    # Below are all the methods that calculate SCM model attributes (like labeling,
    # age, residence time, etc.)
    # numerically (using SciPy and NumPy).

    def M(self, x: Optional[Iterable[float]] = None) -> np.ndarray:
        """Get the contributed turnover matrix - M.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            M: np.ndarray
                The M-matrix containing the contributed turnovers.
        """
        if self.n_params == 0:
            return self._contributed_turnover_matrix.as_numpy()
        else:
            return self._contributed_turnover_matrix.as_numpy(self._get_params_dict(x))

    def abscissa(self, x: Optional[Iterable[float]] = None) -> float:
        """Get the largest eigenvalue of the M-matrix.

        Parameters
        ---------
            x : Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            abscissa : float
                The abscissa of the M matrix (largest eigenvalue)..

        """
        M = self.M(x)
        return max(np.linalg.eigvals(M).real)

    def s(self, x: Optional[Iterable[float]] = None) -> np.ndarray:
        """Get the observed pool weights

        Parameters
        ---------
            x : Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            s : np.ndarray
                The observed pool weights.

        """
        if self.n_params == 0:
            s = self._observed_pool_weights.as_numpy()
        else:
            s = self._observed_pool_weights.as_numpy(self._get_params_dict(x))
        return s / np.sum(s)

    def f(
        self,
        x: Optional[Iterable[float]] = None
    ) -> Callable[[Union[float, np.ndarray]], Union[float, np.ndarray]]:
        """Get a lambda expression for the system labeling.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            f: callable
                the system labeling as a function of time

        Notes
        -----

        .. math::
            f_s(t) = \\mathbf{s}^\\top e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        s = self.s(x)
        M = self.M(x)
        def func(t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
            if isinstance(t, np.ndarray):
                return np.array([np.sum(s.T @ expm(M * _t)) for _t in t], dtype=float)
            else:
                return np.sum(s.T @ expm(M * t))
        return func

    def fdot(
        self,
        x: Optional[Iterable[float]] = None
    ) -> Callable[[Union[float, np.ndarray]], Union[float, np.ndarray]]:
        """Get a lambda expression for the derivative of the system labeling.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            fdot: callable
                the 1st derivative of the system labeling as a function of time

        Notes
        -----

        .. math::
            \\dot{f}_s(t) = \\mathbf{s}^\\top \\mathbf{M} e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        s = self.s(x)
        M = self.M(x)
        def func(t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
            if isinstance(t, np.ndarray):
                return np.array([np.sum(s.T @ M @ expm(M * _t)) for _t in t], dtype=float)
            else:
                return np.sum(s.T @ M @ expm(M * t))
        return func

    def fddot(
        self,
        x: Optional[Iterable[float]] = None
    ) -> Callable[[Union[float, np.ndarray]], Union[float, np.ndarray]]:
        """Get a lambda expression for the 2nd derivative of the system labeling.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            fddot: callable
                the 2nd derivative of the system labeling as a function of time

        Notes
        -----

        .. math::
            \\ddot{f}_s(t) = \\mathbf{s}^\\top \\mathbf{M}^2 e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        s = self.s(x)
        M = self.M(x)
        def func(t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
            if isinstance(t, np.ndarray):
                return np.array([np.sum(s.T @ M @ M @ expm(M * _t)) for _t in t], dtype=float)
            else:
                return np.sum(s.T @ M @ M @ expm(M * t))
        return func

    def vf(
        self,
        x: Optional[Iterable[float]] = None
    ) -> Callable[[Union[float, np.ndarray]], np.ndarray]:
        """Get lambda expression for the vector of labeling curves.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            vf: callable
                the labeling curve vector as a function of time

        Notes
        -----

        .. math::
            \\mathbf{f}(t) = e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        M = self.M(x)
        def func(t: Union[float, np.ndarray]) -> np.ndarray:
            if isinstance(t, np.ndarray):
                return np.vstack([np.sum(expm(M * _t), axis=1) for _t in t]).T
            else:
                return np.sum(expm(M * t), axis=1)
        return func

    def vfdot(
        self,
        x: Optional[Iterable[float]] = None
    ) -> Callable[[Union[float, np.ndarray]], np.ndarray]:
        """Get lambda expression for the derivative of the vector of labeling curves.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            vfdot: callable
                the 1st derivative of the labeling curve vector as a function of time

        Notes
        -----

        .. math::
            \\dot{\\mathbf{f}}(t) = \\mathbf{M} e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        M = self.M(x)
        def func(t: Union[float, np.ndarray]) -> np.ndarray:
            if isinstance(t, np.ndarray):
                return np.vstack([np.sum(M @ expm(M * _t), axis=1) for _t in t]).T
            else:
                return np.sum(M @ expm(M * t), axis=1)
        return func

    def vfddot(
        self,
        x: Optional[Iterable[float]] = None
    ) -> Callable[[Union[float, np.ndarray]], np.ndarray]:
        """Get lambda expression for the 2nd derivative of the vector of labeling curves.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            vfddot: callable
                the 2nd derivative of the labeling curve vector as a function of time

        Notes
        -----

        .. math::
            \\ddot{\\mathbf{f}}(t) = \\mathbf{M}^2 e^{\\mathbf{M}t} \\mathbf{1}_n

        """
        M = self.M(x)
        def func(t: Union[float, np.ndarray]) -> np.ndarray:
            if isinstance(t, np.ndarray):
                return np.vstack([np.sum(M @ M @expm(M * _t), axis=1) for _t in t]).T
            else:
                return np.sum(M @ M @ expm(M * t), axis=1)
        return func

    def fdot_zero(self, x: Optional[Iterable[float]] = None) -> float:
        """Get the initial slope of the system labeling curve.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            fdot_zero: float
                the initial slope of the system labeling curve

        Notes
        -----

        .. math::
            \\dot{f}_s(0) = \\mathbf{s}^\\top \\mathbf{M} \\mathbf{1}_n

        """
        M = self.M(x)
        s = self.s(x)
        return np.sum(s.T @ M)

    def vfdot_zero(self, x: Optional[Iterable[float]] = None) -> np.ndarray:
        """Get the initial slope of the vector of labeling curves.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            vfdot_zero: np.ndarray
                the initial slope of the labeling curve vector

        Notes
        -----

        .. math::
            \\dot{\\mathbf{f}}(0) = \\mathbf{M} \\mathbf{1}_n

        """
        M = self.M(x)
        return np.sum(M, axis=1)

    def mean_ages(self, x: Optional[Iterable[float]] = None) -> np.ndarray:
        """Get the mean ages for all states.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            mean_ages: np.ndarray
                mean ages of all states

        Notes
        -----

        .. math::
            \\mathbb{E}[\\mathcal{A}] = -\\mathbf{M}^{-1} \\mathbf{1}_n

        """
        M = self.M(x)
        M_inv = np.linalg.inv(M)
        return -np.sum(M_inv, axis=1)

    def mean_age(self, x: Optional[Iterable[float]] = None) -> float:
        """Get the mean system age.

        Parameters
        ---------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            mean_age : float
                system mean age

        Notes
        -----

        .. math::
            \\mathbb{E}[\\mathcal{A}_s] = \\int_0^\\infty f_s(t) = -\\mathbf{s}^\\top
            \\mathbf{M}^{-1} \\mathbf{1}_n

        """
        M = self.M(x)
        s = self.s(x)
        M_inv = np.linalg.inv(M)
        return -np.sum(s.T @ M_inv)

    def conditional_area_under_curve(
        self,
        start: float = 0,
        end: float = np.inf,
        x: Optional[Iterable[float]] = None,
    ) -> float:
        """Get the area under the curve of the system labeling between two time points.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            area : float
                the computed AUC

        Notes
        -----

        .. math::
            \\int_a^b f_s(t) = \\mathbf{s}^\\top \\mathbf{M}^{-1} ( e^{
            \\mathbf{M}b} - e^{\\mathbf{M}a} ) \\mathbf{1}_n

        """
        M = self.M(x)
        s = self.s(x)
        M_inv = np.linalg.inv(M)
        exp_M_diff = self._exp_M_diff(start, end, x)
        return np.float64((s.T @ M_inv @ exp_M_diff)[0])

    def age_quantile(
        self,
        x: Optional[Iterable[float]] = None,
        quantile: Optional[float] = None,
    ) -> Union[float, Callable[[float], float]]:
        """Get a lambda expression for calculating system age quantiles.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.
            quantile: float, optional
                The desired age quantile, must be between 0 and 1. (default: None)

        Returns
        -------
            age / inv_f : float or callable
                the desired age quantile or the inverse function of the labeling curve

        Notes
        -----

        If the quantile argument is provided, the function returns a float with the result. Otherwise,
        it returns a callable which maps numbers between 0 and 1 to the age quantile.

        """

        inv_f = inversefunc(
            self.age_cdf(x),
            domain=0.0,
        )
        if quantile is not None:
            assert 0 <= quantile <= 1, "quantile must be between 0 and 1"
            return inv_f(quantile)
        else:
            return inv_f

    def median_age(
        self,
        x: Optional[Iterable[float]] = None,
    ) -> float:
        """Get a lambda expression for calculating median system age.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            median_age : float
                the median system age (half-life)

        Notes
        -----

        .. math::
            t_{1/2} \\qquad \\text{such that} \\qquad \\mathbf{s}^\\top
            e^{\\mathbf{M} t_{1/2}} \\mathbf{1}_n = \\frac{1}{2}

        """
        return self.age_quantile(x, 0.5)

    def _exp_M_diff(
        self,
        start: float = 0.0,
        end: float = 1.0,
        x: Optional[Iterable[float]] = None
    ) -> np.ndarray:
        """Returns the difference of matrix exponent at two time points."""
        if start < 0:
            raise ValueError("start must be non-negative")
        if start > end:
            raise ValueError("start must be smaller than end")
        elif start == end:
            return np.zeros(self.n_states)

        M = self.M(x)
        if end != np.inf:
            return np.sum(expm(M * end) - expm(M * start), axis=1)
        else:
            return -np.sum(expm(M * start), axis=1)

    def _M_plus_mu_I(self, x: Optional[Iterable[float]] = None) -> np.ndarray:
        """Returns a sympy Matrix representing the contributed turnovers with growth removed."""
        return self.M(x) + self.growth_rate * np.eye(self.n_states)

    def ages_cdf(
        self,
        x: Optional[Iterable[float]] = None
    ) -> Callable[[Union[float, np.ndarray]], np.ndarray]:
        """Get the age CDFs of all states.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            ages_cdf : callable
                the CDF of the age of all states

        Notes
        -----

        .. math::
            P(\\mathcal{A} \\leq t) = \\mathbf{1}_n - e^{\\mathbf{M} t} \\mathbf{1}_n

        """
        M = self.M(x)
        def func(t: Union[float, np.ndarray]) -> np.ndarray:
            if isinstance(t, np.ndarray):
                return np.vstack([1.0 - np.sum(expm(M * _t), axis=1) for _t in t]).T
            else:
                return 1.0 - np.sum(expm(M * t), axis=1)
        return func

    def ages_pdf(
        self,
        x: Optional[Iterable[float]] = None
    ) -> Callable[[Union[float, np.ndarray]], np.ndarray]:
        """Get the age PDFs of all states.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            ages_ddf : callable
                the PDF of the age of all states

        Notes
        -----

        .. math::
            p(\\mathcal{A} = t) = - \\mathbf{M} e^{\\mathbf{M} t} \\mathbf{1}_n

        """
        M = self.M(x)
        def func(t: Union[float, np.ndarray]) -> np.ndarray:
            if isinstance(t, np.ndarray):
                return np.vstack([-np.sum(M @ expm(M * _t), axis=1) for _t in t]).T
            else:
                return -np.sum(M @ expm(M * t), axis=1)
        return func

    def age_cdf(
        self,
        x: Optional[Iterable[float]] = None
    ) -> Callable[[Union[float, np.ndarray]], Union[float, np.ndarray]]:
        """Get the system age CDF.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            age_cdf : callable
                the CDF of the system age

        Notes
        -----

        .. math::
            P(\\mathcal{A}_s \\leq t) = 1 - \\mathbf{s}^\\top e^{\\mathbf{M} t}
            \\mathbf{1}_n

        """
        s = self.s(x)
        M = self.M(x)
        def func(t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
            if isinstance(t, np.ndarray):
                return np.array([1.0 - np.sum(s.T @ expm(M * _t)) for _t in t], dtype=float)
            else:
                return 1.0 - np.sum(s.T @ expm(M * t))

        return func

    def age_pdf(
        self,
        x: Optional[Iterable[float]] = None
    ) -> Callable[[Union[float, np.ndarray]], Union[float, np.ndarray]]:
        """Get the system age PDF.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.

        Returns
        -------
            age_pdf : callable
                the PDF of the system age

        Notes
        -----

        .. math::
            p(\\mathcal{A}_s = t) = - \\mathbf{s}^\\top \\mathbf{M}
            e^{\\mathbf{M} t} \\mathbf{1}_n

        """
        s = self.s(x)
        M = self.M(x)
        def func(t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
            if isinstance(t, np.ndarray):
                return np.array([- np.sum(s.T @ M @ expm(M * _t)) for _t in t], dtype=float)
            else:
                return -np.sum(s.T @ M @ expm(M * t))

        return func

    def residence_time_cdf(
        self,
        x: Optional[Iterable[float]] = None,
        ignore_growth: bool = False,
    ) -> Callable[[Union[float, np.ndarray]], Union[float, np.ndarray]]:
        """Get the system residence time CDF.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            residence_time_cdf : callable
                the CDF of the system residence time

        Notes
        -----

        .. math::
            P(\\mathcal{T}_s \\leq t) = 1 - e^{\\mu t} \\mathbf{s}^\\top
            \\mathbf{M} e^{\\mathbf{M} t} \\mathbf{1}_n / \\mathbf{s}^\\top \\mathbf{M}
            \\mathbf{1}_n

        """

        M = self.M(x)
        s = self.s(x)
        if ignore_growth:
            A = M
        else:
            A = self._M_plus_mu_I(x)
        fdot_zero = self.fdot_zero(x)
        def func(t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
            if isinstance(t, np.ndarray):
                return np.array([
                    1.0 - np.sum(s.T @ M @ expm(A*_t)) / fdot_zero
                    for _t in t
                ], dtype=float)
            else:
                return 1.0 - np.sum(s.T @ M @ expm(A*t)) / fdot_zero

        return func

    def residence_time_pdf(
        self,
        x: Optional[Iterable[float]] = None,
        ignore_growth: bool = False,
    ) -> Callable[[Union[float, np.ndarray]], Union[float, np.ndarray]]:
        """Get the system residence time PDF.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            residence_time_pdf : callable
                the PDF of the system residence time.

        Notes
        -----

        .. math::
            p(\\mathcal{T}_s = t) = - e^{\\mu t} \\mathbf{s}^\\top \\mathbf{M}
            (\\mathbf{M} + \\mu \\mathbf{I}_n)  e^{\\mathbf{M} t} \\mathbf{1}_n / \\mathbf{
            s}^\\top \\mathbf{M} \\mathbf{1}_n

        """
        M = self.M(x)
        s = self.s(x)
        fdot_zero = self.fdot_zero(x)
        if ignore_growth:
            A = M
        else:
            A = self._M_plus_mu_I(x)

        def func(t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
            if isinstance(t, np.ndarray):
                return np.array([
                    -np.sum(s.T @ M @ A @ expm(A*_t)) / fdot_zero
                    for _t in t
                ], dtype=float)
            else:
                return -np.sum(s.T @ M @ A @ expm(A*t)) / fdot_zero

        return func

    def decay_rate(
        self,
        x: Optional[Iterable[float]] = None,
        ignore_growth: bool = False,
    ) -> Callable[[Union[float, np.ndarray]], Union[float, np.ndarray]]:
        """Get the system decay rate as a function of time.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            rate : callable
                the system decay rate as a function of time

        Notes
        -----

        .. math::
            \\kappa_{deg}(\\mathcal{A}_s) = - \\mathbf{s}^\\top \\mathbf{M}^2
            e^{\\mathbf{M} t} \\mathbf{1}_n / \\mathbf{s}^\\top \\mathbf{M} e^{\\mathbf{
            M} t} \\mathbf{1}_n - \\mu

        """

        s = self.s(x)
        M = self.M(x)
        sM = s.T @ M
        sMM = sM @ M
        mu = 0.0 if ignore_growth else self.growth_rate
        def func(t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
            if isinstance(t, np.ndarray):
                return np.array([
                    -np.sum(sMM @ expm(M*_t)) / np.sum(sM @ expm(M*_t)) - mu
                    for _t in t
                ], dtype=float)
            else:
                return -np.sum(sMM @ expm(M*t)) / np.sum(sM @ expm(M*t)) - mu

        return func

    def mean_residence_time(
        self,
        x: Optional[Iterable[float]] = None,
        ignore_growth: bool = False,
    ) -> float:
        """Get the mean system residence time.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            residence_time : float
                the mean system residence time

        Notes
        -----

        .. math::
            \\mathbb{E}[\\mathcal{T}] = - \\mathbf{s}^\\top \\mathbf{M} (
            \\mathbf{M} + \\mu \\mathbf{I}_n)^{-1} \\mathbf{1}_n / \\mathbf{s}^\\top
            \\mathbf{M} \\mathbf{1}_n

        """
        if ignore_growth or self.growth_rate == 0:
            return -1.0 / self.fdot_zero(x)
        else:
            M = self.M(x)
            s = self.s(x)
            A = self._M_plus_mu_I(x)
            inv_A = np.linalg.inv(A)
            numerator = s.T @ M @ inv_A
            denominator = s.T @ M
            return - np.sum(numerator) / np.sum(denominator)

    def conditional_mean_residence_time(
        self,
        t0: float = 0,
        x: Optional[Iterable[float]] = None,
        ignore_growth: bool = False,
    ) -> float:
        """Get the conditional mean residence time.

        Parameters
        ----------
            t0 : float
                The initial time point after which to calculate the mean residence time.
            x: Iterable[float]
                Assigned values for all the model parameters.
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            residence_time : float
                the mean residence time in the interval t > t0

        Notes
        -----

        .. math::
            \\mathbb{E}[\\mathcal{T} | \\mathcal{T} \\geq t_0] = t_0 +
            \\frac{\\int_0^\\infty e^{\\mu t} \\dot{f}(t + t_0) dt}{\\dot{f}(t_0)}

        """
        if ignore_growth or self.growth_rate == 0:
            return t0 - self.f(x)(t0) / self.fdot(x)(t0)
        else:
            M = self.M(x)
            s = self.s(x)
            A = self._M_plus_mu_I(x)
            exp_M_t0 = expm(M*t0)
            inv_A = np.linalg.inv(A)
            numerator = s.T @ M @ inv_A @ exp_M_t0
            denominator = s.T @ M @ exp_M_t0
            return t0 - np.sum(numerator) / np.sum(denominator)

    def expected_decay_rate(
        self,
        x: Optional[Iterable[float]] = None,
        ignore_growth: bool = False,
    ) -> float:
        """Get the expected decay rate.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            rate : float
                the expected decay rate

        Notes
        -----

        .. math::
            \\mathbb{E}[\\kappa_{deg}(\\mathcal{A})] = -\\mathbf{s}^\\top
            \\mathbf{M} \\mathbf{1}_n - \\mu

        """
        if ignore_growth:
            return -self.fdot_zero(x)
        else:
            return -self.fdot_zero(x) - self.growth_rate

    def conditional_expected_decay_rate(
        self,
        start: float = 0,
        end: float = np.inf,
        x: Optional[Iterable[float]] = None,
        ignore_growth: bool = False,
    ) -> float:
        """Get the expected decay rate within a specified time interval.

        Parameters
        ----------
            start : float
                The initial time point after which to calculate the expected decay rate (t0).
            end : float
                The final time point until which to calculate the expected decay rate (t1).
            x: Iterable[float]
                Assigned values for all the model parameters.
            ignore_growth : bool
                a flag to ignore growth (i.e. not to subtract it from the calculated
                rate)

        Returns
        -------
            rate : float
                the expected decay rate within the age interval (t0, t1)

        Notes
        -----

        .. math::
            \\mathbb{E}_{t_0 < \\mathcal{A} < t_1}[\\kappa_{deg}(\\mathcal{A})] =
            \\mathbf{s}^\\top \\mathbf{M} (e^{\\mathbf{M} t_0} - e^{\\mathbf{M}t_1}) /
            \\mathbf{s}^\\top (e^{\\mathbf{M} t_0} - e^{\\mathbf{M} t_1}) - \\mu

        """
        M = self.M(x)
        s = self.s(x)
        exp_M_diff = self._exp_M_diff(start, end, x)
        if ignore_growth:
            return -np.float64((s.T @ M @ exp_M_diff)[0] / (s.T @ exp_M_diff)[0])
        else:
            return (-np.float64((s.T @ M @ exp_M_diff)[0] / (s.T @ exp_M_diff)[0]) -
                    self.growth_rate)

    def as_numeric(self, key: str, x: Optional[Iterable[float]] = None) -> Union[float, np.ndarray, callable]:
        """Return a constant of function representing the specific dynamic attribute.

        Parameters
        ---------
            key: str
                The name of the attribute.
            x: Optional[Iterable[float]]
                Assigned values for all the model parameters.

        Returns
        -------
            value: float, np.ndarray, callable
                The value, array or lambda expression representing the dynamic attribute.
        """

        try:
            func_numeric = getattr(self, key)
        except AttributeError:
            raise KeyError(f"Unrecognized attribute of Age Balance Analysis: '{key}'")
        return func_numeric(x)

    def _minimize(
        self,
        f: callable,
        x0: Optional[np.ndarray] = None,
        basinhopping_kwargs: Optional[dict] = None,
        minimizer_kwargs: Optional[dict] = None,
        raise_exception: bool = True,
    ) -> Optional[OptimizeResult]:
        """Find the minimum x for a scalar function f(x)."""
        if self.n_params == 0:
            raise ValueError("This CM has no free parameters, nothing to fit.")
        if x0 is None:
            x0 = self._p0
        if basinhopping_kwargs is None:
            basinhopping_kwargs = {}
        if minimizer_kwargs is None:
            minimizer_kwargs = {}

        minimizer_kwargs["bounds"] = Bounds(self._lbs, self._ubs)
        results = basinhopping(
            func=f, x0=x0, minimizer_kwargs=minimizer_kwargs, **basinhopping_kwargs
        )

        if not results.success:
            if raise_exception:
                raise Exception("minimization failed: " + str(results.message))
            else:
                print("minimization failed: " + str(results.message))
                return None
        else:
            return results.lowest_optimization_result

    def minimize(
        self,
        tdata: np.ndarray,
        ydata: np.ndarray,
        check_mass_balance: bool = False,
        basinhopping_kwargs: Optional[dict] = None,
        minimizer_kwargs: Optional[dict] = None,
        raise_exception: bool = True,
    ) -> Optional[CompartmentalModelFittingResults]:
        """Fit the model to the data from a single mix of pools using `scipy.minimize`

        Parameters
        ----------
            tdata : np.ndarray
                The time series.
            ydata : np.ndarray
                The target values.
            check_mass_balance : bool
                Whether to check the mass balance constraint.

        Returns
        -------
            result : CompartmentalModelFittingResults
        """
        def fun(x) -> float:
            # for fitting, we minimize the use of Sympy in order to have faster calculations
            # furthermore, assigning the parameter values should be done before we
            # apply the matrix exponent, in order to avoid division by zero (for example, this
            # happens if after the symbolic diagonalization of M, we assign the same numeric value to
            # two distinct eigenvalues).

            M = self.M(x)
            s = self.s(x)

            penalty = 0.0
            if check_mass_balance:
                # check the mass balance constraint
                # calculate the total efflux minus influx
                mass_imbalance = s.T @ M + s.T * self.growth_rate
                # if the value is negative, assume it is balanced by an implicit efflux
                mass_imbalance[mass_imbalance < 0] = 0.0
                # if there are no positive values left, the system is mass-balanced (penalty = 0).
                # if mass-balance is violated, add a large penalty proportional to the total imbalance
                penalty = 1e10 * sum(mass_imbalance.flat)
            else:
                # check the conditions for growing systems (i.e. that there is a
                # feasible solution to the state pool-sizes, even when growing at rate mu)
                abscissa = max(np.linalg.eigvals(M).real)
                if self.growth_rate > -abscissa:
                    # if this matrix is infeasible, add a large penalty proportional to the difference
                    penalty = 1e10 * (self.growth_rate + abscissa)

            try:
                # calculate the residual sum of squares for `f(t)` vs `y`
                rss = 0.0
                for t, y in zip(tdata, ydata):
                    rss += ((s.T @ expm(M * t)).sum() - y) ** 2
                return penalty + rss
            except RuntimeError:
                # if labeling computation fails, discard this 'x' by returning a large value
                return 1e6

        results = self._minimize(f=fun, basinhopping_kwargs=basinhopping_kwargs,
                                 minimizer_kwargs=minimizer_kwargs,
                                 raise_exception=raise_exception)
        if results is None:
            return None

        # calculate the Aikaike information criterion (ΔAIC) based on:
        # https://en.wikipedia.org/wiki/Akaike_information_criterion#Comparison_with_least_squares
        rss = results.fun  # residual sum of squares
        n = len(tdata)
        delta_aic = 2 * self.n_params + n * np.log(rss / n)
        return CompartmentalModelFittingResults(
            self.parameterize(results.x), popt=results.x, pcov=results.hess_inv, n_params=self.n_params,
            n_samples=n, rss=rss, delta_aic=delta_aic
        )

    def _elementary(self, i: int) -> np.ndarray:
        """Return the elementary basis vector e_i.

        Parameters
        ----------
            i: int
                an index
        """
        self.check_state_index(i)
        s = np.zeros((self.n_states, 1))
        s[int(i), 0] = 1.0
        return s

    def minimize_multiple_pools(
        self,
        data: List[Tuple[int, float, float]],
        basinhopping_kwargs: Optional[dict] = None,
        minimizer_kwargs: Optional[dict] = None,
        raise_exception: bool = True,
    ) -> Optional[CompartmentalModelFittingResults]:
        """Fit the model to data from multiple single-pool measurements using
        `scipy.minimize`.

        Parameters
        ---------
            data : List[Tuple[int, float, float]]
                A list of tuples representing the measured pool index,
                the time stamp, and the unlabeled fraction.

        Returns
        -------
            result : CompartmentalModelFittingResults
        """
        def fun(x) -> float:
            M = self.M(x)
            penalty = 0.0
            # check the conditions for growing systems (i.e. that there is a
            # feasible solution to the state pool-sizes, even when growing at rate mu)
            abscissa = max(np.linalg.eigvals(M).real)
            if self.growth_rate > -abscissa:
                # if this matrix is infeasible, add a large penalty proportional to the difference
                penalty = 1e6 * (self.growth_rate + abscissa)

            try:
                rss = 0.0
                for i, t, y in data:
                    rss += ((self._elementary(i).T @ expm(M * t)).sum() - y) ** 2
                return penalty + rss
            except RuntimeError:
                # if labeling computation fails, discard this 'x' by returning a large value
                return 1e6

        results = self._minimize(f=fun, basinhopping_kwargs=basinhopping_kwargs,
                                 minimizer_kwargs=minimizer_kwargs,
                                 raise_exception=raise_exception)
        if results is None:
            return None

        # calculate the Aikaike information criterion (ΔAIC) based on:
        # https://en.wikipedia.org/wiki/Akaike_information_criterion#Comparison_with_least_squares
        rss = results.fun  # residual sum of squares
        n = len(data)
        delta_aic = 2 * self.n_params + n * np.log(rss / n)
        return CompartmentalModelFittingResults(
            self.parameterize(results.x), popt=results.x, pcov=results.hess_inv, n_params=self.n_params,
            n_samples=n, rss=rss, delta_aic=delta_aic
        )

    def minimize_M_given_s(
        self,
        s0: np.ndarray,
        tdata: np.ndarray,
        ydata: np.ndarray,
        x0: Optional[np.ndarray] = None,
        basinhopping_kwargs: Optional[dict] = None,
        minimizer_kwargs: Optional[dict] = None,
        raise_exception: bool = True,
    ) -> Tuple[np.ndarray, OptimizeResult]:
        """Fit M using non-linear optimization, given 's' and measured data using
        `scipy.minimize`.

        Parameters
        ---------
            s0 : np.ndarray
                The pool weight vector.
            tdata : np.ndarray
                The time series.
            ydata : np.ndarray
                The target values.
            x0 : ndarray
                Initial assignment for the parameter values.

        Returns
        -------
            x_opt : ndarray
                The optimal parameter values (best fit).
            results : OptimizeResult
                The optimization result represented as a ``OptimizeResult`` object.
                Important attributes are: ``x`` the solution array, ``success`` a
                Boolean flag indicating if the optimizer exited successfully and
                ``message`` which describes the cause of the termination. See
                `OptimizeResult` for a description of other attributes.
        """
        def fun(x) -> float:
            M = self.M(x)
            abscissa = max(np.linalg.eigvals(M).real)
            penalty = 0.0
            if abscissa > -self.growth_rate:
                penalty = 1e6 * (self.growth_rate + abscissa)
            try:
                # calculate the residual sum of squares for `f(t)` vs `y`
                rss = 0.0
                for t, y in zip(tdata, ydata):
                    rss += ((s0.T @ expm(M * t)).sum() - y) ** 2
                return penalty + rss
            except RuntimeError:
                return 1e6

        results = self._minimize(f=fun, x0=x0,
                                 basinhopping_kwargs=basinhopping_kwargs,
                                 minimizer_kwargs=minimizer_kwargs,
                                 raise_exception=raise_exception)
        if results is None:
            raise Exception("minimization failed: " + str(results.message))

        return results.x, results

    def minimize_s_given_M(
        self,
        tdata: np.ndarray,
        ydata: np.ndarray,
        x0: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, float]:
        """Fit pool weights using quadratic programming (for a given M and measured
        data) using `scipy.minimize`.

        Parameters
        ---------
            tdata : np.ndarray
                The time series.
            ydata : np.ndarray
                The target values.
            x0 : ndarray
                Model parameter values.
        Returns
        -------
            s_opt : ndarray
                The optimal pool weight vector (best fit).
            rss : float
                Residual sum of squares
        """

        if x0 is None:
            x0 = self._p0

        # now use quadratic programming to find the least-squares fit for `s` (for a
        # given M)
        s_variable = cvxpy.Variable(self.n_states)
        X = self.vf(x0)(tdata)
        resid = s_variable @ X - ydata
        obj = cvxpy.norm2(resid)
        prob = cvxpy.Problem(
            objective=cvxpy.Minimize(obj),
            constraints=[
                s_variable >= np.zeros(self.n_states),  # weights are positive
                s_variable.sum() <= 1.0 + 1e-6,  # sum of weights equals 1
                s_variable.sum() >= 1.0 - 1e-6,  # sum of weights equals 1
                s_variable @ self._M_plus_mu_I(x0) <= 0.0,  # mass-balance constraints
            ]
        )
        rss = prob.solve(solver=cvxpy.CLARABEL)
        if not np.isfinite(rss):
            raise Exception("Quadratic program infeasible or unbounded")
        if isinstance(rss, str):
            raise Exception("Quadratic program failed: " + rss)
        return s_variable.value, rss

    def minimize_whole_system(
        self,
        tdata: np.ndarray,
        ydata: np.ndarray,
        niter: int = 100,
        basinhopping_kwargs: Optional[dict] = None,
        minimizer_kwargs: Optional[dict] = None,
        raise_exception: bool = True,
    ) -> Optional[CompartmentalModelFittingResults]:
        """Fit the model to data from a whole system (pool sizes are free variables)
        using `scipy.minimize`.

        Parameters
        ---------
            tdata : np.ndarray
                The time series.
            ydata : np.ndarray
                The target values.
            niter : int, optional
                The number of iterations in the optimization procedure (default=100).
            convergence_threshold : float, optional
                The threshold for testing convergence (default=1e-6).

        Returns
        -------
            result : CompartmentalModelFittingResults
        """

        # Here, we need to find the best fit for M while at the same time
        # find the values for the pool sizes. One of the issues that is
        # complicates things, is that we also need to ensure that the values of s and M
        # satisfy the mass-balance constraints, making it a non-linear optimization
        # in a space with bilinear constraints.
        # Our solution is to solve it iteratively, by alternating between two
        # optimizations:
        # (1) Fitting the parameters of M while s is kept constant (as in `fit()`)
        # (2) Fitting s while M is kept constant (which can be done using quadratic
        #     programming)
        if niter <= 0:
            raise ValueError("niter must be a positive integer")

        x0 = self._p0
        last_delta_aic = np.inf
        convergence_threshold = 1e-6
        i = 0
        while True:
            i += 1
            # iteration phase 1
            s, rss = self.minimize_s_given_M(tdata, ydata, x0)

            # validate result
            self.is_M_mass_balanced(x0, raise_exception=True)

            # iteration phase 2
            x0, results = self.minimize_M_given_s(
                s, tdata, ydata, x0,
                basinhopping_kwargs=basinhopping_kwargs,
                minimizer_kwargs=minimizer_kwargs,
                raise_exception=raise_exception,
            )

            n = len(tdata)
            rss = results.fun
            delta_aic = 2 * self.n_params + n * np.log(rss / n)
            if (i == niter) or (last_delta_aic - convergence_threshold <= delta_aic <= last_delta_aic):
                result_cm = self.parameterize(x0)
                result_cm.observed_pool_weights = s
                return CompartmentalModelFittingResults(
                    result_cm, popt=x0, pcov=results.hess_inv, n_params=self.n_params,
                    n_samples=n, rss=rss, delta_aic=delta_aic
                )
            else:
                last_delta_aic = delta_aic

    def _curve_fit(self, f: callable, tdata: np.ndarray, ydata: np.ndarray) -> (
            Optional)[CompartmentalModelFittingResults]:
        """A helper function for the other fitting methods using `scipy.curve_fit`."""

        if self.n_params == 0:
            raise ValueError("This CM has no free parameters, nothing to fit.")

        n = len(tdata)
        # see Part 3 for optimization function derails
        try:
            popt, pcov = curve_fit(
                f=f,
                xdata=tdata,
                ydata=ydata,
                p0=self._p0,
                bounds=[self._lbs, self._ubs],
                full_output=False,
            )
            if np.all(popt == self._p0):
                raise RuntimeError("optimization remained at the initial point")

            # calculate the Aikaike information criterion (ΔAIC) based on:
            # https://en.wikipedia.org/wiki/Akaike_information_criterion#Comparison_with_least_squares
            rss = sum((ydata - f(tdata, *popt)) ** 2)  # residual sum of squares
            delta_aic = 2 * self.n_params + n * np.log(rss / n)
            return CompartmentalModelFittingResults(
                self.parameterize(popt), popt=popt, pcov=pcov, n_params=self.n_params,
                n_samples=n, rss=rss, delta_aic=delta_aic
            )
        except RuntimeError as e:
            # if the optimization failed
            print("curve_fit failed: " + str(e))
            return None

    def fit(
        self, tdata: np.ndarray, ydata: np.ndarray, check_mass_balance: bool = False
    ) -> Optional[CompartmentalModelFittingResults]:
        """Fit the model to the data from a single mix of pools using
        `scipy.curve_fit`
        .

        Parameters
        ----------
            tdata : np.ndarray
                The time series.
            ydata : np.ndarray
                The target values.
            check_mass_balance : bool
                Whether to check the mass balance constraint.

        Returns
        -------
            result : CompartmentalModelFittingResults
        """
        def fun(_tdata: np.ndarray, *x) -> np.ndarray:
            # for fitting, we minimize the use of Sympy in order to have faster
            # calculations furthermore, assigning the parameter values should be
            # done before we apply the matrix exponent, in order to avoid division by
            # zero (for example, this happens if after the symbolic diagonalization
            # of M, we assign the same numeric value to two distinct eigenvalues).

            M = self.M(x)
            s = self.s(x)
            if check_mass_balance:
                # check the mass balance constraint
                if not self.is_mass_balanced(x, raise_exception=False):
                    # return a vector of ones, if mass-balance is violated
                    return np.ones(len(_tdata))
            else:
                # check the conditions for growing systems (i.e. that there is a
                # feasible solution to the state pool-sizes, even when growing at
                # rate mu)
                abscissa = self.abscissa(x)
                if self.growth_rate > -abscissa:
                    # return a vector of ones, if this matrix is infeasible
                    return np.ones(len(_tdata))

            try:
                f_values = [(s.T @ expm(M * t)).sum() for t in _tdata]
                return np.array(f_values, dtype=float)
            except RuntimeError:
                # return a vector of ones, if labeling computation fails
                return np.ones(len(_tdata))

        return self._curve_fit(fun, tdata, ydata)

    def fit_multiple_pools(
        self, data: List[Tuple[int, float, float]]
    ) -> Optional[CompartmentalModelFittingResults]:
        """Fit the model to data from multiple single-pool measurements using
        `scipy.curve_fit`.

        Parameters
        ---------
            data : List[Tuple[int, float, float]]
                A list of tuples representing the measured pool index,
                the time stamp, and the unlabeled fraction.

        Returns
        -------
            result : CompartmentalModelFittingResults
        """
        idx, tdata, ydata = zip(*data)
        tdata = np.array(list(zip(idx, tdata)))
        ydata = np.array(ydata)

        def fun(_tdata: List[Tuple[int, float]], *x) -> np.ndarray:
            M = self.M(x)
            try:
                pred = [(self._elementary(i).T @ expm(M * t)).sum() for i, t in _tdata]
                return np.array(pred)
            except RuntimeError:
                # return vector of ones if labelling computation fails
                return np.ones(len(_tdata))

        return self._curve_fit(fun, tdata, ydata)


    def fit_whole_system(
        self,
        tdata: np.ndarray,
        ydata: np.ndarray,
        niter: int = 10,
        verbose: bool = False,
    ) -> Optional[CompartmentalModelFittingResults]:
        """Fit the model to data from a whole system (pool sizes are free variables)
        using `scipy.curve_fit`.

        Parameters
        ---------
            tdata : np.ndarray
                The time series.
            ydata : np.ndarray
                The target values.
            niter : int, optional
                The number of iterations in the optimization procedure.

        Returns
        -------
            result : CompartmentalModelFittingResults
        """

        # Here, we need to find the best fit for M while at the same time
        # find the values for the pool sizes. One of the issues that is
        # complicates things, is that we also need to ensure that the values of s and M
        # satisfy the mass-balance constraints, making it a non-linear optimization
        # in a space with bilinear constraints.
        # Our solution is to solve it iteratively, by alternating between two
        # optimizations:
        # (1) Fitting the parameters of M while s is kept constant (as in `fit()`)
        # (2) Fitting s while M is kept constant (which can be done using quadratic
        #     programming)
        if self.n_params == 0:
            raise ValueError("This CM has no free parameters, nothing to fit.")

        p0 = self._p0
        M = self.M(p0)
        s = self.s(p0)
        if np.any(s.T @ M > -s.T * self.growth_rate):
            # the initial values for s and M do not comply with the mass-balance
            # constraints, therefore we initialize s using the dominant eigenvector

            # first, we have to ensure that the abscissa is lower than -mu (otherwise
            # there is no feasible solution for s)
            eig_res = np.linalg.eig(M)
            i_abscissa = np.argmax(eig_res.eigenvalues.real)
            abscissa = eig_res.eigenvalues[i_abscissa].real
            if abscissa > -self.growth_rate:
                raise ValueError(
                    "The initial parameters for M don't satisfy the growth rate "
                    "constraints."
                )

            # initialize s with the eigenvector corresponding to the abscissa, so that
            # (s, M) will definitely satisfy the mass-balance constraints
            s = eig_res.eigenvectors[:, i_abscissa]
            if not np.all(s >= 0):
                raise ValueError(
                    "The dominant eigenvector of M contains negative values."
                )

            # normalize the pool size vector to sum up to 1
            s = s / sum(s)

        if verbose:
            print("s = ", s)

        fitting_res = None
        for i in range(niter):

            ## iteration phase 1
            # use the given 's' to minimize the residual (as we do in `fit()`)
            def func(_tdata: np.ndarray, *x) -> np.ndarray:
                M = self.M(x)
                abscissa = max(np.linalg.eigvals(M).real)
                if abscissa > -self.growth_rate:
                    return np.ones(len(_tdata))
                try:
                    f_values = [np.sum(s.T @ expm(M * t)) for t in _tdata]
                    return np.array(f_values, dtype=float)
                except RuntimeError:
                    return np.ones(len(_tdata))

            # use the `func` function to find the best fit for M
            fitting_res = self._curve_fit(func, tdata, ydata)
            if fitting_res is None:
                return None

            M = fitting_res.cm.M()
            if verbose:
                print("M = ", M)

            ## iteration phase 2
            # now use linear programming to find the best `s` assuming the resulting
            # M is fixed
            X = np.vstack([np.sum(expm(M * t), axis=1) for t in tdata]).T
            s_variable = cvxpy.Variable(self.n_states)
            resid = s_variable @ X - ydata
            obj = cvxpy.norm2(resid)
            prob = cvxpy.Problem(
                objective=cvxpy.Minimize(obj),
                constraints=[
                    np.ones(self.n_states) @ s_variable <= np.ones(self.n_states) + 1e-6,
                    np.ones(self.n_states) @ s_variable >= np.ones(self.n_states) - 1e-6,
                    s_variable @ M <= -np.ones(self.n_states) * self.growth_rate,
                    s_variable >= np.zeros(self.n_states),
                ]
            )
            rss = prob.solve(solver=cvxpy.CLARABEL)
            if np.isfinite(rss):
                s = s_variable.value
                if verbose:
                    print("s = ", s)
                    print("RSS = ", rss)
            else:
                print("Quadratic programming failed: " + rss)
                return None
            fitting_res.cm.observed_pool_weights = s

        return fitting_res

    def draw_transition_matrix(
        self, ax: plt.Axes, x: Optional[Iterable[float]] = None, seed: int = 13648
    ) -> None:
        """Draws the transition matrix using NetworkX.

        Parameters
        ----------
            ax : plt.Axes
                A matplotlib Axes instance to plot on.

            x: Iterable[float]
                Assigned values for all the model parameters.

            seed : int, optional
                A random seed for the spring layout initialization.

        """
        M = self.M(x)
        G = nx.Graph()
        edge_labels = {}
        for i in range(M.shape[0]):
            influx = -M[i, :].sum()
            if influx >= 1e-3:
                G.add_edge(f"i{i}", f"s{i}", weight=3)
                edge_labels[(f"i{i}", f"s{i}")] = influx.round(2)
            for j in range(M.shape[1]):
                if i == j:
                    continue
                if np.abs(M[i, j]) < 1e-3:
                    continue
                G.add_edge(f"s{j}", f"s{i}", weight=1)
                edge_labels[(f"s{j}", f"s{i}")] = M[i, j].round(2)

        # instead of the diagonal values, show the row sum as
        # the turnover contributed by the external state

        pos = nx.spring_layout(G, seed=seed)
        nx.draw_networkx_nodes(G, pos=pos, node_size=400, ax=ax)  # draw nodes and edges
        nx.draw_networkx_labels(G, pos=pos, ax=ax)  # draw node labels
        nx.draw_networkx_edges(
            G, pos=pos, arrowstyle="->", arrowsize=30, arrows=True, width=1, ax=ax
        )
        nx.draw_networkx_edge_labels(
            G, pos=pos, edge_labels=edge_labels, ax=ax
        )  # draw edge weights

    def plot(
        self,
        key: str,
        ax: Optional[plt.Axes] = None,
        x: Optional[Iterable[float]] = None,
        t_range: Optional[np.ndarray] = None,
        fmt: Optional[str] = None,
        **kwarg,
    ) -> plt.Axes:
        """Plot one of the attributes.

        Parameters
        ---------
            key: str
                The name of the attribute to plot.
            ax: plt.Axes, optional
                A matplotlib Axes instance to plot on.
            x: Iterable[float], optional
                Assigned values for all the model parameters.
            t_range: np.ndarray, optional
                The time range to plot.
            fmt: str, optional
                A shorthand formatting string for the plot (e.g. "r-", "g:", "o")

        Returns
        -------
            ax: plt.Axes
                The axes instance that were used for plotting.

        """
        # if no Axes are provided, create new ones
        if ax is None:
            _, ax = plt.subplots()

        # define the range of time points for plotting
        if t_range is None:
            # use a range where the largest eigenvalue (i.e. the one
            # closest to 0, since they are all negative, and therefore represents
            # the slowest timescale) will decay to almost zero: exp(-5)
            stop = 5.0 / np.abs(self.abscissa(x))
            t_range = np.linspace(start=0, stop=stop, num=100)

        func = self.as_numeric(key, x)
        if isinstance(func, (float, np.ndarray)):
            y = [func]*t_range.size
        else:
            y = func(t_range)

        if fmt is None:
            ax.plot(t_range, y, **kwarg)
        else:
            ax.plot(t_range, y, fmt, **kwarg)

        ax.set_xlabel("time")
        ax.set_ylabel(key)
        return ax

    def is_valid(
        self, x: Optional[Iterable[float]] = None, raise_exception: bool = False
    ) -> bool:
        """Test whether the model is valid (all rows have non-positive sums).

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.
            raise_exception : bool
                A flag indicating whether to raise an exception if the model is invalid
                (otherwise, the function simply returns False).

        Returns
        -------
            is_valid : bool
                True iff the model is valid

        Notes
        -----

        A valid model is one whose M-matrix has no rows with a negative sum:

        .. math:: \\mathbf{M} \\mathbf{1}_n \\leq \\mathbf{0}_n

        """
        M = self.M(x)
        try:
            assert np.all(
                np.sum(M, axis=1) <= 0
            ), "not valid: all rows of M must have a non-positive sum"
            return True
        except AssertionError as e:
            if raise_exception:
                raise e
            else:
                return False

    def has_delayed_input(
        self, x: Optional[Iterable[float]] = None, raise_exception: bool = False
    ) -> bool:
        """Test whether the model has a delayed input.

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.
            raise_exception : bool
                A flag indicating whether to raise an exception if the model is incomplete
                (otherwise, the function simply returns False).

        Returns
        -------
            has_delayed_input : bool
                True iff the model has a delayed input

        Notes
        -----

        We currently only test whether the labeling curve is convex:

        .. math:: \\mathbf{s}^\\top \\mathbf{M}^2 \\mathbf{1}_n \\geq \\mathbf{0}_n

        """
        M = self.M(x)
        s = self.s(x)
        try:
            assert np.sum(
                s.T @ M @ M, axis=1
            ) >= 0, "not complete: the labeling function must be convex"
            return False
        except AssertionError as e:
            if raise_exception:
                raise e
            else:
                return True

    def is_mass_balanced(
        self, x: Optional[Iterable[float]] = None, raise_exception: bool = False
    ) -> bool:
        """Test whether the model is mass balanced (considering the growth rate).

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.
            raise_exception : bool
                A flag indicating whether to raise an exception if the model is not mass-balanced
                (otherwise, the function simply returns False).

        Returns
        -------
            is_mass_balanced : bool
                True iff the model is mass-balanced

        Notes
        -----

        The model is mass balanced if and only if the following condition is met (for M and s):

        .. math::
            \\mathbf{s}^\\top (\\mathbf{M} + \\mu \\mathbf{I}_n) \\leq \\mathbf{0}_n

        """
        try:
            influx_minus_efflux = self.s(x).T @ self._M_plus_mu_I(x)
            assert np.all(influx_minus_efflux <= 0), (
                "not mass-balanced: effluxes are bigger than the influxes for some "
                "states"
            )
            return True
        except AssertionError as e:
            if raise_exception:
                raise e
            else:
                return False

    def is_M_mass_balanced(
        self, x: Optional[Iterable[float]] = None, raise_exception: bool = False
    ) -> bool:
        """Test whether the M-matrix can be mass balanced (considering the growth rate).

        Parameters
        ----------
            x: Iterable[float]
                Assigned values for all the model parameters.
            raise_exception : bool
                A flag indicating whether to raise an exception if the model is not mass-balanced
                (otherwise, the function simply returns False).

        Returns
        -------
            is_M_mass_balanced : bool
                True iff the model is mass-balanced

        Notes
        -----

        This function checks whether there exists a pool size vector (s) which satisfies the
        mass-balance constraints.

        .. math::
            \\exists \\mathbf{s} \\quad \\text{such that} \\quad \\mathbf{s}^\\top
            (\\mathbf{M} + \\mu \\mathbf{I}_n) \\leq \\mathbf{0}_n

        This is equivalent to checking that the abscissa of the M-matrix
        (the largest eigenvalue, remember that all the eigenvalues of M are negative)
        is smaller or equal to -mu (minus the growth rate).

        """
        try:
            assert self.abscissa(x) <= -self.growth_rate, "M cannot be mass-balanced"
            return True
        except AssertionError as e:
            if raise_exception:
                raise e
            else:
                return False

    def reduce(
        self, states_to_remove: Union[int, Iterable[int]]
    ) -> "SymbolicCompartmentalModel":
        """Reduce the model by removing a strict subset of its states.

        Parameters
        ----------
            states_to_remove : Iterable[int]
                the indices of the states that should be removed

        Returns
        -------
            reduced_model: SymbolicCompartmentalModel
                the reduced model

        """
        if isinstance(states_to_remove, int):
            states_to_remove = [states_to_remove]
        states_to_keep = list(set(range(self.n_states)).difference(states_to_remove))
        if len(states_to_keep) == 0:
            raise ValueError("Cannot remove all of the states")

        reduced_model = SymbolicCompartmentalModel(len(states_to_keep), self.n_params)
        reduced_model._growth_rate = self.growth_rate
        reduced_model._p0 = self._p0.copy()
        reduced_model._lbs = self._lbs.copy()
        reduced_model._ubs = self._ubs.copy()
        for i_new, i_old in enumerate(states_to_keep):
            reduced_model._observed_pool_weights[i_new] = self._observed_pool_weights[i_old]
            for j_new, j_old in enumerate(states_to_keep):
                reduced_model._contributed_turnover_matrix[i_new, j_new] = self._contributed_turnover_matrix[i_old, j_old]
        return reduced_model

    @staticmethod
    def estimate_mean_age_trapezoid(
        tdata: np.ndarray,
        ydata: np.ndarray,
        semilogy: bool = True,
        extrapolate: bool = True,
        ax: Optional[plt.Axes] = None,
    ) -> float:
        """Estimate the mean age using the numerical approximation.

        Parameters
        ----------
            tdata : np.ndarray
                The time series.
            ydata : np.ndarray
                The target values of the labeling curve.
            semilogy : bool
                A flag for using logscale on the y-axis
            extrapolate : bool
                A flag for using extrapolation beyond the last time point
            ax : plt.Axes, optional
                The axes on which to plot the data.

        """
        N = tdata.size
        if N < 2:
            raise ValueError(
                "The labeling data must have at least 2 time points (including t=0)"
            )

        if ax is not None:
            ax.plot(tdata, ydata, ".", color="black")
            if semilogy:
                ax.set_yscale("log")

        # define the range of time points for plotting
        area = 0.0
        t_fin = None
        f_range = None
        for j in range(N - 1):
            ti, tj = tdata[j: j + 2]
            fi, fj = ydata[j: j + 2]

            t_fin = tj
            if extrapolate and (j == N - 2):
                # if extrapolate is true and we reached the final trapezoid,
                # extend it all the way to f = 0 to create a triangle
                if semilogy:
                    area += fi * (tj - ti) / np.log(fi / fj)
                    t_fin = tj + 4 * (tj - ti) / np.log(fi / fj)
                else:
                    area += fi ** 2 * (tj - ti) / (fi - fj) / 2
                    t_fin = tj + (tj - ti) / (fi / fj - 1)
            else:
                if semilogy:
                    area += (fi - fj) * (tj - ti) / np.log(fi / fj)
                else:
                    area += (fi ** 2 - fj ** 2) * (tj - ti) / (fi - fj) / 2

            if ax is not None:
                # these are not the last two points, so draw the trapezoid
                # defined by them and add its area to the sum
                if semilogy:
                    t_range = np.linspace(ti, t_fin, 25)
                    f_range = fi * (fj / fi) ** ((t_range - ti) / (tj - ti))
                    ax.set_ylim(f_range.min(), 1.02)
                else:
                    t_range = np.linspace(ti, t_fin, 2)
                    f_range = fi + (fj - fi) * ((t_range - ti) / (tj - ti))
                    ax.set_ylim(0, 1.02)

                ax.fill_between(t_range, 0, f_range, facecolor="orange", edgecolor="black")

        if ax is not None:
            ax.set_xlim(-t_fin * 0.02, t_fin * 1.02)
            ax.set_title(f"mean age estimate ~ {area:.2f}")
        return area

    @staticmethod
    def estimate_mean_residence_time_trapezoid(
        tdata: np.ndarray,
        ydata: np.ndarray,
        mu: float,
        semilogy: bool = True,
        extrapolate: bool = True,
        ax: Optional[plt.Axes] = None,
    ) -> float:
        """Estimate the mean residence time using numerical approximation.

        Parameters
        ---------
            tdata : np.ndarray
                The time series.
            ydata : np.ndarray
                The target values of the labeling curve.
            mu : float
                The system growth rate.
            semilogy : bool, optional
                A flag for using logscale on the y-axis (default: True)
            extrapolate : bool, optional
                A flag for using extrapolation beyond the last time
                point (default: True)
            ax : plt.Axes, optional
                The axes on which to plot the data.

        """
        N = tdata.size
        if N < 3:
            raise ValueError(
                "The labeling data must have at least 3 time points (including t=0)"
            )

        # we start by calculating the first derivative of f
        data = []
        for j in range(N - 1):
            ti, tj = tdata[j: j + 2]
            fi, fj = ydata[j: j + 2]

            t_mid = (ti + tj) / 2
            slope = (fj - fi) / (tj - ti)
            data.append({"time": t_mid, "fdot": slope})

        derivative_df = pd.DataFrame.from_records(data)

        # to find the slope at t=0, we assume f'' is constant in the range close to 0
        # and extrapolate f' back from the first two point
        t1, t2 = derivative_df.time[0:2]
        fdot1, fdot2 = derivative_df.fdot[0:2]
        fdot0 = (fdot1 * t2 - fdot2 * t1) / (t2 - t1)
        data = [{"time": 0.0, "fdot": fdot0}] + data
        derivative_df = pd.DataFrame.from_records(data).sort_values(by="time")

        # calculate the function for integration: g = -fdot(t) * e^{mu*t}
        derivative_df["g"] = derivative_df.fdot * np.exp(mu * derivative_df.time) / fdot0

        if ax is not None:
            ax.plot(derivative_df.time, derivative_df.g, ".", color="black")
            if semilogy:
                ax.set_yscale("log")

        # define the range of time points for plotting
        area = 0.0
        t_fin = None
        f_range = None
        for j in range(N - 1):
            ti, tj = derivative_df.time[j: j + 2]
            gi, gj = derivative_df.g[j: j + 2]
            t_fin = tj

            if extrapolate and (j == N - 2):
                # if extrapolate is true and we reached the final trapezoid,
                # extend it all the way to f = 0 to create a triangle
                if semilogy:
                    area += gi * (tj - ti) / np.log(gi / gj)
                    t_fin = tj + 4 * (tj - ti) / np.log(gi / gj)
                else:
                    area += gi ** 2 * (tj - ti) / (gi - gj) / 2
                    t_fin = tj + (tj - ti) / (gi / gj - 1)
            else:
                if semilogy:
                    area += (gi - gj) * (tj - ti) / np.log(gi / gj)
                else:
                    area += (gi ** 2 - gj ** 2) * (tj - ti) / (gi - gj) / 2

            if ax is not None:
                # these are not the last two points, so draw the trapezoid
                # defined by them and add its area to the sum
                if semilogy:
                    t_range = np.linspace(ti, t_fin, 25)
                    f_range = gi * (gj / gi) ** ((t_range - ti) / (tj - ti))
                else:
                    t_range = np.linspace(ti, t_fin, 2)
                    f_range = gi + (gj - gi) * ((t_range - ti) / (tj - ti))
                    ax.set_ylim(0, 1.02)

                ax.fill_between(t_range, 0, f_range, facecolor="orange", edgecolor="black")

        if ax is not None:
            ax.set_xlim(-t_fin * 0.02, t_fin * 1.02)
            ax.set_title(f"mean residence time estimate ~ {area:.2f}")
            if semilogy:
                ax.set_ylim(f_range.min(), 1.02)
            else:
                ax.set_ylim(0, 1.02)

        return -area / derivative_df.fdot.iat[0]
