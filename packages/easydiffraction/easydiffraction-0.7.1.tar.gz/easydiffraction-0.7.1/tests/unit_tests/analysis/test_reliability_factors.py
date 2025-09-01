from unittest.mock import Mock

import numpy as np

from easydiffraction.analysis.reliability_factors import calculate_r_factor
from easydiffraction.analysis.reliability_factors import calculate_r_factor_squared
from easydiffraction.analysis.reliability_factors import calculate_rb_factor
from easydiffraction.analysis.reliability_factors import calculate_reduced_chi_square
from easydiffraction.analysis.reliability_factors import calculate_weighted_r_factor
from easydiffraction.analysis.reliability_factors import get_reliability_inputs


def test_calculate_r_factor():
    y_obs = [10, 20, 30]
    y_calc = [9, 19, 29]
    result = calculate_r_factor(y_obs, y_calc)
    expected = 0.05
    np.testing.assert_allclose(result, expected)

    # Test with empty arrays
    assert np.isnan(calculate_r_factor([], []))

    # Test with zero denominator
    assert np.isnan(calculate_r_factor([0, 0, 0], [1, 1, 1]))


def test_calculate_weighted_r_factor():
    y_obs = [10, 20, 30]
    y_calc = [9, 19, 29]
    weights = [1, 1, 1]
    result = calculate_weighted_r_factor(y_obs, y_calc, weights)
    expected = 0.04629100498862757
    np.testing.assert_allclose(result, expected)

    # Test with empty arrays
    assert np.isnan(calculate_weighted_r_factor([], [], []))

    # Test with zero denominator
    assert np.isnan(calculate_weighted_r_factor([0, 0, 0], [1, 1, 1], [1, 1, 1]))


def test_calculate_rb_factor():
    y_obs = [10, 20, 30]
    y_calc = [9, 19, 29]
    result = calculate_rb_factor(y_obs, y_calc)
    expected = 0.05
    np.testing.assert_allclose(result, expected)

    # Test with empty arrays
    assert np.isnan(calculate_rb_factor([], []))

    # Test with zero denominator
    assert np.isnan(calculate_rb_factor([0, 0, 0], [1, 1, 1]))


def test_calculate_r_factor_squared():
    y_obs = [10, 20, 30]
    y_calc = [9, 19, 29]
    result = calculate_r_factor_squared(y_obs, y_calc)
    expected = 0.04629100498862757
    np.testing.assert_allclose(result, expected)

    # Test with empty arrays
    assert np.isnan(calculate_r_factor_squared([], []))

    # Test with zero denominator
    assert np.isnan(calculate_r_factor_squared([0, 0, 0], [1, 1, 1]))


def test_calculate_reduced_chi_square():
    residuals = [1, 2, 3]
    num_parameters = 1
    result = calculate_reduced_chi_square(residuals, num_parameters)
    expected = 7.0
    np.testing.assert_allclose(result, expected)

    # Test with empty residuals
    assert np.isnan(calculate_reduced_chi_square([], 1))

    # Test with zero degrees of freedom
    assert np.isnan(calculate_reduced_chi_square([1, 2, 3], 3))


def test_get_reliability_inputs():
    # Mock inputs
    sample_models = None
    experiments = Mock()
    calculator = Mock()

    experiments._items = {
        'experiment1': Mock(
            datastore=Mock(
                pattern=Mock(
                    meas=np.array([10.0, 20.0, 30.0]),
                    meas_su=np.array([1.0, 1.0, 1.0]),
                    excluded=np.array([False, False, False]),
                )
            )
        )
    }
    calculator.calculate_pattern.return_value = np.array([9.0, 19.0, 29.0])

    y_obs, y_calc, y_err = get_reliability_inputs(sample_models, experiments, calculator)

    # Assertions
    np.testing.assert_array_equal(y_obs, [10.0, 20.0, 30.0])
    np.testing.assert_array_equal(y_calc, [9.0, 19.0, 29.0])
    np.testing.assert_array_equal(y_err, [1.0, 1.0, 1.0])
