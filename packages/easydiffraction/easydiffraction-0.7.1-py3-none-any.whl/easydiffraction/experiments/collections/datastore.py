# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

if TYPE_CHECKING:
    from ..experiment import Experiment  # adjust path if needed

import numpy as np


class Pattern:
    """
    Base pattern class for both powder and single crystal experiments.
    Stores x, measured intensities, uncertainties, background, and calculated intensities.
    """

    def __init__(self, experiment: Experiment) -> None:
        self.experiment = experiment

        # Data arrays
        self.x: Optional[np.ndarray] = None
        self.d: Optional[np.ndarray] = None
        self.meas: Optional[np.ndarray] = None
        self.meas_su: Optional[np.ndarray] = None
        self.bkg: Optional[np.ndarray] = None
        self.excluded: Optional[np.ndarray] = None  # Flags for excluded points
        self._calc: Optional[np.ndarray] = None  # Cached calculated intensities

    @property
    def calc(self) -> Optional[np.ndarray]:
        """Access calculated intensities. Should be updated via external calculation."""
        return self._calc

    @calc.setter
    def calc(self, values: np.ndarray) -> None:
        """Set calculated intensities (from Analysis.calculate_pattern())."""
        self._calc = values


class PowderPattern(Pattern):
    """
    Specialized pattern for powder diffraction (can be extended in the future).
    """

    # TODO: Check if this class is needed or if it can be merged with Pattern
    def __init__(self, experiment: Experiment) -> None:
        super().__init__(experiment)
        # Additional powder-specific initialization if needed


class Datastore:
    """
    Stores pattern data (measured and calculated) for an experiment.
    """

    def __init__(self, sample_form: str, experiment: Experiment) -> None:
        self.sample_form: str = sample_form

        if sample_form == 'powder':
            self.pattern: Pattern = PowderPattern(experiment)
        elif sample_form == 'single_crystal':
            self.pattern: Pattern = Pattern(experiment)  # TODO: Find better name for single crystal pattern
        else:
            raise ValueError(f"Unknown sample form '{sample_form}'")

    def load_measured_data(self, file_path: str) -> None:
        """Load measured data from an ASCII file."""
        # TODO: Check if this method is used...
        #  Looks like _load_ascii_data_to_experiment from experiments.py is used instead
        print(f'Loading measured data for {self.sample_form} diffraction from {file_path}')

        try:
            data: np.ndarray = np.loadtxt(file_path)
        except Exception as e:
            print(f'Failed to load data: {e}')
            return

        if data.shape[1] < 2:
            raise ValueError('Data file must have at least two columns (x and y).')

        x: np.ndarray = data[:, 0]
        y: np.ndarray = data[:, 1]
        sy: np.ndarray = data[:, 2] if data.shape[1] > 2 else np.sqrt(np.abs(y))

        self.pattern.x = x
        self.pattern.meas = y
        self.pattern.meas_su = sy
        self.pattern.excluded = np.full(x.shape, fill_value=False, dtype=bool)  # No excluded points by default

        print(f"Loaded {len(x)} points for experiment '{self.pattern.experiment.name}'.")

    def show_measured_data(self) -> None:
        """Display measured data in console."""
        print(f'\nMeasured data ({self.sample_form}):')
        print(f'x: {self.pattern.x}')
        print(f'meas: {self.pattern.meas}')
        print(f'meas_su: {self.pattern.meas_su}')

    def show_calculated_data(self) -> None:
        """Display calculated data in console."""
        print(f'\nCalculated data ({self.sample_form}):')
        print(f'calc: {self.pattern.calc}')


class DatastoreFactory:
    """
    Factory to dynamically create appropriate datastore instances (SC/Powder).
    """

    @staticmethod
    def create(sample_form: str, experiment: Experiment) -> Datastore:
        """
        Create a datastore object depending on the sample form.

        Args:
            sample_form: The form of the sample ("powder" or "single_crystal").
            experiment: The experiment object.

        Returns:
            A new Datastore instance appropriate for the sample form.
        """
        return Datastore(sample_form, experiment)
