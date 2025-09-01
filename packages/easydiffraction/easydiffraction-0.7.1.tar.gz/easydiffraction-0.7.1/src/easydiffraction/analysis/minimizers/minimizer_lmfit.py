# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any
from typing import Dict
from typing import List

import lmfit

from .minimizer_base import MinimizerBase

DEFAULT_METHOD = 'leastsq'
DEFAULT_MAX_ITERATIONS = 1000


class LmfitMinimizer(MinimizerBase):
    """
    Minimizer using the lmfit package.
    """

    def __init__(
        self,
        name: str = 'lmfit',
        method: str = DEFAULT_METHOD,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
    ) -> None:
        super().__init__(
            name=name,
            method=method,
            max_iterations=max_iterations,
        )

    def _prepare_solver_args(
        self,
        parameters: List[Any],
    ) -> Dict[str, Any]:
        """
        Prepares the solver arguments for the lmfit minimizer.

        Args:
            parameters: List of parameters to be optimized.

        Returns:
            A dictionary containing the prepared lmfit.Parameters object.
        """
        engine_parameters = lmfit.Parameters()
        for param in parameters:
            engine_parameters.add(
                name=param.minimizer_uid,
                value=param.value,
                vary=param.free,
                min=param.min,
                max=param.max,
            )
        return {'engine_parameters': engine_parameters}

    def _run_solver(self, objective_function: Any, **kwargs: Any) -> Any:
        """
        Runs the lmfit solver.

        Args:
            objective_function: The objective function to minimize.
            **kwargs: Additional arguments for the solver.

        Returns:
            The result of the lmfit minimization.
        """
        engine_parameters = kwargs.get('engine_parameters')

        return lmfit.minimize(
            objective_function,
            params=engine_parameters,
            method=self.method,
            nan_policy='propagate',
            max_nfev=self.max_iterations,
        )

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
        if hasattr(raw_result, 'params'):
            param_values = raw_result.params
        else:
            param_values = raw_result  # fallback if params attribute is not present

        for param in parameters:
            param_result = param_values.get(param.minimizer_uid)
            if param_result is not None:
                param.value = param_result.value
                param.uncertainty = getattr(param_result, 'stderr', None)

    def _check_success(self, raw_result: Any) -> bool:
        """
        Determines success from lmfit MinimizerResult.

        Args:
            raw_result: The result object returned by the solver.

        Returns:
            True if the optimization was successful, False otherwise.
        """
        return getattr(raw_result, 'success', False)

    def _iteration_callback(
        self,
        params: lmfit.Parameters,
        iter: int,
        resid: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Callback function for each iteration of the minimizer.

        Args:
            params: The current parameters.
            iter: The current iteration number.
            resid: The residuals.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self._iteration = iter
