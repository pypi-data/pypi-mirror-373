from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from easydiffraction.analysis.minimization import DiffractionMinimizer


@pytest.fixture
def mock_sample_models():
    sample_models = MagicMock()
    sample_models.get_free_params.return_value = [
        MagicMock(name='param1', value=1.0, start_value=None, min=0.0, max=2.0, free=True),
        MagicMock(name='param2', value=2.0, start_value=None, min=1.0, max=3.0, free=True),
    ]
    return sample_models


@pytest.fixture
def mock_experiments():
    experiments = MagicMock()
    experiments.get_free_params.return_value = [
        MagicMock(name='param3', value=3.0, start_value=None, min=2.0, max=4.0, free=True),
    ]
    experiments.ids = ['experiment1']
    experiments._items = {
        'experiment1': MagicMock(
            datastore=MagicMock(
                pattern=MagicMock(
                    meas=np.array([10.0, 20.0, 30.0]),
                    meas_su=np.array([1.0, 1.0, 1.0]),
                    excluded=np.array([False, False, False]),
                )
            )
        )
    }
    return experiments


@pytest.fixture
def mock_calculator():
    calculator = MagicMock()
    calculator.calculate_pattern.return_value = np.array([9.0, 19.0, 29.0])
    return calculator


@pytest.fixture
def mock_minimizer():
    minimizer = MagicMock()
    minimizer.fit.return_value = MagicMock(success=True)
    minimizer._sync_result_to_parameters = MagicMock()
    minimizer.tracker.track = MagicMock(return_value=np.array([1.0, 2.0, 3.0]))
    return minimizer


@pytest.fixture
def diffraction_minimizer(mock_minimizer):
    with patch(
        'easydiffraction.analysis.minimizers.minimizer_factory.MinimizerFactory.create_minimizer', return_value=mock_minimizer
    ):
        return DiffractionMinimizer(selection='lmfit (leastsq)')


def test_fit_no_params(diffraction_minimizer, mock_sample_models, mock_experiments, mock_calculator):
    mock_sample_models.get_free_params.return_value = []
    mock_experiments.get_free_params.return_value = []

    result = diffraction_minimizer.fit(mock_sample_models, mock_experiments, mock_calculator)

    # Assertions
    assert result is None


def test_fit_with_params(diffraction_minimizer, mock_sample_models, mock_experiments, mock_calculator):
    diffraction_minimizer.fit(mock_sample_models, mock_experiments, mock_calculator)

    # Assertions
    assert diffraction_minimizer.results.success is True
    assert mock_calculator.calculate_pattern.called
    assert mock_sample_models.get_free_params.called
    assert mock_experiments.get_free_params.called


def test_residual_function(diffraction_minimizer, mock_sample_models, mock_experiments, mock_calculator):
    parameters = mock_sample_models.get_free_params() + mock_experiments.get_free_params()
    engine_params = MagicMock()

    residuals = diffraction_minimizer._residual_function(
        engine_params=engine_params,
        parameters=parameters,
        sample_models=mock_sample_models,
        experiments=mock_experiments,
        calculator=mock_calculator,
    )

    # Assertions
    assert isinstance(residuals, np.ndarray)
    assert len(residuals) == 3
    assert mock_calculator.calculate_pattern.called
    assert diffraction_minimizer.minimizer._sync_result_to_parameters.called


@patch(
    'easydiffraction.analysis.reliability_factors.get_reliability_inputs',
    return_value=(np.array([10.0]), np.array([9.0]), np.array([1.0])),
)
def test_process_fit_results(
    mock_get_reliability_inputs, diffraction_minimizer, mock_sample_models, mock_experiments, mock_calculator
):
    diffraction_minimizer.results = MagicMock()
    diffraction_minimizer._process_fit_results(mock_sample_models, mock_experiments, mock_calculator)

    # Assertions
    # mock_get_reliability_inputs.assert_called_once_with(mock_sample_models, mock_experiments, mock_calculator)

    # Extract the arguments passed to `display_results`
    _, kwargs = diffraction_minimizer.results.display_results.call_args

    # Assertions for arrays
    np.testing.assert_array_equal(kwargs['y_calc'], np.array([9.0, 19.0, 29.0]))
    np.testing.assert_array_equal(kwargs['y_err'], np.array([1.0, 1.0, 1.0]))
    np.testing.assert_array_equal(kwargs['y_obs'], np.array([10.0, 20.0, 30.0]))

    # Assertions for other arguments
    assert kwargs['f_obs'] is None
    assert kwargs['f_calc'] is None
