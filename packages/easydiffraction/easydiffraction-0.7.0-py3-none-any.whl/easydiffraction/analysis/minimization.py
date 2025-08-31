# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import numpy as np

from easydiffraction.analysis.calculators.calculator_base import CalculatorBase
from easydiffraction.core.objects import Parameter
from easydiffraction.experiments.experiments import Experiments
from easydiffraction.sample_models.sample_models import SampleModels

from ..analysis.reliability_factors import get_reliability_inputs
from .minimizers.minimizer_base import FitResults
from .minimizers.minimizer_factory import MinimizerFactory


class DiffractionMinimizer:
    """
    Handles the fitting workflow using a pluggable minimizer.
    """

    def __init__(self, selection: str = 'lmfit (leastsq)') -> None:
        self.selection: str = selection
        self.engine: str = selection.split(' ')[0]  # Extracts 'lmfit' or 'dfols'
        self.minimizer = MinimizerFactory.create_minimizer(selection)
        self.results: Optional[FitResults] = None

    def fit(
        self,
        sample_models: SampleModels,
        experiments: Experiments,
        calculator: Any,
        weights: Optional[np.array] = None,
    ) -> None:
        """
        Run the fitting process.

        Args:
            sample_models: Collection of sample models.
            experiments: Collection of experiments.
            calculator: The calculator to use for pattern generation.
            weights: Optional weights for joint fitting.

        """
        params = sample_models.get_free_params() + experiments.get_free_params()

        if not params:
            print('⚠️ No parameters selected for fitting.')
            return None

        for param in params:
            param.start_value = param.value

        def objective_function(engine_params: Dict[str, Any]) -> np.ndarray:
            return self._residual_function(
                engine_params=engine_params,
                parameters=params,
                sample_models=sample_models,
                experiments=experiments,
                calculator=calculator,
                weights=weights,
            )

        # Perform fitting
        self.results = self.minimizer.fit(params, objective_function)

        # Post-fit processing
        self._process_fit_results(sample_models, experiments, calculator)

    def _process_fit_results(
        self,
        sample_models: SampleModels,
        experiments: Experiments,
        calculator: CalculatorBase,
    ) -> None:
        """
        Collect reliability inputs and display results after fitting.

        Args:
            sample_models: Collection of sample models.
            experiments: Collection of experiments.
            calculator: The calculator used for pattern generation.
        """
        y_obs, y_calc, y_err = get_reliability_inputs(
            sample_models,
            experiments,
            calculator,
        )

        # Placeholder for future f_obs / f_calc retrieval
        f_obs, f_calc = None, None

        if self.results:
            self.results.display_results(
                y_obs=y_obs,
                y_calc=y_calc,
                y_err=y_err,
                f_obs=f_obs,
                f_calc=f_calc,
            )

    def _collect_free_parameters(
        self,
        sample_models: SampleModels,
        experiments: Experiments,
    ) -> List[Parameter]:
        """
        Collect free parameters from sample models and experiments.

        Args:
            sample_models: Collection of sample models.
            experiments: Collection of experiments.

        Returns:
            List of free parameters.
        """
        free_params: List[Parameter] = sample_models.get_free_params() + experiments.get_free_params()
        return free_params

    def _residual_function(
        self,
        engine_params: Dict[str, Any],
        parameters: List[Parameter],
        sample_models: SampleModels,
        experiments: Experiments,
        calculator: CalculatorBase,
        weights: Optional[np.array] = None,
    ) -> np.ndarray:
        """
        Residual function computes the difference between measured and calculated patterns.
        It updates the parameter values according to the optimizer-provided engine_params.

        Args:
            engine_params: Engine-specific parameter dict.
            parameters: List of parameters being optimized.
            sample_models: Collection of sample models.
            experiments: Collection of experiments.
            calculator: The calculator to use for pattern generation.
            weights: Optional weights for joint fitting.

        Returns:
            Array of weighted residuals.
        """
        # Sync parameters back to objects
        self.minimizer._sync_result_to_parameters(parameters, engine_params)

        # Prepare weights for joint fitting
        num_expts: int = len(experiments.ids)
        if weights is None:
            _weights = np.ones(num_expts)
        else:
            _weights_list: List[float] = []
            for id in experiments.ids:
                _weight = weights._items[id].weight.value
                _weights_list.append(_weight)
            _weights = np.array(_weights_list, dtype=np.float64)

        # Normalize weights so they sum to num_expts
        # We should obtain the same reduced chi_squared when a single dataset is split into
        # two parts and fit together. If weights sum to one, then reduced chi_squared
        # will be half as large as expected.
        _weights *= num_expts / np.sum(_weights)
        residuals: List[float] = []

        for (expt_id, experiment), weight in zip(experiments._items.items(), _weights):
            # Calculate the difference between measured and calculated patterns
            y_calc: np.ndarray = calculator.calculate_pattern(
                sample_models,
                experiment,
                called_by_minimizer=True,
            )
            y_meas: np.ndarray = experiment.datastore.pattern.meas
            y_meas_su: np.ndarray = experiment.datastore.pattern.meas_su
            diff = (y_meas - y_calc) / y_meas_su

            # Residuals are squared before going into reduced chi-squared
            diff *= np.sqrt(weight)

            # Append the residuals for this experiment
            residuals.extend(diff)

        return self.minimizer.tracker.track(np.array(residuals), parameters)
