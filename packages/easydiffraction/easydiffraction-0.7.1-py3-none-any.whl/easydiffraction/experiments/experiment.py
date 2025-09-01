# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from abc import abstractmethod
from typing import List
from typing import Optional

import numpy as np

from easydiffraction.core.constants import DEFAULT_BACKGROUND_TYPE
from easydiffraction.core.constants import DEFAULT_BEAM_MODE
from easydiffraction.core.constants import DEFAULT_PEAK_PROFILE_TYPE
from easydiffraction.core.constants import DEFAULT_RADIATION_PROBE
from easydiffraction.core.constants import DEFAULT_SAMPLE_FORM
from easydiffraction.core.constants import DEFAULT_SCATTERING_TYPE
from easydiffraction.core.objects import Datablock
from easydiffraction.experiments.collections.background import BackgroundFactory
from easydiffraction.experiments.collections.datastore import DatastoreFactory
from easydiffraction.experiments.collections.excluded_regions import ExcludedRegions
from easydiffraction.experiments.collections.linked_phases import LinkedPhases
from easydiffraction.experiments.components.experiment_type import ExperimentType
from easydiffraction.experiments.components.instrument import InstrumentBase
from easydiffraction.experiments.components.instrument import InstrumentFactory
from easydiffraction.experiments.components.peak import PeakFactory
from easydiffraction.utils.decorators import enforce_type
from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.formatting import warning
from easydiffraction.utils.utils import render_cif
from easydiffraction.utils.utils import render_table


class InstrumentMixin:
    def __init__(self, *args, **kwargs):
        expt_type = kwargs.get('type')
        super().__init__(*args, **kwargs)
        self._instrument = InstrumentFactory.create(
            scattering_type=expt_type.scattering_type.value,
            beam_mode=expt_type.beam_mode.value,
        )

    @property
    def instrument(self):
        return self._instrument

    @instrument.setter
    @enforce_type
    def instrument(self, new_instrument: InstrumentBase):
        self._instrument = new_instrument


class BaseExperiment(Datablock):
    """
    Base class for all experiments with only core attributes.
    Wraps experiment type, instrument and datastore.
    """

    # TODO: Find better name for the attribute 'type'.
    #  1. It shadows the built-in type() function.
    #  2. It is not very clear what it refers to.
    def __init__(self, name: str, type: ExperimentType):
        self.name = name
        self.type = type
        self.datastore = DatastoreFactory.create(
            sample_form=self.type.sample_form.value,
            experiment=self,
        )

    # ---------------------------
    # Name (ID) of the experiment
    # ---------------------------

    @property
    def name(self):
        return self._name

    @name.setter
    @enforce_type
    def name(self, new_name: str):
        self._name = new_name

    # ---------------
    # Experiment type
    # ---------------

    @property
    def type(self):
        return self._type

    @type.setter
    @enforce_type
    def type(self, new_experiment_type: ExperimentType):
        self._type = new_experiment_type

    # ----------------
    # Misc. Need to be sorted
    # ----------------

    def as_cif(
        self,
        max_points: Optional[int] = None,
    ) -> str:
        """
        Export the sample model to CIF format.
        Returns:
            str: CIF string representation of the experiment.
        """
        # Data block header
        cif_lines: List[str] = [f'data_{self.name}']

        # Experiment type
        cif_lines += ['', self.type.as_cif()]

        # Instrument setup and calibration
        if hasattr(self, 'instrument'):
            cif_lines += ['', self.instrument.as_cif()]

        # Peak profile, broadening and asymmetry
        if hasattr(self, 'peak'):
            cif_lines += ['', self.peak.as_cif()]

        # Phase scale factors for powder experiments
        if hasattr(self, 'linked_phases') and self.linked_phases._items:
            cif_lines += ['', self.linked_phases.as_cif()]

        # Crystal scale factor for single crystal experiments
        if hasattr(self, 'linked_crystal'):
            cif_lines += ['', self.linked_crystal.as_cif()]

        # Background points
        if hasattr(self, 'background') and self.background._items:
            cif_lines += ['', self.background.as_cif()]

        # Excluded regions
        if hasattr(self, 'excluded_regions') and self.excluded_regions._items:
            cif_lines += ['', self.excluded_regions.as_cif()]

        # Measured data
        if hasattr(self, 'datastore') and hasattr(self.datastore, 'pattern'):
            cif_lines.append('')
            cif_lines.append('loop_')
            category = '_pd_meas'  # TODO: Add category to pattern component
            attributes = ('2theta_scan', 'intensity_total', 'intensity_total_su')
            for attribute in attributes:
                cif_lines.append(f'{category}.{attribute}')
            pattern = self.datastore.pattern
            if max_points is not None and len(pattern.x) > 2 * max_points:
                for i in range(max_points):
                    x = pattern.x[i]
                    meas = pattern.meas[i]
                    meas_su = pattern.meas_su[i]
                    cif_lines.append(f'{x} {meas} {meas_su}')
                cif_lines.append('...')
                for i in range(-max_points, 0):
                    x = pattern.x[i]
                    meas = pattern.meas[i]
                    meas_su = pattern.meas_su[i]
                    cif_lines.append(f'{x} {meas} {meas_su}')
            else:
                for x, meas, meas_su in zip(pattern.x, pattern.meas, pattern.meas_su):
                    cif_lines.append(f'{x} {meas} {meas_su}')

        return '\n'.join(cif_lines)

    def show_as_cif(self) -> None:
        cif_text: str = self.as_cif(max_points=5)
        paragraph_title: str = paragraph(f"Experiment 🔬 '{self.name}' as cif")
        render_cif(cif_text, paragraph_title)

    @abstractmethod
    def _load_ascii_data_to_experiment(self, data_path: str) -> None:
        pass


