# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any
from typing import List
from typing import Optional

import numpy as np

from easydiffraction.experiments.experiment import Experiment
from easydiffraction.experiments.experiments import Experiments
from easydiffraction.sample_models.sample_models import SampleModels

from .calculators.calculator_factory import CalculatorFactory


class DiffractionCalculator:
    """
    Invokes calculation engines for pattern generation.
    """

    def __init__(self, engine: str = 'cryspy') -> None:
        """
        Initialize the DiffractionCalculator with a specified backend engine.

        Args:
            engine: Type of the calculation engine to use.
                    Supported types: 'crysfml', 'cryspy', 'pdffit'.
                    Default is 'cryspy'.
        """
        self.calculator_factory = CalculatorFactory()
        self._calculator = self.calculator_factory.create_calculator(engine)

    def set_calculator(self, engine: str) -> None:
        """
        Switch to a different calculator engine at runtime.

        Args:
            engine: New calculation engine type to use.
        """
        self._calculator = self.calculator_factory.create_calculator(engine)

    def calculate_structure_factors(
        self,
        sample_models: SampleModels,
        experiments: Experiments,
    ) -> Optional[List[Any]]:
        """
        Calculate HKL intensities (structure factors) for sample models and experiments.

        Args:
            sample_models: Collection of sample models.
            experiments: Collection of experiments.

        Returns:
            HKL intensities calculated by the backend calculator.
        """
        return self._calculator.calculate_structure_factors(sample_models, experiments)

    def calculate_pattern(
        self,
        sample_models: SampleModels,
        experiment: Experiment,
    ) -> np.ndarray:
        """
        Calculate diffraction pattern based on sample models and experiment.

        Args:
            sample_models: Collection of sample models.
            experiment: A single experiment object.

        Returns:
            Diffraction pattern calculated by the backend calculator.
        """
        return self._calculator.calculate_pattern(sample_models, experiment)
