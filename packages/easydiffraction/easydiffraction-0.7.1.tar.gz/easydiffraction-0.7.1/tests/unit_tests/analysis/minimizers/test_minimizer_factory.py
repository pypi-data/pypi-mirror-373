from unittest.mock import patch

import pytest

from easydiffraction.analysis.minimizers.minimizer_dfols import DfolsMinimizer
from easydiffraction.analysis.minimizers.minimizer_factory import MinimizerFactory
from easydiffraction.analysis.minimizers.minimizer_lmfit import LmfitMinimizer


def test_list_available_minimizers():
    minimizers = MinimizerFactory.list_available_minimizers()

    # Assertions
    assert isinstance(minimizers, list)
    assert 'lmfit' in minimizers
    assert 'dfols' in minimizers


@patch('builtins.print')
def test_show_available_minimizers(mock_print):
    MinimizerFactory.show_available_minimizers()

    # Assertions
    # mock_print.assert_any_call("Available minimizers")
    assert any(
        'LMFIT library using the default Levenberg-Marquardt least squares method' in call.args[0]
        for call in mock_print.call_args_list
    )
    assert any(
        'DFO-LS library for derivative-free least-squares optimization' in call.args[0] for call in mock_print.call_args_list
    )


def test_create_minimizer():
    # Test creating an LmfitMinimizer
    minimizer = MinimizerFactory.create_minimizer('lmfit')
    assert isinstance(minimizer, LmfitMinimizer)
    assert minimizer.method == 'leastsq'

    # Test creating a DfolsMinimizer
    minimizer = MinimizerFactory.create_minimizer('dfols')
    assert isinstance(minimizer, DfolsMinimizer)
    assert minimizer.method is None

    # Test invalid minimizer
    with pytest.raises(ValueError, match="Unknown minimizer 'invalid'.*"):
        MinimizerFactory.create_minimizer('invalid')


def test_register_minimizer():
    class MockMinimizer:
        def __init__(self, method=None):
            self.method = method

    MinimizerFactory.register_minimizer(
        name='mock_minimizer', minimizer_cls=MockMinimizer, method='mock_method', description='Mock minimizer for testing'
    )

    # Assertions
    minimizers = MinimizerFactory.list_available_minimizers()
    assert 'mock_minimizer' in minimizers

    # Test creating the registered minimizer
    minimizer = MinimizerFactory.create_minimizer('mock_minimizer')
    assert isinstance(minimizer, MockMinimizer)
    assert minimizer.method == 'mock_method'