class BasePowderExperiment(BaseExperiment):
    """
    Base class for all powder experiments.
    """

    def __init__(
        self,
        name: str,
        type: ExperimentType,
    ) -> None:
        super().__init__(name=name, type=type)

        self._peak_profile_type: str = DEFAULT_PEAK_PROFILE_TYPE[self.type.scattering_type.value][self.type.beam_mode.value]
        self.peak = PeakFactory.create(
            scattering_type=self.type.scattering_type.value,
            beam_mode=self.type.beam_mode.value,
            profile_type=self._peak_profile_type,
        )

        self.linked_phases: LinkedPhases = LinkedPhases()
        self.excluded_regions: ExcludedRegions = ExcludedRegions(parent=self)

    @abstractmethod
    def _load_ascii_data_to_experiment(self, data_path: str) -> None:
        pass

    @property
    def peak_profile_type(self):
        return self._peak_profile_type

    @peak_profile_type.setter
    def peak_profile_type(self, new_type: str):
        if new_type not in PeakFactory._supported[self.type.scattering_type.value][self.type.beam_mode.value]:
            supported_types = list(PeakFactory._supported[self.type.scattering_type.value][self.type.beam_mode.value].keys())
            print(warning(f"Unsupported peak profile '{new_type}'"))
            print(f'Supported peak profiles: {supported_types}')
            print("For more information, use 'show_supported_peak_profile_types()'")
            return
        self.peak = PeakFactory.create(
            scattering_type=self.type.scattering_type.value, beam_mode=self.type.beam_mode.value, profile_type=new_type
        )
        self._peak_profile_type = new_type
        print(paragraph(f"Peak profile type for experiment '{self.name}' changed to"))
        print(new_type)

    def show_supported_peak_profile_types(self):
        columns_headers = ['Peak profile type', 'Description']
        columns_alignment = ['left', 'left']
        columns_data = []
        for name, config in PeakFactory._supported[self.type.scattering_type.value][self.type.beam_mode.value].items():
            description = getattr(config, '_description', 'No description provided.')
            columns_data.append([name, description])

        print(paragraph('Supported peak profile types'))
        render_table(columns_headers=columns_headers, columns_alignment=columns_alignment, columns_data=columns_data)

    def show_current_peak_profile_type(self):
        print(paragraph('Current peak profile type'))
        print(self.peak_profile_type)


