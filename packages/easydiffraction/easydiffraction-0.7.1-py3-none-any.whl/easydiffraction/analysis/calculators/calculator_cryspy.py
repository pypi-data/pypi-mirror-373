# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

import contextlib
import copy
import io
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import numpy as np

from easydiffraction.experiments.experiment import Experiment
from easydiffraction.sample_models.sample_model import SampleModel

from .calculator_base import CalculatorBase

try:
    import cryspy
    from cryspy.H_functions_global.function_1_cryspy_objects import str_to_globaln
    from cryspy.procedure_rhochi.rhochi_by_dictionary import rhochi_calc_chi_sq_by_dictionary

    # TODO: Add the following print to debug mode
    # print("✅ 'cryspy' calculation engine is successfully imported.")
except ImportError:
    # TODO: Add the following print to debug mode
    # print("⚠️ 'cryspy' module not found. This calculation engine will not be available.")
    cryspy = None


class CryspyCalculator(CalculatorBase):
    """
    Cryspy-based diffraction calculator.
    Converts EasyDiffraction models into Cryspy objects and computes patterns.
    """

    engine_imported: bool = cryspy is not None

    @property
    def name(self) -> str:
        return 'cryspy'

    def __init__(self) -> None:
        super().__init__()
        self._cryspy_dicts: Dict[str, Dict[str, Any]] = {}

    def calculate_structure_factors(
        self,
        sample_model: SampleModel,
        experiment: Experiment,
    ) -> None:
        """
        Raises a NotImplementedError as HKL calculation is not implemented.

        Args:
            sample_model: The sample model to calculate structure factors for.
            experiment: The experiment associated with the sample models.
        """
        raise NotImplementedError('HKL calculation is not implemented for CryspyCalculator.')

    def _calculate_single_model_pattern(
        self,
        sample_model: SampleModel,
        experiment: Experiment,
        called_by_minimizer: bool = False,
    ) -> Union[np.ndarray, List[float]]:
        """
        Calculates the diffraction pattern using Cryspy for the given sample model and experiment.
        We only recreate the cryspy_obj if this method is
         - NOT called by the minimizer, or
         - the cryspy_dict is NOT yet created.
        In other cases, we are modifying the existing cryspy_dict
        This allows significantly speeding up the calculation

        Args:
            sample_model: The sample model to calculate the pattern for.
            experiment: The experiment associated with the sample model.
            called_by_minimizer: Whether the calculation is called by a minimizer.

        Returns:
            The calculated diffraction pattern as a NumPy array or a list of floats.
        """
        combined_name = f'{sample_model.name}_{experiment.name}'

        if called_by_minimizer:
            if self._cryspy_dicts and combined_name in self._cryspy_dicts:
                cryspy_dict = self._recreate_cryspy_dict(sample_model, experiment)
            else:
                cryspy_obj = self._recreate_cryspy_obj(sample_model, experiment)
                cryspy_dict = cryspy_obj.get_dictionary()
        else:
            cryspy_obj = self._recreate_cryspy_obj(sample_model, experiment)
            cryspy_dict = cryspy_obj.get_dictionary()

        self._cryspy_dicts[combined_name] = copy.deepcopy(cryspy_dict)

        cryspy_in_out_dict: Dict[str, Any] = {}

        # Calculate the pattern using Cryspy
        # TODO: Redirect stderr to suppress Cryspy warnings.
        #  This is a temporary solution to avoid cluttering the output.
        #  E.g. cryspy/A_functions_base/powder_diffraction_tof.py:106:
        #  RuntimeWarning: overflow encountered in exp
        #  Remove this when Cryspy is updated to handle warnings better.
        with contextlib.redirect_stderr(io.StringIO()):
            rhochi_calc_chi_sq_by_dictionary(
                cryspy_dict,
                dict_in_out=cryspy_in_out_dict,
                flag_use_precalculated_data=False,
                flag_calc_analytical_derivatives=False,
            )

        prefixes = {'constant wavelength': 'pd', 'time-of-flight': 'tof'}
        beam_mode = experiment.type.beam_mode.value
        if beam_mode in prefixes.keys():
            cryspy_block_name = f'{prefixes[beam_mode]}_{experiment.name}'
        else:
            print(f'[CryspyCalculator] Error: Unknown beam mode {experiment.type.beam_mode.value}')
            return []

        try:
            signal_plus = cryspy_in_out_dict[cryspy_block_name]['signal_plus']
            signal_minus = cryspy_in_out_dict[cryspy_block_name]['signal_minus']
            y_calc = signal_plus + signal_minus
        except KeyError:
            print(f'[CryspyCalculator] Error: No calculated data for {cryspy_block_name}')
            return []

        return y_calc

    def _recreate_cryspy_dict(
        self,
        sample_model: SampleModel,
        experiment: Experiment,
    ) -> Dict[str, Any]:
        """
        Recreates the Cryspy dictionary for the given sample model and experiment.

        Args:
            sample_model: The sample model to update.
            experiment: The experiment to update.

        Returns:
            The updated Cryspy dictionary.
        """
        combined_name = f'{sample_model.name}_{experiment.name}'
        cryspy_dict = copy.deepcopy(self._cryspy_dicts[combined_name])

        cryspy_model_id = f'crystal_{sample_model.name}'
        cryspy_model_dict = cryspy_dict[cryspy_model_id]

        # Cell
        cryspy_cell = cryspy_model_dict['unit_cell_parameters']
        cryspy_cell[0] = sample_model.cell.length_a.value
        cryspy_cell[1] = sample_model.cell.length_b.value
        cryspy_cell[2] = sample_model.cell.length_c.value
        cryspy_cell[3] = np.deg2rad(sample_model.cell.angle_alpha.value)
        cryspy_cell[4] = np.deg2rad(sample_model.cell.angle_beta.value)
        cryspy_cell[5] = np.deg2rad(sample_model.cell.angle_gamma.value)

        # Atomic coordinates
        cryspy_xyz = cryspy_model_dict['atom_fract_xyz']
        for idx, atom_site in enumerate(sample_model.atom_sites):
            cryspy_xyz[0][idx] = atom_site.fract_x.value
            cryspy_xyz[1][idx] = atom_site.fract_y.value
            cryspy_xyz[2][idx] = atom_site.fract_z.value

        # Atomic occupancies
        cryspy_occ = cryspy_model_dict['atom_occupancy']
        for idx, atom_site in enumerate(sample_model.atom_sites):
            cryspy_occ[idx] = atom_site.occupancy.value

        # Atomic ADPs - Biso only for now
        cryspy_biso = cryspy_model_dict['atom_b_iso']
        for idx, atom_site in enumerate(sample_model.atom_sites):
            cryspy_biso[idx] = atom_site.b_iso.value

        # ---------- Update experiment parameters ----------
        if experiment.type.beam_mode.value == 'constant wavelength':
            cryspy_expt_name = f'pd_{experiment.name}'
            cryspy_expt_dict = cryspy_dict[cryspy_expt_name]
            # Instrument
            cryspy_expt_dict['offset_ttheta'][0] = np.deg2rad(experiment.instrument.calib_twotheta_offset.value)
            cryspy_expt_dict['wavelength'][0] = experiment.instrument.setup_wavelength.value
            # Peak
            cryspy_resolution = cryspy_expt_dict['resolution_parameters']
            cryspy_resolution[0] = experiment.peak.broad_gauss_u.value
            cryspy_resolution[1] = experiment.peak.broad_gauss_v.value
            cryspy_resolution[2] = experiment.peak.broad_gauss_w.value
            cryspy_resolution[3] = experiment.peak.broad_lorentz_x.value
            cryspy_resolution[4] = experiment.peak.broad_lorentz_y.value

        elif experiment.type.beam_mode.value == 'time-of-flight':
            cryspy_expt_name = f'tof_{experiment.name}'
            cryspy_expt_dict = cryspy_dict[cryspy_expt_name]
            # Instrument
            cryspy_expt_dict['zero'][0] = experiment.instrument.calib_d_to_tof_offset.value
            cryspy_expt_dict['dtt1'][0] = experiment.instrument.calib_d_to_tof_linear.value
            cryspy_expt_dict['dtt2'][0] = experiment.instrument.calib_d_to_tof_quad.value
            cryspy_expt_dict['ttheta_bank'] = np.deg2rad(experiment.instrument.setup_twotheta_bank.value)
            # Peak
            cryspy_sigma = cryspy_expt_dict['profile_sigmas']
            cryspy_sigma[0] = experiment.peak.broad_gauss_sigma_0.value
            cryspy_sigma[1] = experiment.peak.broad_gauss_sigma_1.value
            cryspy_sigma[2] = experiment.peak.broad_gauss_sigma_2.value

            cryspy_beta = cryspy_expt_dict['profile_betas']
            cryspy_beta[0] = experiment.peak.broad_mix_beta_0.value
            cryspy_beta[1] = experiment.peak.broad_mix_beta_1.value

            cryspy_alpha = cryspy_expt_dict['profile_alphas']
            cryspy_alpha[0] = experiment.peak.asym_alpha_0.value
            cryspy_alpha[1] = experiment.peak.asym_alpha_1.value

        return cryspy_dict

    def _recreate_cryspy_obj(
        self,
        sample_model: SampleModel,
        experiment: Experiment,
    ) -> Any:
        """
        Recreates the Cryspy object for the given sample model and experiment.

        Args:
            sample_model: The sample model to recreate.
            experiment: The experiment to recreate.

        Returns:
            The recreated Cryspy object.
        """
        cryspy_obj = str_to_globaln('')

        cryspy_sample_model_cif = self._convert_sample_model_to_cryspy_cif(sample_model)
        cryspy_sample_model_obj = str_to_globaln(cryspy_sample_model_cif)
        cryspy_obj.add_items(cryspy_sample_model_obj.items)

        # Add single experiment to cryspy_obj
        cryspy_experiment_cif = self._convert_experiment_to_cryspy_cif(
            experiment,
            linked_phase=sample_model,
        )

        cryspy_experiment_obj = str_to_globaln(cryspy_experiment_cif)
        cryspy_obj.add_items(cryspy_experiment_obj.items)

        return cryspy_obj

    def _convert_sample_model_to_cryspy_cif(
        self,
        sample_model: SampleModel,
    ) -> str:
        """
        Converts a sample model to a Cryspy CIF string.

        Args:
            sample_model: The sample model to convert.

        Returns:
            The Cryspy CIF string representation of the sample model.
        """
        return sample_model.as_cif()

    def _convert_experiment_to_cryspy_cif(
        self,
        experiment: Experiment,
        linked_phase: Any,
    ) -> str:
        """
        Converts an experiment to a Cryspy CIF string.

        Args:
            experiment: The experiment to convert.
            linked_phase: The linked phase associated with the experiment.

        Returns:
            The Cryspy CIF string representation of the experiment.
        """
        expt_type = getattr(experiment, 'type', None)
        instrument = getattr(experiment, 'instrument', None)
        peak = getattr(experiment, 'peak', None)

        cif_lines = [f'data_{experiment.name}']

        if expt_type is not None:
            cif_lines.append('')
            radiation_probe = expt_type.radiation_probe.value
            radiation_probe = radiation_probe.replace('neutron', 'neutrons')
            radiation_probe = radiation_probe.replace('xray', 'X-rays')
            cif_lines.append(f'_setup_radiation {radiation_probe}')

        if instrument:
            instrument_mapping = {
                'setup_wavelength': '_setup_wavelength',
                'calib_twotheta_offset': '_setup_offset_2theta',
                'setup_twotheta_bank': '_tof_parameters_2theta_bank',
                'calib_d_to_tof_offset': '_tof_parameters_Zero',
                'calib_d_to_tof_linear': '_tof_parameters_Dtt1',
                'calib_d_to_tof_quad': '_tof_parameters_dtt2',
            }
            cif_lines.append('')
            for local_attr_name, engine_key_name in instrument_mapping.items():
                if hasattr(instrument, local_attr_name):
                    attr_value = getattr(instrument, local_attr_name).value
                    cif_lines.append(f'{engine_key_name} {attr_value}')

        if peak:
            peak_mapping = {
                'broad_gauss_u': '_pd_instr_resolution_U',
                'broad_gauss_v': '_pd_instr_resolution_V',
                'broad_gauss_w': '_pd_instr_resolution_W',
                'broad_lorentz_x': '_pd_instr_resolution_X',
                'broad_lorentz_y': '_pd_instr_resolution_Y',
                'broad_gauss_sigma_0': '_tof_profile_sigma0',
                'broad_gauss_sigma_1': '_tof_profile_sigma1',
                'broad_gauss_sigma_2': '_tof_profile_sigma2',
                'broad_mix_beta_0': '_tof_profile_beta0',
                'broad_mix_beta_1': '_tof_profile_beta1',
                'asym_alpha_0': '_tof_profile_alpha0',
                'asym_alpha_1': '_tof_profile_alpha1',
            }
            cif_lines.append('')
            if expt_type.beam_mode.value == 'time-of-flight':
                cif_lines.append('_tof_profile_peak_shape Gauss')
            for local_attr_name, engine_key_name in peak_mapping.items():
                if hasattr(peak, local_attr_name):
                    attr_value = getattr(peak, local_attr_name).value
                    cif_lines.append(f'{engine_key_name} {attr_value}')

        x_data = experiment.datastore.pattern.x
        twotheta_min = float(x_data.min())
        twotheta_max = float(x_data.max())
        cif_lines.append('')
        if expt_type.beam_mode.value == 'constant wavelength':
            cif_lines.append(f'_range_2theta_min {twotheta_min}')
            cif_lines.append(f'_range_2theta_max {twotheta_max}')
        elif expt_type.beam_mode.value == 'time-of-flight':
            cif_lines.append(f'_range_time_min {twotheta_min}')
            cif_lines.append(f'_range_time_max {twotheta_max}')

        cif_lines.append('')
        cif_lines.append('loop_')
        cif_lines.append('_phase_label')
        cif_lines.append('_phase_scale')
        cif_lines.append(f'{linked_phase.name} 1.0')

        if expt_type.beam_mode.value == 'constant wavelength':
            cif_lines.append('')
            cif_lines.append('loop_')
            cif_lines.append('_pd_background_2theta')
            cif_lines.append('_pd_background_intensity')
            cif_lines.append(f'{twotheta_min} 0.0')
            cif_lines.append(f'{twotheta_max} 0.0')
        elif expt_type.beam_mode.value == 'time-of-flight':
            cif_lines.append('')
            cif_lines.append('loop_')
            cif_lines.append('_tof_backgroundpoint_time')
            cif_lines.append('_tof_backgroundpoint_intensity')
            cif_lines.append(f'{twotheta_min} 0.0')
            cif_lines.append(f'{twotheta_max} 0.0')

        if expt_type.beam_mode.value == 'constant wavelength':
            cif_lines.append('')
            cif_lines.append('loop_')
            cif_lines.append('_pd_meas_2theta')
            cif_lines.append('_pd_meas_intensity')
            cif_lines.append('_pd_meas_intensity_sigma')
        elif expt_type.beam_mode.value == 'time-of-flight':
            cif_lines.append('')
            cif_lines.append('loop_')
            cif_lines.append('_tof_meas_time')
            cif_lines.append('_tof_meas_intensity')
            cif_lines.append('_tof_meas_intensity_sigma')

        y_data = experiment.datastore.pattern.meas
        sy_data = experiment.datastore.pattern.meas_su
        for x_val, y_val, sy_val in zip(x_data, y_data, sy_data):
            cif_lines.append(f'  {x_val:.5f}   {y_val:.5f}   {sy_val:.5f}')

        cryspy_experiment_cif = '\n'.join(cif_lines)

        return cryspy_experiment_cif
