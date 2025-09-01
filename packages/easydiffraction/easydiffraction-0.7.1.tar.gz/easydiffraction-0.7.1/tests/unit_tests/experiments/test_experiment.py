from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from easydiffraction.core.constants import DEFAULT_BEAM_MODE
from easydiffraction.core.constants import DEFAULT_RADIATION_PROBE
from easydiffraction.core.constants import DEFAULT_SAMPLE_FORM
from easydiffraction.core.constants import DEFAULT_SCATTERING_TYPE
from easydiffraction.experiments.components.experiment_type import ExperimentType
from easydiffraction.experiments.experiment import BaseExperiment
from easydiffraction.experiments.experiment import Experiment
from easydiffraction.experiments.experiment import ExperimentFactory
from easydiffraction.experiments.experiment import PowderExperiment
from easydiffraction.experiments.experiment import SingleCrystalExperiment


@pytest.fixture
def expt_type():
    return ExperimentType(
        sample_form=DEFAULT_SAMPLE_FORM, beam_mode=DEFAULT_BEAM_MODE, radiation_probe='xray', scattering_type='bragg'
    )


class ConcreteBaseExperiment(BaseExperiment):
    """Concrete implementation of BaseExperiment for testing."""

    def _load_ascii_data_to_experiment(self, data_path):
        pass

    def show_meas_chart(self, x_min=None, x_max=None):
        pass


class ConcreteSingleCrystalExperiment(SingleCrystalExperiment):
    """Concrete implementation of SingleCrystalExperiment for testing."""

    def _load_ascii_data_to_experiment(self, data_path):
        pass


def test_base_experiment_initialization(expt_type):
    experiment = ConcreteBaseExperiment(name='TestExperiment', type=expt_type)
    assert experiment.name == 'TestExperiment'
    assert experiment.type == expt_type


def test_powder_experiment_initialization(expt_type):
    experiment = PowderExperiment(name='PowderTest', type=expt_type)
    assert experiment.name == 'PowderTest'
    assert experiment.type == expt_type
    assert experiment.background is not None
    assert experiment.peak is not None
    assert experiment.linked_phases is not None


def test_powder_experiment_load_ascii_data(expt_type):
    experiment = PowderExperiment(name='PowderTest', type=expt_type)
    experiment.datastore = MagicMock()
    experiment.datastore.pattern = MagicMock()
    mock_data = np.array([[1.0, 2.0, 0.1], [2.0, 3.0, 0.2]])
    with patch('numpy.loadtxt', return_value=mock_data):
        experiment._load_ascii_data_to_experiment('mock_path')
    assert np.array_equal(experiment.datastore.pattern.x, mock_data[:, 0])
    assert np.array_equal(experiment.datastore.pattern.meas, mock_data[:, 1])
    assert np.array_equal(experiment.datastore.pattern.meas_su, mock_data[:, 2])


def test_single_crystal_experiment_initialization(expt_type):
    experiment = ConcreteSingleCrystalExperiment(name='SingleCrystalTest', type=expt_type)
    assert experiment.name == 'SingleCrystalTest'
    assert experiment.type == expt_type
    assert experiment.linked_crystal is None


def test_single_crystal_experiment_show_meas_chart(expt_type):
    experiment = ConcreteSingleCrystalExperiment(name='SingleCrystalTest', type=expt_type)
    with patch('builtins.print') as mock_print:
        experiment.show_meas_chart()
        mock_print.assert_called_once_with('Showing measured data chart is not implemented yet.')


def test_experiment_factory_create_powder():
    experiment = ExperimentFactory.create(
        name='PowderTest',
        sample_form='powder',
        beam_mode=DEFAULT_BEAM_MODE,
        radiation_probe=DEFAULT_RADIATION_PROBE,
        scattering_type=DEFAULT_SCATTERING_TYPE,
    )
    assert isinstance(experiment, PowderExperiment)
    assert experiment.name == 'PowderTest'


# to be added once single crystal works
def no_test_experiment_factory_create_single_crystal():
    experiment = ExperimentFactory.create(
        name='SingleCrystalTest',
        sample_form='single crystal',
        beam_mode=DEFAULT_BEAM_MODE,
        radiation_probe=DEFAULT_RADIATION_PROBE,
    )
    assert isinstance(experiment, SingleCrystalExperiment)
    assert experiment.name == 'SingleCrystalTest'


def test_experiment_method():
    mock_data = np.array([[1.0, 2.0, 0.1], [2.0, 3.0, 0.2]])
    with patch('numpy.loadtxt', return_value=mock_data):
        experiment = Experiment(
            name='ExperimentTest',
            sample_form='powder',
            beam_mode=DEFAULT_BEAM_MODE,
            radiation_probe=DEFAULT_RADIATION_PROBE,
            data_path='mock_path',
        )
    assert isinstance(experiment, PowderExperiment)
    assert experiment.name == 'ExperimentTest'
    assert np.array_equal(experiment.datastore.pattern.x, mock_data[:, 0])
    assert np.array_equal(experiment.datastore.pattern.meas, mock_data[:, 1])
    assert np.array_equal(experiment.datastore.pattern.meas_su, mock_data[:, 2])
