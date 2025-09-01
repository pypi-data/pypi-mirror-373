# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any
from typing import Dict
from typing import List
from typing import Union

import numpy as np

from easydiffraction.experiments.experiment import Experiment
from easydiffraction.experiments.experiments import Experiments
from easydiffraction.sample_models.sample_models import SampleModel
from easydiffraction.sample_models.sample_models import SampleModels

from .calculator_base import CalculatorBase

try:
    from pycrysfml import cfml_py_utilities

    # TODO: Add the following print to debug mode
    # print("✅ 'pycrysfml' calculation engine is successfully imported.")
except ImportError:
    # TODO: Add the following print to debug mode
    # print("⚠️ 'pycrysfml' module not found. This calculation engine will not be available.")
    cfml_py_utilities = None


class CrysfmlCalculator(CalculatorBase):
    """
    Wrapper for Crysfml library.
    """

    engine_imported: bool = cfml_py_utilities is not None

    @property
    def name(self) -> str:
        return 'crysfml'

    def calculate_structure_factors(
        self,
        sample_models: SampleModels,
        experiments: Experiments,
    ) -> None:
        """
        Call Crysfml to calculate structure factors.

        Args:
            sample_models: The sample models to calculate structure factors for.
            experiments: The experiments associated with the sample models.
        """
        raise NotImplementedError('HKL calculation is not implemented for CrysfmlCalculator.')

    def _calculate_single_model_pattern(
        self,
        sample_model: SampleModels,
        experiment: Experiment,
        called_by_minimizer: bool = False,
    ) -> Union[np.ndarray, List[float]]:
        """
        Calculates the diffraction pattern using Crysfml for the given sample model and experiment.

        Args:
            sample_model: The sample model to calculate the pattern for.
            experiment: The experiment associated with the sample model.
            called_by_minimizer: Whether the calculation is called by a minimizer.

        Returns:
            The calculated diffraction pattern as a NumPy array or a list of floats.
        """
        crysfml_dict = self._crysfml_dict(sample_model, experiment)
        try:
            _, y = cfml_py_utilities.cw_powder_pattern_from_dict(crysfml_dict)
            y = self._adjust_pattern_length(y, len(experiment.datastore.pattern.x))
        except KeyError:
            print('[CrysfmlCalculator] Error: No calculated data')
            y = []
        return y

    def _adjust_pattern_length(
        self,
        pattern: List[float],
        target_length: int,
    ) -> List[float]:
        """
        Adjusts the length of the pattern to match the target length.

        Args:
            pattern: The pattern to adjust.
            target_length: The desired length of the pattern.

        Returns:
            The adjusted pattern.
        """
        # TODO: Check the origin of this discrepancy coming from PyCrysFML
        if len(pattern) > target_length:
            return pattern[:target_length]
        return pattern

    def _crysfml_dict(
        self,
        sample_model: SampleModels,
        experiment: Experiment,
    ) -> Dict[str, Union[Experiment, SampleModel]]:
        """
        Converts the sample model and experiment into a dictionary format for Crysfml.

        Args:
            sample_model: The sample model to convert.
            experiment: The experiment to convert.

        Returns:
            A dictionary representation of the sample model and experiment.
        """
        sample_model_dict = self._convert_sample_model_to_dict(sample_model)
        experiment_dict = self._convert_experiment_to_dict(experiment)
        return {
            'phases': [sample_model_dict],
            'experiments': [experiment_dict],
        }

    def _convert_sample_model_to_dict(
        self,
        sample_model: SampleModel,
    ) -> Dict[str, Any]:
        """
        Converts a sample model into a dictionary format.

        Args:
            sample_model: The sample model to convert.

        Returns:
            A dictionary representation of the sample model.
        """
        sample_model_dict = {
            sample_model.name: {
                '_space_group_name_H-M_alt': sample_model.space_group.name_h_m.value,
                '_cell_length_a': sample_model.cell.length_a.value,
                '_cell_length_b': sample_model.cell.length_b.value,
                '_cell_length_c': sample_model.cell.length_c.value,
                '_cell_angle_alpha': sample_model.cell.angle_alpha.value,
                '_cell_angle_beta': sample_model.cell.angle_beta.value,
                '_cell_angle_gamma': sample_model.cell.angle_gamma.value,
                '_atom_site': [],
            }
        }

        for atom in sample_model.atom_sites:
            atom_site = {
                '_label': atom.label.value,
                '_type_symbol': atom.type_symbol.value,
                '_fract_x': atom.fract_x.value,
                '_fract_y': atom.fract_y.value,
                '_fract_z': atom.fract_z.value,
                '_occupancy': atom.occupancy.value,
                '_adp_type': 'Biso',  # Assuming Biso for simplicity
                '_B_iso_or_equiv': atom.b_iso.value,
            }
            sample_model_dict[sample_model.name]['_atom_site'].append(atom_site)

        return sample_model_dict

    def _convert_experiment_to_dict(
        self,
        experiment: Experiment,
    ) -> Dict[str, Any]:
        """
        Converts an experiment into a dictionary format.

        Args:
            experiment: The experiment to convert.

        Returns:
            A dictionary representation of the experiment.
        """
        expt_type = getattr(experiment, 'type', None)
        instrument = getattr(experiment, 'instrument', None)
        peak = getattr(experiment, 'peak', None)

        x_data = experiment.datastore.pattern.x
        twotheta_min = float(x_data.min())
        twotheta_max = float(x_data.max())

        exp_dict = {
            'NPD': {
                '_diffrn_radiation_probe': expt_type.radiation_probe.value if expt_type else 'neutron',
                '_diffrn_radiation_wavelength': instrument.setup_wavelength.value if instrument else 1.0,
                '_pd_instr_resolution_u': peak.broad_gauss_u.value if peak else 0.0,
                '_pd_instr_resolution_v': peak.broad_gauss_v.value if peak else 0.0,
                '_pd_instr_resolution_w': peak.broad_gauss_w.value if peak else 0.0,
                '_pd_instr_resolution_x': peak.broad_lorentz_x.value if peak else 0.0,
                '_pd_instr_resolution_y': peak.broad_lorentz_y.value if peak else 0.0,
                # "_pd_instr_reflex_s_l": peak_asymm.s_l.value if peak_asymm else 0.0,
                # "_pd_instr_reflex_d_l": peak_asymm.d_l.value if peak_asymm else 0.0,
                '_pd_meas_2theta_offset': instrument.calib_twotheta_offset.value if instrument else 0.0,
                '_pd_meas_2theta_range_min': twotheta_min,
                '_pd_meas_2theta_range_max': twotheta_max,
                '_pd_meas_2theta_range_inc': (twotheta_max - twotheta_min) / len(x_data),
            }
        }

        return exp_dict
