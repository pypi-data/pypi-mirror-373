from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from easydiffraction.experiments.collections.datastore import Datastore
from easydiffraction.experiments.collections.datastore import DatastoreFactory
from easydiffraction.experiments.collections.datastore import Pattern
from easydiffraction.experiments.collections.datastore import PowderPattern


def test_pattern_initialization():
    mock_experiment = MagicMock()
    pattern = Pattern(experiment=mock_experiment)

    assert pattern.experiment == mock_experiment
    assert pattern.x is None
    assert pattern.meas is None
    assert pattern.meas_su is None
    assert pattern.bkg is None
    assert pattern.calc is None


def test_pattern_calc_property():
    mock_experiment = MagicMock()
    pattern = Pattern(experiment=mock_experiment)

    # Test calc setter and getter
    pattern.calc = [1, 2, 3]
    assert pattern.calc == [1, 2, 3]


def test_powder_pattern_initialization():
    mock_experiment = MagicMock()
    powder_pattern = PowderPattern(experiment=mock_experiment)

    assert powder_pattern.experiment == mock_experiment
    assert isinstance(powder_pattern, Pattern)


def test_datastore_initialization_powder():
    mock_experiment = MagicMock()
    datastore = Datastore(sample_form='powder', experiment=mock_experiment)

    assert datastore.sample_form == 'powder'
    assert isinstance(datastore.pattern, PowderPattern)


def test_datastore_initialization_single_crystal():
    mock_experiment = MagicMock()
    datastore = Datastore(sample_form='single_crystal', experiment=mock_experiment)

    assert datastore.sample_form == 'single_crystal'
    assert isinstance(datastore.pattern, Pattern)


def test_datastore_initialization_invalid_sample_form():
    mock_experiment = MagicMock()
    with pytest.raises(ValueError, match="Unknown sample form 'invalid'"):
        Datastore(sample_form='invalid', experiment=mock_experiment)


def test_datastore_load_measured_data_valid():
    mock_experiment = MagicMock()
    mock_experiment.name = 'TestExperiment'
    datastore = Datastore(sample_form='powder', experiment=mock_experiment)

    mock_data = np.array([[1.0, 2.0, 0.1], [2.0, 3.0, 0.2]])
    with patch('numpy.loadtxt', return_value=mock_data):
        datastore.load_measured_data('mock_path')

    assert np.array_equal(datastore.pattern.x, mock_data[:, 0])
    assert np.array_equal(datastore.pattern.meas, mock_data[:, 1])
    assert np.array_equal(datastore.pattern.meas_su, mock_data[:, 2])


def test_datastore_load_measured_data_no_uncertainty():
    mock_experiment = MagicMock()
    mock_experiment.name = 'TestExperiment'
    datastore = Datastore(sample_form='powder', experiment=mock_experiment)

    mock_data = np.array([[1.0, 2.0], [2.0, 3.0]])
    with patch('numpy.loadtxt', return_value=mock_data):
        datastore.load_measured_data('mock_path')

    assert np.array_equal(datastore.pattern.x, mock_data[:, 0])
    assert np.array_equal(datastore.pattern.meas, mock_data[:, 1])
    assert np.array_equal(datastore.pattern.meas_su, np.sqrt(np.abs(mock_data[:, 1])))


def test_datastore_load_measured_data_invalid_file():
    mock_experiment = MagicMock()
    datastore = Datastore(sample_form='powder', experiment=mock_experiment)

    with patch('numpy.loadtxt', side_effect=Exception('File not found')):
        datastore.load_measured_data('invalid_path')


def test_datastore_show_measured_data(capsys):
    mock_experiment = MagicMock()
    datastore = Datastore(sample_form='powder', experiment=mock_experiment)

    datastore.pattern.x = [1.0, 2.0, 3.0]
    datastore.pattern.meas = [10.0, 20.0, 30.0]
    datastore.pattern.meas_su = [0.1, 0.2, 0.3]

    datastore.show_measured_data()
    captured = capsys.readouterr()

    assert 'Measured data (powder):' in captured.out
    assert 'x: [1.0, 2.0, 3.0]' in captured.out
    assert 'meas: [10.0, 20.0, 30.0]' in captured.out
    assert 'meas_su: [0.1, 0.2, 0.3]' in captured.out


def test_datastore_show_calculated_data(capsys):
    mock_experiment = MagicMock()
    datastore = Datastore(sample_form='powder', experiment=mock_experiment)

    datastore.pattern.calc = [100.0, 200.0, 300.0]

    datastore.show_calculated_data()
    captured = capsys.readouterr()

    assert 'Calculated data (powder):' in captured.out
    assert 'calc: [100.0, 200.0, 300.0]' in captured.out


def test_datastore_factory_create_powder():
    mock_experiment = MagicMock()
    datastore = DatastoreFactory.create(sample_form='powder', experiment=mock_experiment)

    assert isinstance(datastore, Datastore)
    assert datastore.sample_form == 'powder'
    assert isinstance(datastore.pattern, PowderPattern)


def test_datastore_factory_create_single_crystal():
    mock_experiment = MagicMock()
    datastore = DatastoreFactory.create(sample_form='single_crystal', experiment=mock_experiment)

    assert isinstance(datastore, Datastore)
    assert datastore.sample_form == 'single_crystal'
    assert isinstance(datastore.pattern, Pattern)


def test_datastore_factory_create_invalid_sample_form():
    mock_experiment = MagicMock()
    with pytest.raises(ValueError, match="Unknown sample form 'invalid'"):
        DatastoreFactory.create(sample_form='invalid', experiment=mock_experiment)
