# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

import numpy as np

from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.utils import render_table

from ..reliability_factors import calculate_r_factor
from ..reliability_factors import calculate_r_factor_squared
from ..reliability_factors import calculate_rb_factor
from ..reliability_factors import calculate_weighted_r_factor
from .fitting_progress_tracker import FittingProgressTracker


class FitResults:
    def __init__(
        self,
        success: bool = False,
        parameters: Optional[List[Any]] = None,
        chi_square: Optional[float] = None,
        reduced_chi_square: Optional[float] = None,
        message: str = '',
        iterations: int = 0,
        engine_result: Optional[Any] = None,
        starting_parameters: Optional[List[Any]] = None,
        fitting_time: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        self.success: bool = success
        self.parameters: List[Any] = parameters if parameters is not None else []
        self.chi_square: Optional[float] = chi_square
        self.reduced_chi_square: Optional[float] = reduced_chi_square
        self.message: str = message
        self.iterations: int = iterations
        self.engine_result: Optional[Any] = engine_result
        self.result: Optional[Any] = None
        self.starting_parameters: List[Any] = starting_parameters if starting_parameters is not None else []
        self.fitting_time: Optional[float] = fitting_time

        if 'redchi' in kwargs and self.reduced_chi_square is None:
            self.reduced_chi_square = kwargs.get('redchi')

        for key, value in kwargs.items():
            setattr(self, key, value)

    def display_results(
        self,
        y_obs: Optional[List[float]] = None,
        y_calc: Optional[List[float]] = None,
        y_err: Optional[List[float]] = None,
        f_obs: Optional[List[float]] = None,
        f_calc: Optional[List[float]] = None,
    ) -> None:
        status_icon = '✅' if self.success else '❌'
        rf = rf2 = wr = br = None
        if y_obs is not None and y_calc is not None:
            rf = calculate_r_factor(y_obs, y_calc) * 100
            rf2 = calculate_r_factor_squared(y_obs, y_calc) * 100
        if y_obs is not None and y_calc is not None and y_err is not None:
            wr = calculate_weighted_r_factor(y_obs, y_calc, y_err) * 100
        if f_obs is not None and f_calc is not None:
            br = calculate_rb_factor(f_obs, f_calc) * 100

        print(paragraph('Fit results'))
        print(f'{status_icon} Success: {self.success}')
        print(f'⏱️ Fitting time: {self.fitting_time:.2f} seconds')
        print(f'📏 Goodness-of-fit (reduced χ²): {self.reduced_chi_square:.2f}')
        if rf is not None:
            print(f'📏 R-factor (Rf): {rf:.2f}%')
        if rf2 is not None:
            print(f'📏 R-factor squared (Rf²): {rf2:.2f}%')
        if wr is not None:
            print(f'📏 Weighted R-factor (wR): {wr:.2f}%')
        if br is not None:
            print(f'📏 Bragg R-factor (BR): {br:.2f}%')
        print('📈 Fitted parameters:')

        headers = [
            'datablock',
            'category',
            'entry',
            'parameter',
            'start',
            'fitted',
            'uncertainty',
            'units',
            'change',
        ]
        alignments = [
            'left',
            'left',
            'left',
            'left',
            'right',
            'right',
            'right',
            'left',
            'right',
        ]

        rows = []
        for param in self.parameters:
            datablock_id = getattr(param, 'datablock_id', 'N/A')
            category_key = getattr(param, 'category_key', 'N/A')
            collection_entry_id = getattr(param, 'collection_entry_id', 'N/A')
            name = getattr(param, 'name', 'N/A')
            start = f'{getattr(param, "start_value", "N/A"):.4f}' if param.start_value is not None else 'N/A'
            fitted = f'{param.value:.4f}' if param.value is not None else 'N/A'
            uncertainty = f'{param.uncertainty:.4f}' if param.uncertainty is not None else 'N/A'
            units = getattr(param, 'units', 'N/A')

            if param.start_value and param.value:
                change = ((param.value - param.start_value) / param.start_value) * 100
                arrow = '↑' if change > 0 else '↓'
                relative_change = f'{abs(change):.2f} % {arrow}'
            else:
                relative_change = 'N/A'

            rows.append(
                [datablock_id, category_key, collection_entry_id, name, start, fitted, uncertainty, units, relative_change]
            )

        render_table(
            columns_headers=headers,
            columns_alignment=alignments,
            columns_data=rows,
            show_index=True,
        )


class MinimizerBase(ABC):
    """
    Abstract base class for minimizer implementations.
    Provides shared logic and structure for concrete minimizers.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        method: Optional[str] = None,
        max_iterations: Optional[int] = None,
    ) -> None:
        self.name: Optional[str] = name
        self.method: Optional[str] = method
        self.max_iterations: Optional[int] = max_iterations
        self.result: Optional[FitResults] = None
        self._previous_chi2: Optional[float] = None
        self._iteration: Optional[int] = None
        self._best_chi2: Optional[float] = None
        self._best_iteration: Optional[int] = None
        self._fitting_time: Optional[float] = None
        self.tracker: FittingProgressTracker = FittingProgressTracker()

    def _start_tracking(self, minimizer_name: str) -> None:
        self.tracker.reset()
        self.tracker.start_tracking(minimizer_name)
        self.tracker.start_timer()

    def _stop_tracking(self) -> None:
        self.tracker.stop_timer()
        self.tracker.finish_tracking()

    @abstractmethod
    def _prepare_solver_args(self, parameters: List[Any]) -> Dict[str, Any]:
        """
        Prepare the solver arguments directly from the list of free parameters.
        """
        pass

    @abstractmethod
    def _run_solver(
        self,
        objective_function: Callable[..., Any],
        engine_parameters: Dict[str, Any],
    ) -> Any:
        pass

    @abstractmethod
    def _sync_result_to_parameters(
        self,
        raw_result: Any,
        parameters: List[Any],
    ) -> None:
        pass

    def _finalize_fit(
        self,
        parameters: List[Any],
        raw_result: Any,
    ) -> FitResults:
        self._sync_result_to_parameters(parameters, raw_result)
        success = self._check_success(raw_result)
        self.result = FitResults(
            success=success,
            parameters=parameters,
            reduced_chi_square=self.tracker.best_chi2,
            engine_result=raw_result,
            starting_parameters=parameters,
            fitting_time=self.tracker.fitting_time,
        )
        return self.result

    @abstractmethod
    def _check_success(self, raw_result: Any) -> bool:
        """
        Determine whether the fit was successful.
        This must be implemented by concrete minimizers.
        """
        pass

    def fit(
        self,
        parameters: List[Any],
        objective_function: Callable[..., Any],
    ) -> FitResults:
        minimizer_name = self.name or 'Unnamed Minimizer'
        if self.method is not None:
            minimizer_name += f' ({self.method})'

        self._start_tracking(minimizer_name)

        solver_args = self._prepare_solver_args(parameters)
        raw_result = self._run_solver(objective_function, **solver_args)

        self._stop_tracking()

        result = self._finalize_fit(parameters, raw_result)

        return result

    def _objective_function(
        self,
        engine_params: Dict[str, Any],
        parameters: List[Any],
        sample_models: Any,
        experiments: Any,
        calculator: Any,
    ) -> np.ndarray:
        return self._compute_residuals(
            engine_params,
            parameters,
            sample_models,
            experiments,
            calculator,
        )

    def _create_objective_function(
        self,
        parameters: List[Any],
        sample_models: Any,
        experiments: Any,
        calculator: Any,
    ) -> Callable[[Dict[str, Any]], np.ndarray]:
        return lambda engine_params: self._objective_function(
            engine_params,
            parameters,
            sample_models,
            experiments,
            calculator,
        )
