from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from easydiffraction.sample_models.sample_models import SampleModel
from easydiffraction.sample_models.sample_models import SampleModels


@pytest.fixture
def mock_sample_model():
    with (
        patch('easydiffraction.sample_models.components.space_group.SpaceGroup') as MockSpaceGroup,
        patch('easydiffraction.sample_models.components.cell.Cell') as MockCell,
        patch('easydiffraction.sample_models.collections.atom_sites.AtomSites') as MockAtomSites,
    ):
        space_group = MockSpaceGroup.return_value
        cell = MockCell.return_value
        atom_sites = MockAtomSites.return_value

        # Mock attributes
        space_group.name_h_m.value = 'P 1'
        space_group.it_coordinate_system_code.value = 1
        cell.length_a.value = 1.0
        cell.length_b.value = 2.0
        cell.length_c.value = 3.0
        cell.angle_alpha.value = 90.0
        cell.angle_beta.value = 90.0
        cell.angle_gamma.value = 90.0
        atom_sites.__iter__.return_value = []

        return SampleModel(name='test_model')


@pytest.fixture
def mock_sample_models():
    return SampleModels()


def test_sample_models_add(mock_sample_models, mock_sample_model):
    mock_sample_models.add(model=mock_sample_model)

    # Assertions
    assert 'test_model' in mock_sample_models.get_ids()


def test_sample_models_remove(mock_sample_models, mock_sample_model):
    mock_sample_models.add(model=mock_sample_model)
    mock_sample_models.remove('test_model')

    # Assertions
    assert 'test_model' not in mock_sample_models.get_ids()


def test_sample_models_as_cif(mock_sample_models, mock_sample_model):
    mock_sample_model.as_cif = MagicMock(return_value='data_test_model')
    mock_sample_models.add(model=mock_sample_model)

    cif = mock_sample_models.as_cif()

    # Assertions
    assert 'data_test_model' in cif


@patch('builtins.print')
def test_sample_models_show_names(mock_print, mock_sample_models, mock_sample_model):
    mock_sample_models.add(model=mock_sample_model)
    mock_sample_models.show_names()

    # Assertions
    mock_print.assert_called_with(['test_model'])


@patch.object(SampleModel, 'show_params', autospec=True)
def test_sample_models_show_params(mock_show_params, mock_sample_models, mock_sample_model):
    mock_sample_models.add(model=mock_sample_model)
    mock_sample_models.show_params()

    # Assertions
    mock_show_params.assert_called_once_with(mock_sample_model)
