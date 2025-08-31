from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from easydiffraction.analysis.minimizers.minimizer_base import FitResults
from easydiffraction.analysis.minimizers.minimizer_base import MinimizerBase


# Mock subclass of MinimizerBase to test its methods
class MockMinimizer(MinimizerBase):
    def _prepare_solver_args(self, parameters):
        return {'mock_arg': 'mock_value'}

    def _run_solver(self, objective_function, **engine_parameters):
        return {'success': True, 'raw_result': 'mock_result'}

    def _sync_result_to_parameters(self, raw_result, parameters):
        for param in parameters:
            param.value = 1.0  # Mock synchronization

    def _check_success(self, raw_result):
        return raw_result.get('success', False)

    def _finalize_fit(self, parameters, raw_result):
        return FitResults(
            success=raw_result.get('success', False),
            parameters=parameters,
            chi_square=raw_result.get('chi_square', 0.0),
            reduced_chi_square=raw_result.get('reduced_chi_square', 0.0),
            message=raw_result.get('message', ''),
            iterations=raw_result.get('iterations', 0),
            engine_result=raw_result.get('raw_result', None),
            starting_parameters=[p.start_value for p in parameters],
            fitting_time=raw_result.get('fitting_time', 0.0),
        )


@pytest.fixture
def mock_minimizer():
    return MockMinimizer(name='MockMinimizer', method='mock_method', max_iterations=100)


@pytest.fixture
def mock_parameters():
    param1 = MagicMock(name='param1', value=None, start_value=0.5, uncertainty=None)
    param2 = MagicMock(name='param2', value=None, start_value=1.0, uncertainty=None)
    return [param1, param2]


@pytest.fixture
def mock_objective_function():
    return MagicMock(return_value=[1.0, 2.0, 3.0])


def test_prepare_solver_args(mock_minimizer, mock_parameters):
    solver_args = mock_minimizer._prepare_solver_args(mock_parameters)
    assert solver_args == {'mock_arg': 'mock_value'}


def test_run_solver(mock_minimizer, mock_objective_function):
    raw_result = mock_minimizer._run_solver(mock_objective_function, mock_arg='mock_value')
    assert raw_result == {'success': True, 'raw_result': 'mock_result'}


def test_sync_result_to_parameters(mock_minimizer, mock_parameters):
    raw_result = {'success': True}
    mock_minimizer._sync_result_to_parameters(raw_result, mock_parameters)

    # Assertions
    for param in mock_parameters:
        assert param.value == 1.0


def test_check_success(mock_minimizer):
    raw_result = {'success': True}
    assert mock_minimizer._check_success(raw_result) is True

    raw_result = {'success': False}
    assert mock_minimizer._check_success(raw_result) is False


def test_finalize_fit(mock_minimizer, mock_parameters):
    raw_result = {'success': True}
    result = mock_minimizer._finalize_fit(mock_parameters, raw_result)

    # Assertions
    assert isinstance(result, FitResults)
    assert result.success is True
    assert result.parameters == mock_parameters


@patch('easydiffraction.analysis.minimizers.fitting_progress_tracker.FittingProgressTracker')
def test_fit(mock_tracker, mock_minimizer, mock_parameters, mock_objective_function):
    mock_minimizer.tracker.finish_tracking = MagicMock()
    result = mock_minimizer.fit(mock_parameters, mock_objective_function)

    # Assertions
    assert isinstance(result, FitResults)
    assert result.success is True


def test_create_objective_function(mock_minimizer):
    parameters = [MagicMock()]
    sample_models = MagicMock()
    experiments = MagicMock()
    calculator = MagicMock()

    objective_function = mock_minimizer._create_objective_function(parameters, sample_models, experiments, calculator)

    # Assertions
    assert callable(objective_function)
    with patch.object(mock_minimizer, '_objective_function', return_value=[1.0, 2.0, 3.0]) as mock_objective:
        residuals = objective_function({'param1': 1.0})
        mock_objective.assert_called_once_with({'param1': 1.0}, parameters, sample_models, experiments, calculator)
        assert residuals == [1.0, 2.0, 3.0]