class PowderExperiment(
    InstrumentMixin,
    BasePowderExperiment,
):
    """
    Powder experiment class with specific attributes.
    Wraps background, peak profile, and linked phases.
    """

    def __init__(
        self,
        name: str,
        type: ExperimentType,
    ) -> None:
        super().__init__(name=name, type=type)

        self._background_type: str = DEFAULT_BACKGROUND_TYPE
        self.background = BackgroundFactory.create(background_type=self.background_type)

    # -------------
    # Measured data
    # -------------

    def _load_ascii_data_to_experiment(self, data_path: str) -> None:
        """
        Loads x, y, sy values from an ASCII data file into the experiment.

        The file must be structured as:
            x  y  sy
        """
        try:
            data = np.loadtxt(data_path)
        except Exception as e:
            raise IOError(f'Failed to read data from {data_path}: {e}')

        if data.shape[1] < 2:
            raise ValueError('Data file must have at least two columns: x and y.')

        if data.shape[1] < 3:
            print('Warning: No uncertainty (sy) column provided. Defaulting to sqrt(y).')

        # Extract x, y data
        x: np.ndarray = data[:, 0]
        y: np.ndarray = data[:, 1]

        # Round x to 4 decimal places
        # TODO: This is needed for CrysPy, as otherwise it fails to match
        #  the size of the data arrays.
        x = np.round(x, 4)

        # Determine sy from column 3 if available, otherwise use sqrt(y)
        sy: np.ndarray = data[:, 2] if data.shape[1] > 2 else np.sqrt(y)

        # Replace values smaller than 0.0001 with 1.0
        # TODO: This is needed for minimization algorithms that fail with
        #  very small or zero uncertainties.
        sy = np.where(sy < 0.0001, 1.0, sy)

        # Attach the data to the experiment's datastore

        # The full pattern data
        self.datastore.pattern.full_x = x
        self.datastore.pattern.full_meas = y
        self.datastore.pattern.full_meas_su = sy

        # The pattern data used for fitting (without excluded points)
        # This is the same as full_x, full_meas, full_meas_su by default
        self.datastore.pattern.x = x
        self.datastore.pattern.meas = y
        self.datastore.pattern.meas_su = sy

        # Excluded mask
        # No excluded points by default
        self.datastore.pattern.excluded = np.full(x.shape, fill_value=False, dtype=bool)

        print(paragraph('Data loaded successfully'))
        print(f"Experiment 🔬 '{self.name}'. Number of data points: {len(x)}")

    @property
    def background_type(self):
        return self._background_type

    @background_type.setter
    def background_type(self, new_type):
        if new_type not in BackgroundFactory._supported:
            supported_types = list(BackgroundFactory._supported.keys())
            print(warning(f"Unknown background type '{new_type}'"))
            print(f'Supported background types: {supported_types}')
            print("For more information, use 'show_supported_background_types()'")
            return
        self.background = BackgroundFactory.create(new_type)
        self._background_type = new_type
        print(paragraph(f"Background type for experiment '{self.name}' changed to"))
        print(new_type)

    def show_supported_background_types(self):
        columns_headers = ['Background type', 'Description']
        columns_alignment = ['left', 'left']
        columns_data = []
        for name, config in BackgroundFactory._supported.items():
            description = getattr(config, '_description', 'No description provided.')
            columns_data.append([name, description])

        print(paragraph('Supported background types'))
        render_table(columns_headers=columns_headers, columns_alignment=columns_alignment, columns_data=columns_data)

    def show_current_background_type(self):
        print(paragraph('Current background type'))
        print(self.background_type)


