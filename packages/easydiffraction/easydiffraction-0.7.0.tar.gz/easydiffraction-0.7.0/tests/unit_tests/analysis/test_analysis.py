from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from easydiffraction.analysis.analysis import Analysis


@pytest.fixture
def mock_project():
    project = MagicMock()
    project.sample_models.get_all_params.return_value = [
        MagicMock(
            datablock_id='block1',
            category_key='cat1',
            collection_entry_id='entry1',
            name='param1',
            value=1.0,
            units='unit1',
            free=True,
            min=0.0,
            max=2.0,
            uncertainty=0.1,
        )
    ]
    project.experiments.get_all_params.return_value = [
        MagicMock(
            datablock_id='block2',
            category_key='cat2',
            collection_entry_id='entry2',
            name='param2',
            value=2.0,
            units='unit2',
            free=False,
            min=1.0,
            max=3.0,
            uncertainty=0.2,
        )
    ]
    project.sample_models.get_fittable_params.return_value = project.sample_models.get_all_params()
    project.experiments.get_fittable_params.return_value = project.experiments.get_all_params()
    project.sample_models.get_free_params.return_value = project.sample_models.get_all_params()
    project.experiments.get_free_params.return_value = project.experiments.get_all_params()
    project.experiments.ids = ['experiment1', 'experiment2']
    project._varname = 'project'
    return project


@pytest.fixture
def analysis(mock_project):
    return Analysis(project=mock_project)


# @patch("builtins.print")
# def test_show_all_params(mock_print, analysis):
#    analysis._show_params = MagicMock()
#    analysis.show_all_params()
#
#    # Assertions
#    assert('parameters for all experiments' in mock_print.call_args[0][0])
#
# @patch("builtins.print")
# def test_show_fittable_params(mock_print, analysis):
#    analysis._show_params = MagicMock()
#    analysis.show_fittable_params()
#
#    # Assertions
#    assert('Fittable parameters for all experiments' in mock_print.call_args[0][0])
#
# @patch("builtins.print")
# def test_show_free_params(mock_print, analysis):
#    analysis._show_params = MagicMock()
#    analysis.show_free_params()
#
#    # Assertions
#    assert('Free parameters for both sample models' in mock_print.call_args[0][0])
#    # mock_print.assert_any_call("Free parameters for both sample models (🧩 data blocks) and experiments (🔬 data blocks)")


@patch('builtins.print')
def test_show_current_calculator(mock_print, analysis):
    analysis.show_current_calculator()

    # Assertions
    # mock_print.assert_any_call("Current calculator")
    mock_print.assert_any_call('cryspy')


@patch('builtins.print')
def test_show_current_minimizer(mock_print, analysis):
    analysis.show_current_minimizer()

    # Assertions
    # mock_print.assert_any_call("Current minimizer")
    mock_print.assert_any_call('lmfit (leastsq)')


@patch('easydiffraction.analysis.calculators.calculator_factory.CalculatorFactory.create_calculator')
@patch('builtins.print')
def test_current_calculator_setter(mock_print, mock_create_calculator, analysis):
    mock_create_calculator.return_value = MagicMock()

    analysis.current_calculator = 'pdffit2'

    # Assertions
    mock_create_calculator.assert_called_once_with('pdffit2')


@patch('easydiffraction.analysis.minimizers.minimizer_factory.MinimizerFactory.create_minimizer')
@patch('builtins.print')
def test_current_minimizer_setter(mock_print, mock_create_minimizer, analysis):
    mock_create_minimizer.return_value = MagicMock()

    analysis.current_minimizer = 'dfols'

    # Assertions
    mock_print.assert_any_call('dfols')


@patch('builtins.print')
def test_fit_mode_setter(mock_print, analysis):
    analysis.fit_mode = 'joint'

    # Assertions
    assert analysis.fit_mode == 'joint'
    mock_print.assert_any_call('joint')


@patch('easydiffraction.analysis.minimization.DiffractionMinimizer.fit')
@patch('builtins.print')
def no_test_fit_single_mode(mock_print, mock_fit, analysis, mock_project):
    analysis.fit_mode = 'single'
    analysis.fit()

    # Assertions
    mock_fit.assert_called()
    mock_print.assert_any_call('single')


@patch('easydiffraction.analysis.minimization.DiffractionMinimizer.fit')
@patch('builtins.print')
def test_fit_joint_mode(mock_print, mock_fit, analysis, mock_project):
    analysis.fit_mode = 'joint'
    analysis.fit()

    # Assertions
    mock_fit.assert_called_once()


@patch('builtins.print')
def test_as_cif(mock_print, analysis):
    cif_text = analysis.as_cif()

    # Assertions
    assert '_analysis.calculator_engine  cryspy' in cif_text
    assert '_analysis.fitting_engine  "lmfit (leastsq)"' in cif_text
    assert '_analysis.fit_mode  single' in cif_text
