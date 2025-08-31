from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from easydiffraction.analysis.calculators.calculator_cryspy import CryspyCalculator


@pytest.fixture
def mock_sample_model():
    sample_model = MagicMock()
    sample_model.name = 'sample1'
    sample_model.cell.length_a.value = 1.0
    sample_model.cell.length_b.value = 2.0
    sample_model.cell.length_c.value = 3.0
    sample_model.cell.angle_alpha.value = 90.0
    sample_model.cell.angle_beta.value = 90.0
    sample_model.cell.angle_gamma.value = 90.0
    sample_model.atom_sites = [
        MagicMock(
            fract_x=MagicMock(value=0.1),
            fract_y=MagicMock(value=0.2),
            fract_z=MagicMock(value=0.3),
            occupancy=MagicMock(value=1.0),
            b_iso=MagicMock(value=0.5),
        )
    ]
    return sample_model


@pytest.fixture
def mock_experiment():
    experiment = MagicMock()
    experiment.name = 'experiment1'
    experiment.type.beam_mode.value = 'constant wavelength'
    experiment.datastore.pattern.x = np.array([1.0, 2.0, 3.0])
    experiment.datastore.pattern.meas = np.array([10.0, 20.0, 30.0])
    experiment.datastore.pattern.meas_su = np.array([0.1, 0.2, 0.3])
    experiment.instrument.calib_twotheta_offset.value = 0.0
    experiment.instrument.setup_wavelength.value = 1.54
    experiment.peak.broad_gauss_u.value = 0.1
    experiment.peak.broad_gauss_v.value = 0.2
    experiment.peak.broad_gauss_w.value = 0.3
    experiment.peak.broad_lorentz_x.value = 0.4
    experiment.peak.broad_lorentz_y.value = 0.5
    return experiment


@patch('easydiffraction.analysis.calculators.calculator_cryspy.str_to_globaln')
def test_recreate_cryspy_obj(mock_str_to_globaln, mock_sample_model, mock_experiment):
    mock_str_to_globaln.return_value = MagicMock(add_items=MagicMock())

    calculator = CryspyCalculator()
    cryspy_obj = calculator._recreate_cryspy_obj(mock_sample_model, mock_experiment)

    # Assertions
    mock_str_to_globaln.assert_called()
    assert cryspy_obj.add_items.called


@patch('easydiffraction.analysis.calculators.calculator_cryspy.rhochi_calc_chi_sq_by_dictionary')
def test_calculate_single_model_pattern(mock_rhochi_calc, mock_sample_model, mock_experiment):
    mock_rhochi_calc.return_value = None

    calculator = CryspyCalculator()
    calculator._cryspy_dicts = {'experiment1': {'mock_key': 'mock_value'}}

    result = calculator._calculate_single_model_pattern(mock_sample_model, mock_experiment, called_by_minimizer=False)

    # Assertions
    assert isinstance(result, np.ndarray) or result == []
    mock_rhochi_calc.assert_called()


def test_recreate_cryspy_dict(mock_sample_model, mock_experiment):
    calculator = CryspyCalculator()
    calculator._cryspy_dicts = {
        'sample1_experiment1': {
            'pd_experiment1': {
                'offset_ttheta': [0.1],
                'wavelength': [1.54],
                'resolution_parameters': [0.1, 0.2, 0.3, 0.4, 0.5],
            },
            'crystal_sample1': {
                'unit_cell_parameters': [0, 0, 0, 0, 0, 0],
                'atom_fract_xyz': [[0], [0], [0]],
                'atom_occupancy': [0],
                'atom_b_iso': [0],
            },
        }
    }

    cryspy_dict = calculator._recreate_cryspy_dict(mock_sample_model, mock_experiment)

    # Assertions
    assert cryspy_dict['crystal_sample1']['unit_cell_parameters'][:3] == [1.0, 2.0, 3.0]
    assert cryspy_dict['crystal_sample1']['atom_fract_xyz'][0][0] == 0.1
    assert cryspy_dict['crystal_sample1']['atom_occupancy'][0] == 1.0
    assert cryspy_dict['crystal_sample1']['atom_b_iso'][0] == 0.5
    assert cryspy_dict['pd_experiment1']['offset_ttheta'][0] == 0.0
    assert cryspy_dict['pd_experiment1']['wavelength'][0] == 1.54
    assert cryspy_dict['pd_experiment1']['resolution_parameters'] == [0.1, 0.2, 0.3, 0.4, 0.5]
