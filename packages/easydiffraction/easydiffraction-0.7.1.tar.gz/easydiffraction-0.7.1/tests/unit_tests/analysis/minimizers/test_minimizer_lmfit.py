from unittest.mock import MagicMock
from unittest.mock import patch

import lmfit
import pytest

from easydiffraction.analysis.minimizers.minimizer_lmfit import LmfitMinimizer
from easydiffraction.core.objects import Parameter


@pytest.fixture
def mock_parameters():
    param1 = Parameter(name='param1', cif_name='param1', value=1.0, free=True, min_value=0.0, max_value=2.0, uncertainty=None)
    param2 = Parameter(name='param2', cif_name='param2', value=2.0, free=False, min_value=1.0, max_value=3.0, uncertainty=None)
    return [param1, param2]


@pytest.fixture
def mock_objective_function():
    return MagicMock(return_value=[1.0, 2.0, 3.0])


@pytest.fixture
def lmfit_minimizer():
    return LmfitMinimizer(name='lmfit', method='leastsq', max_iterations=100)


def test_prepare_solver_args(lmfit_minimizer, mock_parameters):
    solver_args = lmfit_minimizer._prepare_solver_args(mock_parameters)

    # Assertions
    assert isinstance(solver_args['engine_parameters'], lmfit.Parameters)
    assert 'None__param1' in solver_args['engine_parameters']
    assert 'None__param2' in solver_args['engine_parameters']
    assert solver_args['engine_parameters']['None__param1'].value == 1.0
    assert solver_args['engine_parameters']['None__param1'].min == 0.0
    assert solver_args['engine_parameters']['None__param1'].max == 2.0
    assert solver_args['engine_parameters']['None__param1'].vary is True
    assert solver_args['engine_parameters']['None__param2'].value == 2.0
    assert solver_args['engine_parameters']['None__param2'].vary is False


@patch('easydiffraction.analysis.minimizers.minimizer_lmfit.lmfit.minimize')
def test_run_solver(mock_minimize, lmfit_minimizer, mock_objective_function, mock_parameters):
    mock_minimize.return_value = MagicMock(params={'param1': MagicMock(value=1.5), 'param2': MagicMock(value=2.5)})

    solver_args = lmfit_minimizer._prepare_solver_args(mock_parameters)
    raw_result = lmfit_minimizer._run_solver(mock_objective_function, **solver_args)

    # Assertions
    mock_minimize.assert_called_once_with(
        mock_objective_function,
        params=solver_args['engine_parameters'],
        method='leastsq',
        nan_policy='propagate',
        max_nfev=lmfit_minimizer.max_iterations,
    )
    assert raw_result.params['param1'].value == 1.5
    assert raw_result.params['param2'].value == 2.5


def test_sync_result_to_parameters(lmfit_minimizer, mock_parameters):
    raw_result = MagicMock(
        params={'None__param1': MagicMock(value=1.5, stderr=0.1), 'None__param2': MagicMock(value=2.5, stderr=0.2)}
    )

    lmfit_minimizer._sync_result_to_parameters(mock_parameters, raw_result)

    # Assertions
    assert mock_parameters[0].value == 1.5
    assert mock_parameters[0].uncertainty == 0.1
    assert mock_parameters[1].value == 2.5
    assert mock_parameters[1].uncertainty == 0.2


def test_check_success(lmfit_minimizer):
    raw_result = MagicMock(success=True)
    assert lmfit_minimizer._check_success(raw_result) is True

    raw_result = MagicMock(success=False)
    assert lmfit_minimizer._check_success(raw_result) is False


@patch('easydiffraction.analysis.minimizers.minimizer_lmfit.lmfit.minimize')
def test_fit(mock_minimize, lmfit_minimizer, mock_parameters, mock_objective_function):
    mock_minimize.return_value = MagicMock(
        params={'None__param1': MagicMock(value=1.5, stderr=0.1), 'None__param2': MagicMock(value=2.5, stderr=0.2)},
        success=True,
    )
    lmfit_minimizer.tracker.finish_tracking = MagicMock()
    result = lmfit_minimizer.fit(mock_parameters, mock_objective_function)

    # Assertions
    assert result.success is True
    assert result.parameters[0].value == 1.5
    assert result.parameters[0].uncertainty == 0.1
    assert result.parameters[1].value == 2.5
    assert result.parameters[1].uncertainty == 0.2
