# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any
from typing import Dict
from typing import List

import numpy as np
from dfols import solve

from .minimizer_base import MinimizerBase

DEFAULT_MAX_ITERATIONS = 1000


class DfolsMinimizer(MinimizerBase):
    """
    Minimizer using the DFO-LS package (Derivative-Free Optimization for Least-Squares).
    """

    def __init__(
        self,
        name: str = 'dfols',
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        **kwargs: Any,
    ) -> None:
        super().__init__(name=name, method=None, max_iterations=max_iterations)

    def _prepare_solver_args(self, parameters: List[Any]) -> Dict[str, Any]:
        x0 = []
        bounds_lower = []
        bounds_upper = []
        for param in parameters:
            x0.append(param.value)
            bounds_lower.append(param.min if param.min is not None else -np.inf)
            bounds_upper.append(param.max if param.max is not None else np.inf)
        bounds = (np.array(bounds_lower), np.array(bounds_upper))
        return {'x0': np.array(x0), 'bounds': bounds}

    def _run_solver(self, objective_function: Any, **kwargs: Any) -> Any:
        x0 = kwargs.get('x0')
        bounds = kwargs.get('bounds')
        return solve(objective_function, x0=x0, bounds=bounds, maxfun=self.max_iterations)

    def _sync_result_to_parameters(
        self,
        parameters: List[Any],
        raw_result: Any,
    ) -> None:
        """
        Synchronizes the result from the solver to the parameters.

        Args:
            parameters: List of parameters being optimized.
            raw_result: The result object returned by the solver.
        """
        # Ensure compatibility with raw_result coming from dfols.solve()
        if hasattr(raw_result, 'x'):
            result_values = raw_result.x
        else:
            result_values = raw_result  # fallback for raw_result being directly a list/array

        for i, param in enumerate(parameters):
            param.value = result_values[i]
            # DFO-LS doesn't provide uncertainties; set to None or calculate later if needed
            param.uncertainty = None

    def _check_success(self, raw_result: Any) -> bool:
        """
        Determines success from DFO-LS result dictionary.

        Args:
            raw_result: The result object returned by the solver.

        Returns:
            True if the optimization was successful, False otherwise.
        """
        return raw_result.flag == raw_result.EXIT_SUCCESS
