# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional
from typing import Tuple

import numpy as np

from easydiffraction.analysis.calculators.calculator_base import CalculatorBase
from easydiffraction.experiments.experiments import Experiments
from easydiffraction.sample_models.sample_models import SampleModels


def calculate_r_factor(
    y_obs: np.ndarray,
    y_calc: np.ndarray,
) -> float:
    """
    Calculate the R-factor (reliability factor) between observed and calculated data.

    Args:
        y_obs: Observed data points.
        y_calc: Calculated data points.

    Returns:
        R-factor value.
    """
    y_obs = np.asarray(y_obs)
    y_calc = np.asarray(y_calc)
    numerator = np.sum(np.abs(y_obs - y_calc))
    denominator = np.sum(np.abs(y_obs))
    return numerator / denominator if denominator != 0 else np.nan


def calculate_weighted_r_factor(
    y_obs: np.ndarray,
    y_calc: np.ndarray,
    weights: np.ndarray,
) -> float:
    """
    Calculate the weighted R-factor between observed and calculated data.

    Args:
        y_obs: Observed data points.
        y_calc: Calculated data points.
        weights: Weights for each data point.

    Returns:
        Weighted R-factor value.
    """
    y_obs = np.asarray(y_obs)
    y_calc = np.asarray(y_calc)
    weights = np.asarray(weights)
    numerator = np.sum(weights * (y_obs - y_calc) ** 2)
    denominator = np.sum(weights * y_obs**2)
    return np.sqrt(numerator / denominator) if denominator != 0 else np.nan


def calculate_rb_factor(
    y_obs: np.ndarray,
    y_calc: np.ndarray,
) -> float:
    """
    Calculate the Bragg R-factor between observed and calculated data.

    Args:
        y_obs: Observed data points.
        y_calc: Calculated data points.

    Returns:
        Bragg R-factor value.
    """
    y_obs = np.asarray(y_obs)
    y_calc = np.asarray(y_calc)
    numerator = np.sum(np.abs(y_obs - y_calc))
    denominator = np.sum(y_obs)
    return numerator / denominator if denominator != 0 else np.nan


def calculate_r_factor_squared(
    y_obs: np.ndarray,
    y_calc: np.ndarray,
) -> float:
    """
    Calculate the R-factor squared between observed and calculated data.

    Args:
        y_obs: Observed data points.
        y_calc: Calculated data points.

    Returns:
        R-factor squared value.
    """
    y_obs = np.asarray(y_obs)
    y_calc = np.asarray(y_calc)
    numerator = np.sum((y_obs - y_calc) ** 2)
    denominator = np.sum(y_obs**2)
    return np.sqrt(numerator / denominator) if denominator != 0 else np.nan


def calculate_reduced_chi_square(
    residuals: np.ndarray,
    num_parameters: int,
) -> float:
    """
    Calculate the reduced chi-square statistic.

    Args:
        residuals: Residuals between observed and calculated data.
        num_parameters: Number of free parameters used in the model.

    Returns:
        Reduced chi-square value.
    """
    residuals = np.asarray(residuals)
    chi_square = np.sum(residuals**2)
    n_points = len(residuals)
    dof = n_points - num_parameters
    if dof > 0:
        return chi_square / dof
    else:
        return np.nan


def get_reliability_inputs(
    sample_models: SampleModels,
    experiments: Experiments,
    calculator: CalculatorBase,
) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
    """
    Collect observed and calculated data points for reliability calculations.

    Args:
        sample_models: Collection of sample models.
        experiments: Collection of experiments.
        calculator: The calculator to use for pattern generation.

    Returns:
        Tuple containing arrays of (observed values, calculated values, error values)
    """
    y_obs_all = []
    y_calc_all = []
    y_err_all = []
    for expt_name, experiment in experiments._items.items():
        y_calc = calculator.calculate_pattern(sample_models, experiment)
        y_meas = experiment.datastore.pattern.meas
        y_meas_su = experiment.datastore.pattern.meas_su

        if y_meas is not None and y_calc is not None:
            # If standard uncertainty is not provided, use ones
            if y_meas_su is None:
                y_meas_su = np.ones_like(y_meas)

            y_obs_all.extend(y_meas)
            y_calc_all.extend(y_calc)
            y_err_all.extend(y_meas_su)

    return (
        np.array(y_obs_all),
        np.array(y_calc_all),
        np.array(y_err_all) if y_err_all else None,
    )
