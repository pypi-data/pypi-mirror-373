from unittest.mock import patch

import numpy as np
import pytest

from easydiffraction.analysis.minimizers.fitting_progress_tracker import FittingProgressTracker
from easydiffraction.analysis.minimizers.fitting_progress_tracker import format_cell


def test_format_cell():
    # Test center alignment
    assert format_cell('test', width=10, align='center') == '   test   '
    # Test left alignment
    assert format_cell('test', width=10, align='left') == 'test      '
    # Test right alignment
    assert format_cell('test', width=10, align='right') == '      test'
    # Test default alignment (center)
    assert format_cell('test', width=10) == '   test   '
    # Test invalid alignment
    assert format_cell('test', width=10, align='invalid') == 'test'


@pytest.fixture
def tracker():
    return FittingProgressTracker()


@patch('builtins.print')
def test_start_tracking(mock_print, tracker):
    tracker.start_tracking('MockMinimizer')

    # Assertions
    mock_print.assert_any_call("🚀 Starting fit process with 'MockMinimizer'...")
    mock_print.assert_any_call('📈 Goodness-of-fit (reduced χ²) change:')
    assert mock_print.call_count > 2  # Ensure headers and borders are printed


@patch('builtins.print')
def test_add_tracking_info(mock_print, tracker):
    tracker.add_tracking_info([1, '9.0', '10% ↓'])

    # Assertions
    mock_print.assert_called_once()
    assert '│        1        │       9.0       │      10% ↓      │' in mock_print.call_args[0][0]


@patch('builtins.print')
def test_finish_tracking(mock_print, tracker):
    tracker._last_iteration = 5
    tracker._last_chi2 = 1.23
    tracker._best_chi2 = 1.23
    tracker._best_iteration = 5

    tracker.finish_tracking()

    # Assertions
    mock_print.assert_any_call('🏆 Best goodness-of-fit (reduced χ²) is 1.23 at iteration 5')
    mock_print.assert_any_call('✅ Fitting complete.')


def test_reset(tracker):
    tracker._iteration = 5
    tracker._previous_chi2 = 1.23
    tracker.reset()

    # Assertions
    assert tracker._iteration == 0
    assert tracker._previous_chi2 is None


@patch('easydiffraction.analysis.reliability_factors.calculate_reduced_chi_square', return_value=1.23)
@patch('builtins.print')
def test_track(mock_print, mock_calculate_chi2, tracker):
    residuals = np.array([1.1, 2.1, 3.1, 4.1, 5.1])
    parameters = [1.0, 2.0, 3.0]

    tracker.track(residuals, parameters)

    # Assertions
    # mock_calculate_chi2.assert_called_once_with(residuals, len(parameters))
    assert tracker._iteration == 1
    assert tracker._previous_chi2 == 29.025
    assert tracker._best_chi2 == 29.025
    assert tracker._best_iteration == 1
    mock_print.assert_called()


def test_start_timer(tracker):
    with patch('time.perf_counter', return_value=100.0):
        tracker.start_timer()
        assert tracker._start_time == 100.0


def test_stop_timer(tracker):
    with patch('time.perf_counter', side_effect=[100.0, 105.0]):
        tracker.start_timer()
        tracker.stop_timer()
        assert tracker._fitting_time == 5.0
