from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from easydiffraction.experiments.experiment import BaseExperiment
from easydiffraction.experiments.experiments import Experiments


class ConcreteBaseExperiment(BaseExperiment):
    """Concrete implementation of BaseExperiment for testing."""

    def _load_ascii_data_to_experiment(self, data_path):
        pass

    def show_meas_chart(self, x_min=None, x_max=None):
        pass


def test_experiments_initialization():
    experiments = Experiments()
    assert isinstance(experiments, Experiments)
    assert len(experiments.ids) == 0


def test_experiments_add_prebuilt_experiment():
    experiments = Experiments()
    mock_experiment = MagicMock(spec=BaseExperiment)
    mock_experiment.name = 'TestExperiment'

    experiments.add(experiment=mock_experiment)
    assert 'TestExperiment' in experiments.ids
    assert experiments._experiments['TestExperiment'] == mock_experiment


def test_experiments_add_from_data_path():
    experiments = Experiments()
    mock_experiment = MagicMock(spec=ConcreteBaseExperiment)
    mock_experiment.name = 'TestExperiment'

    with patch('easydiffraction.experiments.experiment.ExperimentFactory.create', return_value=mock_experiment):
        experiments.add(
            name='TestExperiment',
            sample_form='powder',
            beam_mode='default',
            radiation_probe='x-ray',
            data_path='mock_path',
        )

    assert 'TestExperiment' in experiments.ids
    assert experiments._experiments['TestExperiment'] == mock_experiment
    mock_experiment._load_ascii_data_to_experiment.assert_called_once_with('mock_path')


def test_experiments_add_invalid_input():
    experiments = Experiments()

    with pytest.raises(ValueError, match='Provide either experiment, type parameters, cif_path, cif_str, or data_path'):
        experiments.add()


def test_experiments_remove():
    experiments = Experiments()
    mock_experiment = MagicMock(spec=BaseExperiment)
    mock_experiment.name = 'TestExperiment'

    experiments.add(experiment=mock_experiment)
    assert 'TestExperiment' in experiments.ids

    experiments.remove('TestExperiment')
    assert 'TestExperiment' not in experiments.ids


def test_experiments_show_names(capsys):
    experiments = Experiments()
    mock_experiment = MagicMock(spec=BaseExperiment)
    mock_experiment.name = 'TestExperiment'

    experiments.add(experiment=mock_experiment)
    experiments.show_names()

    captured = capsys.readouterr()
    assert 'Defined experiments 🔬' in captured.out
    assert 'TestExperiment' in captured.out


def test_experiments_as_cif():
    experiments = Experiments()
    mock_experiment = MagicMock(spec=BaseExperiment)
    mock_experiment.name = 'TestExperiment'
    mock_experiment.as_cif.return_value = 'mock_cif_content'

    experiments.add(experiment=mock_experiment)
    cif_output = experiments.as_cif()

    assert 'mock_cif_content' in cif_output
