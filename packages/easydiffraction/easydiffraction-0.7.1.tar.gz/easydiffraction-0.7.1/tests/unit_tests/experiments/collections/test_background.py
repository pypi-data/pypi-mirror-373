from unittest.mock import patch

import numpy as np
import pytest

from easydiffraction.experiments.collections.background import BackgroundFactory
from easydiffraction.experiments.collections.background import ChebyshevPolynomialBackground
from easydiffraction.experiments.collections.background import LineSegmentBackground
from easydiffraction.experiments.collections.background import Point
from easydiffraction.experiments.collections.background import PolynomialTerm


def test_point_initialization():
    point = Point(x=1.0, y=2.0)
    assert point.x.value == 1.0
    assert point.y.value == 2.0
    assert point.cif_category_key == 'pd_background'
    assert point.category_key == 'background'
    assert point._entry_id == '1.0'


def test_polynomial_term_initialization():
    term = PolynomialTerm(order=2, coef=3.0)
    assert term.order.value == 2
    assert term.coef.value == 3.0
    assert term.cif_category_key == 'pd_background'
    assert term.category_key == 'background'
    assert term._entry_id == '2'


def test_line_segment_background_add_and_calculate():
    background = LineSegmentBackground()
    background.add(1.0, 2.0)
    background.add(3.0, 4.0)

    x_data = np.array([1.0, 2.0, 3.0])
    y_data = background.calculate(x_data)

    assert np.array_equal(y_data, np.array([2.0, 3.0, 4.0]))


def test_line_segment_background_calculate_no_points():
    background = LineSegmentBackground()
    x_data = np.array([1.0, 2.0, 3.0])

    with patch('builtins.print') as mock_print:
        y_data = background.calculate(x_data)
        assert np.array_equal(y_data, np.zeros_like(x_data))
        assert 'No background points found. Setting background to zero.' in str(mock_print.call_args.args[0])


def test_line_segment_background_show(capsys):
    background = LineSegmentBackground()
    background.add(1.0, 2.0)
    background.add(3.0, 4.0)

    background.show()
    captured = capsys.readouterr()
    assert 'Line-segment background points' in captured.out


def test_chebyshev_polynomial_background_add_and_calculate():
    background = ChebyshevPolynomialBackground()
    background.add(order=0, coef=1.0)
    background.add(order=1, coef=2.0)

    x_data = np.array([0.0, 0.5, 1.0])
    y_data = background.calculate(x_data)

    # Expected values are calculated using the Chebyshev polynomial formula
    u = (x_data - x_data.min()) / (x_data.max() - x_data.min()) * 2 - 1
    expected_y = 1.0 + 2.0 * u
    assert np.allclose(y_data, expected_y)


def test_chebyshev_polynomial_background_calculate_no_terms():
    background = ChebyshevPolynomialBackground()
    x_data = np.array([0.0, 0.5, 1.0])

    with patch('builtins.print') as mock_print:
        y_data = background.calculate(x_data)
        assert np.array_equal(y_data, np.zeros_like(x_data))
        assert 'No background points found. Setting background to zero.' in str(mock_print.call_args.args[0])


def test_chebyshev_polynomial_background_show(capsys):
    background = ChebyshevPolynomialBackground()
    background.add(order=0, coef=1.0)
    background.add(order=1, coef=2.0)

    background.show()
    captured = capsys.readouterr()
    assert 'Chebyshev polynomial background terms' in captured.out


def test_background_factory_create_supported_types():
    line_segment_background = BackgroundFactory.create('line-segment')
    assert isinstance(line_segment_background, LineSegmentBackground)

    chebyshev_background = BackgroundFactory.create('chebyshev polynomial')
    assert isinstance(chebyshev_background, ChebyshevPolynomialBackground)


def test_background_factory_create_unsupported_type():
    with pytest.raises(ValueError, match="Unsupported background type: 'unsupported'.*"):
        BackgroundFactory.create('unsupported')
