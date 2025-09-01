# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import List

import numpy as np

from easydiffraction.core.singletons import ConstraintsHandler
from easydiffraction.experiments.experiment import Experiment
from easydiffraction.sample_models.sample_model import SampleModel
from easydiffraction.sample_models.sample_models import SampleModels


class CalculatorBase(ABC):
    """
    Base API for diffraction calculation engines.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def engine_imported(self) -> bool:
        pass

    @abstractmethod
    def calculate_structure_factors(
        self,
        sample_model: SampleModel,
        experiment: Experiment,
    ) -> None:
        """
        Calculate structure factors for a single sample model and experiment.
        """
        pass

    def calculate_pattern(
        self,
        sample_models: SampleModels,
        experiment: Experiment,
        called_by_minimizer: bool = False,
    ) -> np.ndarray:
        """
        Calculate the diffraction pattern for multiple sample models and a single experiment.

        Args:
            sample_models: Collection of sample models.
            experiment: The experiment object.
            called_by_minimizer: Whether the calculation is called by a minimizer.

        Returns:
            The calculated diffraction pattern as a NumPy array.
        """
        x_data = experiment.datastore.pattern.x
        y_calc_zeros = np.zeros_like(x_data)

        valid_linked_phases = self._get_valid_linked_phases(sample_models, experiment)

        # Apply user constraints to all sample models
        constraints = ConstraintsHandler.get()
        constraints.apply()

        # Calculate contributions from valid linked sample models
        y_calc_scaled = y_calc_zeros
        for linked_phase in valid_linked_phases:
            sample_model_id = linked_phase._entry_id
            sample_model_scale = linked_phase.scale.value
            sample_model = sample_models[sample_model_id]

            # Apply symmetry constraints
            sample_model.apply_symmetry_constraints()

            sample_model_y_calc = self._calculate_single_model_pattern(
                sample_model,
                experiment,
                called_by_minimizer=called_by_minimizer,
            )

            sample_model_y_calc_scaled = sample_model_scale * sample_model_y_calc
            y_calc_scaled += sample_model_y_calc_scaled

        # Calculate background contribution
        y_bkg = np.zeros_like(x_data)
        if hasattr(experiment, 'background'):
            y_bkg = experiment.background.calculate(x_data)
        experiment.datastore.pattern.bkg = y_bkg

        # Calculate total pattern
        y_calc_total = y_calc_scaled + y_bkg
        experiment.datastore.pattern.calc = y_calc_total

        return y_calc_total

    @abstractmethod
    def _calculate_single_model_pattern(
        self,
        sample_model: SampleModels,
        experiment: Experiment,
        called_by_minimizer: bool,
    ) -> np.ndarray:
        """
        Calculate the diffraction pattern for a single sample model and experiment.

        Args:
            sample_model: The sample model object.
            experiment: The experiment object.
            called_by_minimizer: Whether the calculation is called by a minimizer.

        Returns:
            The calculated diffraction pattern as a NumPy array.
        """
        pass

    def _get_valid_linked_phases(
        self,
        sample_models: SampleModels,
        experiment: Experiment,
    ) -> List[Any]:
        """
        Get valid linked phases from the experiment.

        Args:
            sample_models: Collection of sample models.
            experiment: The experiment object.

        Returns:
            A list of valid linked phases.
        """
        if not experiment.linked_phases:
            print('Warning: No linked phases found. Returning empty pattern.')
            return []

        valid_linked_phases = []
        for linked_phase in experiment.linked_phases:
            if linked_phase._entry_id not in sample_models.get_ids():
                print(f"Warning: Linked phase '{linked_phase.id.value}' not found in Sample Models {sample_models.get_ids()}")
                continue
            valid_linked_phases.append(linked_phase)

        if not valid_linked_phases:
            print('Warning: None of the linked phases found in Sample Models. Returning empty pattern.')

        return valid_linked_phases