# TODO: Refactor this class to reuse PowderExperiment
# TODO: This is not a specific experiment, but rather processed data from
#  PowderExperiment. So, we should think of a better design.
class PairDistributionFunctionExperiment(BasePowderExperiment):
    """PDF experiment class with specific attributes."""

    def __init__(
        self,
        name: str,
        type: ExperimentType,
    ):
        super().__init__(name=name, type=type)

    def _load_ascii_data_to_experiment(self, data_path):
        """
        Loads x, y, sy values from an ASCII data file into the experiment.

        The file must be structured as:
            x  y  sy
        """
        try:
            from diffpy.utils.parsers.loaddata import loadData
        except ImportError:
            raise ImportError('diffpy module not found.')
        try:
            data = loadData(data_path)
        except Exception as e:
            raise IOError(f'Failed to read data from {data_path}: {e}')

        if data.shape[1] < 2:
            raise ValueError('Data file must have at least two columns: x and y.')

        default_sy = 0.03
        if data.shape[1] < 3:
            print(f'Warning: No uncertainty (sy) column provided. Defaulting to {default_sy}.')

        # Extract x, y, and sy data
        x = data[:, 0]
        # We should also add sx = data[:, 2] to capture the e.s.d. of x. It
        # might be useful in future.
        y = data[:, 1]
        # Using sqrt isn’t appropriate here, as the y-scale isn’t raw counts
        # and includes both positive and negative values. For now, set the
        # e.s.d. to a fixed value of 0.03 if it’s not included in the measured
        # data file. We should improve this later.
        # sy = data[:, 3] if data.shape[1] > 2 else np.sqrt(y)
        sy = data[:, 2] if data.shape[1] > 2 else np.full_like(y, fill_value=default_sy)

        # Attach the data to the experiment's datastore
        self.datastore.pattern.x = x
        self.datastore.pattern.meas = y
        self.datastore.pattern.meas_su = sy

        print(paragraph('Data loaded successfully'))
        print(f"Experiment 🔬 '{self.name}'. Number of data points: {len(x)}")


class SingleCrystalExperiment(BaseExperiment):
    """Single crystal experiment class with specific attributes."""

    def __init__(
        self,
        name: str,
        type: ExperimentType,
    ) -> None:
        super().__init__(name=name, type=type)
        self.linked_crystal = None

    def show_meas_chart(self) -> None:
        print('Showing measured data chart is not implemented yet.')


class ExperimentFactory:
    """Creates Experiment instances with only relevant attributes."""

    _supported = {
        'bragg': {
            'powder': PowderExperiment,
            'single crystal': SingleCrystalExperiment,
        },
        'total': {
            'powder': PairDistributionFunctionExperiment,
        },
    }

    @classmethod
    def create(
        cls,
        name: str,
        sample_form: DEFAULT_SAMPLE_FORM,
        beam_mode: DEFAULT_BEAM_MODE,
        radiation_probe: DEFAULT_RADIATION_PROBE,
        scattering_type: DEFAULT_SCATTERING_TYPE,
    ) -> BaseExperiment:
        # TODO: Add checks for expt_type and expt_class
        expt_type = ExperimentType(
            sample_form=sample_form,
            beam_mode=beam_mode,
            radiation_probe=radiation_probe,
            scattering_type=scattering_type,
        )

        expt_class = cls._supported[scattering_type][sample_form]
        expt_obj = expt_class(
            name=name,
            type=expt_type,
        )

        return expt_obj


# User exposed API for convenience
# TODO: Refactor based on the implementation of method add() in class Experiments
# TODO: Think of where to keep default values for sample_form, beam_mode, radiation_probe, as they are also defined in the
#  class ExperimentType
def Experiment(
    name: str,
    sample_form: str = DEFAULT_SAMPLE_FORM,
    beam_mode: str = DEFAULT_BEAM_MODE,
    radiation_probe: str = DEFAULT_RADIATION_PROBE,
    scattering_type: str = DEFAULT_SCATTERING_TYPE,
    data_path: str = None,
):
    experiment = ExperimentFactory.create(
        name=name,
        sample_form=sample_form,
        beam_mode=beam_mode,
        radiation_probe=radiation_probe,
        scattering_type=scattering_type,
    )
    if data_path:
        experiment._load_ascii_data_to_experiment(data_path)
    return experiment
