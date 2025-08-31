from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from easydiffraction.analysis.minimizers.minimizer_dfols import DfolsMinimizer


@pytest.fixture
def mock_parameters():
    param1 = MagicMock(name='param1', value=1.0, min=0.0, max=2.0, uncertainty=None)
    param2 = MagicMock(name='param2', value=2.0, min=1.0, max=3.0, uncertainty=None)
    return [param1, param2]


@pytest.fixture
def mock_objective_function():
    return MagicMock(return_value=np.array([1.0, 2.0, 3.0]))


@pytest.fixture
def dfols_minimizer():
    return DfolsMinimizer(name='dfols', max_iterations=100)


def test_prepare_solver_args(dfols_minimizer, mock_parameters):
    solver_args = dfols_minimizer._prepare_solver_args(mock_parameters)

    # Assertions
    assert np.allclose(solver_args['x0'], [1.0, 2.0])
    assert np.allclose(solver_args['bounds'][0], [0.0, 1.0])  # Lower bounds
    assert np.allclose(solver_args['bounds'][1], [2.0, 3.0])  # Upper bounds


@patch('easydiffraction.analysis.minimizers.minimizer_dfols.solve')
def test_run_solver(mock_solve, dfols_minimizer, mock_objective_function):
    mock_solve.return_value = MagicMock(x=np.array([1.5, 2.5]), flag=0)

    solver_args = {'x0': np.array([1.0, 2.0]), 'bounds': (np.array([0.0, 1.0]), np.array([2.0, 3.0]))}
    raw_result = dfols_minimizer._run_solver(mock_objective_function, **solver_args)

    # Assertions
    mock_solve.assert_called_once_with(
        mock_objective_function, x0=solver_args['x0'], bounds=solver_args['bounds'], maxfun=dfols_minimizer.max_iterations
    )
    assert np.allclose(raw_result.x, [1.5, 2.5])


def test_sync_result_to_parameters(dfols_minimizer, mock_parameters):
    raw_result = MagicMock(x=np.array([1.5, 2.5]))

    dfols_minimizer._sync_result_to_parameters(mock_parameters, raw_result)

    # Assertions
    assert mock_parameters[0].value == 1.5
    assert mock_parameters[1].value == 2.5
    assert mock_parameters[0].uncertainty is None
    assert mock_parameters[1].uncertainty is None


def test_check_success(dfols_minimizer):
    raw_result = MagicMock(flag=0, EXIT_SUCCESS=0)
    assert dfols_minimizer._check_success(raw_result) is True

    raw_result = MagicMock(flag=1, EXIT_SUCCESS=0)
    assert dfols_minimizer._check_success(raw_result) is False


@patch('easydiffraction.analysis.minimizers.minimizer_dfols.solve')
def test_fit(mock_solve, dfols_minimizer, mock_parameters, mock_objective_function):
    mock_solve.return_value = MagicMock(x=np.array([1.5, 2.5]), flag=0)
    dfols_minimizer.tracker.finish_tracking = MagicMock()

    result = dfols_minimizer.fit(mock_parameters, mock_objective_function)

    # Assertions
    assert np.allclose([p.value for p in result.parameters], [1.5, 2.5])
    assert result.iterations == 0  # DFO-LS doesn't provide iteration count by default
