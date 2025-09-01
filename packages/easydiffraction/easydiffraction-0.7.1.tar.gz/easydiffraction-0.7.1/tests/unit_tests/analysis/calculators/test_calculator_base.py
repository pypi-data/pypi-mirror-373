from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from easydiffraction.analysis.calculators.calculator_base import CalculatorBase


# Mock subclass of CalculatorBase to test its concrete methods
class MockCalculator(CalculatorBase):
    @property
    def name(self):
        return 'MockCalculator'

    @property
    def engine_imported(self):
        return True

    def calculate_structure_factors(self, sample_model, experiment):
        return np.array([1.0, 2.0, 3.0])

    def _calculate_single_model_pattern(self, sample_model, experiment, called_by_minimizer):
        return np.array([1.0, 2.0, 3.0])


@pytest.fixture
def mock_sample_models():
    sample_models = MagicMock()
    sample_models.get_all_params.return_value = {'param1': 1, 'param2': 2}
    sample_models.get_ids.return_value = ['phase1', 'phase2']
    sample_models.__getitem__.side_effect = lambda key: MagicMock(apply_symmetry_constraints=MagicMock())
    return sample_models


@pytest.fixture
def mock_experiment():
    experiment = MagicMock()
    experiment.datastore.pattern.x = np.array([1.0, 2.0, 3.0])
    experiment.datastore.pattern.bkg = None
    experiment.datastore.pattern.calc = None
    experiment.linked_phases = [
        MagicMock(_entry_id='phase1', scale=MagicMock(value=2.0)),
        MagicMock(_entry_id='phase2', scale=MagicMock(value=1.5)),
    ]
    experiment.background.calculate.return_value = np.array([0.1, 0.2, 0.3])
    return experiment


@patch('easydiffraction.core.singletons.ConstraintsHandler.get')
def test_calculate_pattern(mock_constraints_handler, mock_sample_models, mock_experiment):
    mock_constraints_handler.return_value.apply = MagicMock()

    calculator = MockCalculator()
    result = calculator.calculate_pattern(mock_sample_models, mock_experiment)

    # Assertions
    assert np.allclose(result, np.array([3.6, 7.2, 10.8]))
    mock_constraints_handler.return_value.apply.assert_called_once_with()
    assert mock_experiment.datastore.pattern.bkg is not None
    assert mock_experiment.datastore.pattern.calc is not None


def test_get_valid_linked_phases(mock_sample_models, mock_experiment):
    calculator = MockCalculator()

    valid_phases = calculator._get_valid_linked_phases(mock_sample_models, mock_experiment)

    # Assertions
    assert len(valid_phases) == 2
    assert valid_phases[0]._entry_id == 'phase1'
    assert valid_phases[1]._entry_id == 'phase2'


def test_calculate_structure_factors(mock_sample_models, mock_experiment):
    calculator = MockCalculator()

    # Mock the method's behavior if necessary
    result = calculator.calculate_structure_factors(mock_sample_models, mock_experiment)

    # Assertions
    assert np.allclose(result, np.array([1.0, 2.0, 3.0]))
