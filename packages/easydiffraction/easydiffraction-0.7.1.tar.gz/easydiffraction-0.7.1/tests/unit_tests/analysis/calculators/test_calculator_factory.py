from unittest.mock import patch

import pytest

from easydiffraction.analysis.calculators.calculator_crysfml import CrysfmlCalculator
from easydiffraction.analysis.calculators.calculator_cryspy import CryspyCalculator
from easydiffraction.analysis.calculators.calculator_factory import CalculatorFactory
from easydiffraction.analysis.calculators.calculator_pdffit import PdffitCalculator
from easydiffraction.utils.formatting import paragraph


@pytest.fixture
def mock_calculators():
    with (
        patch.object(CrysfmlCalculator, 'engine_imported', True),
        patch.object(CryspyCalculator, 'engine_imported', True),
        patch.object(PdffitCalculator, 'engine_imported', False),
    ):
        yield


def test_supported_calculators(mock_calculators):
    supported = CalculatorFactory._supported_calculators()

    # Assertions
    assert 'crysfml' in supported
    assert 'cryspy' in supported
    assert 'pdffit' not in supported  # Engine not imported


def test_list_supported_calculators(mock_calculators):
    supported_list = CalculatorFactory.list_supported_calculators()

    # Assertions
    assert 'crysfml' in supported_list
    assert 'cryspy' in supported_list
    assert 'pdffit' not in supported_list  # Engine not imported


@patch('builtins.print')
def test_show_supported_calculators(mock_print, mock_calculators):
    CalculatorFactory.show_supported_calculators()

    # Assertions
    mock_print.assert_any_call(paragraph('Supported calculators'))
    assert any('CrysFML library for crystallographic calculations' in call.args[0] for call in mock_print.call_args_list)
    assert any('CrysPy library for crystallographic calculations' in call.args[0] for call in mock_print.call_args_list)


def test_create_calculator(mock_calculators):
    crysfml_calculator = CalculatorFactory.create_calculator('crysfml')
    cryspy_calculator = CalculatorFactory.create_calculator('cryspy')
    pdffit_calculator = CalculatorFactory.create_calculator('pdffit')  # Not supported

    # Assertions
    assert isinstance(crysfml_calculator, CrysfmlCalculator)
    assert isinstance(cryspy_calculator, CryspyCalculator)
    assert pdffit_calculator is None


def test_create_calculator_unknown(mock_calculators):
    unknown_calculator = CalculatorFactory.create_calculator('unknown')

    # Assertions
    assert unknown_calculator is None


def no_test_register_calculator():
    class MockCalculator:
        engine_imported = True

    CalculatorFactory.register_calculator('mock_calculator', MockCalculator, description='Mock calculator for testing')

    supported = CalculatorFactory._supported_calculators()

    # Assertions
    assert 'mock_calculator' in CalculatorFactory._potential_calculators
    assert supported['mock_calculator']['description'] == 'Mock calculator for testing'
    assert supported['mock_calculator']['class'] == MockCalculator
