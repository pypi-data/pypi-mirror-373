# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Type
from typing import Union

import numpy as np
from numpy.polynomial.chebyshev import chebval
from scipy.interpolate import interp1d

from easydiffraction.core.constants import DEFAULT_BACKGROUND_TYPE
from easydiffraction.core.objects import Collection
from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Descriptor
from easydiffraction.core.objects import Parameter
from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.formatting import warning
from easydiffraction.utils.utils import render_table


# TODO: rename to LineSegment
class Point(Component):
    @property
    def category_key(self) -> str:
        return 'background'

    @property
    def cif_category_key(self) -> str:
        return 'pd_background'

    def __init__(self, x: float, y: float):
        super().__init__()

        self.x = Descriptor(
            value=x,
            name='x',
            cif_name='line_segment_X',
            description='X-coordinates used to create many straight-line segments representing the background in a '
            'calculated diffractogram.',
        )
        self.y = Parameter(
            value=y,  # TODO: rename to intensity
            name='y',  # TODO: rename to intensity
            cif_name='line_segment_intensity',
            description='Intensity used to create many straight-line segments representing the background in a calculated '
            'diffractogram',
        )

        # Select which of the input parameters is used for the
        # as ID for the whole object
        self._entry_id = str(x)

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked = True


class PolynomialTerm(Component):
    # TODO: make consistency in where to place the following properties:
    #  before or after the __init__ method
    @property
    def category_key(self) -> str:
        return 'background'

    @property
    def cif_category_key(self):
        return 'pd_background'

    def __init__(self, order: int, coef: float) -> None:
        super().__init__()

        self.order = Descriptor(
            value=order,
            name='chebyshev_order',
            cif_name='Chebyshev_order',
            description='The value of an order used in a Chebyshev polynomial equation representing the background in a '
            'calculated diffractogram',
        )
        self.coef = Parameter(
            value=coef,
            name='chebyshev_coef',
            cif_name='Chebyshev_coef',
            description='The value of a coefficient used in a Chebyshev polynomial equation representing the background in a '
            'calculated diffractogram',
        )

        # Select which of the input parameters is used for the
        # as ID for the whole object
        self._entry_id = str(order)

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked = True


class BackgroundBase(Collection):
    @property
    def _type(self) -> str:
        return 'category'  # datablock or category

    @abstractmethod
    def calculate(self, x_data: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def show(self) -> None:
        pass


class LineSegmentBackground(BackgroundBase):
    _description: str = 'Linear interpolation between points'

    @property
    def _child_class(self) -> Type[Point]:
        return Point

    def calculate(self, x_data: np.ndarray) -> np.ndarray:
        """Interpolate background points over x_data."""
        if not self._items:
            print(warning('No background points found. Setting background to zero.'))
            return np.zeros_like(x_data)

        background_x = np.array([point.x.value for point in self._items.values()])
        background_y = np.array([point.y.value for point in self._items.values()])
        interp_func = interp1d(
            background_x,
            background_y,
            kind='linear',
            bounds_error=False,
            fill_value=(
                background_y[0],
                background_y[-1],
            ),
        )
        y_data = interp_func(x_data)
        return y_data

    def show(self) -> None:
        columns_headers: List[str] = ['X', 'Intensity']
        columns_alignment = ['left', 'left']
        columns_data: List[List[float]] = []
        for point in self._items.values():
            x = point.x.value
            y = point.y.value
            columns_data.append([x, y])

        print(paragraph('Line-segment background points'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=columns_data,
        )


class ChebyshevPolynomialBackground(BackgroundBase):
    _description: str = 'Chebyshev polynomial background'

    @property
    def _child_class(self) -> Type[PolynomialTerm]:
        return PolynomialTerm

    def calculate(self, x_data: np.ndarray) -> np.ndarray:
        """Evaluate polynomial background over x_data."""
        if not self._items:
            print(warning('No background points found. Setting background to zero.'))
            return np.zeros_like(x_data)

        u = (x_data - x_data.min()) / (x_data.max() - x_data.min()) * 2 - 1  # scale to [-1, 1]
        coefs = [term.coef.value for term in self._items.values()]
        y_data = chebval(u, coefs)
        return y_data

    def show(self) -> None:
        columns_headers: List[str] = ['Order', 'Coefficient']
        columns_alignment = ['left', 'left']
        columns_data: List[List[Union[int, float]]] = []
        for term in self._items.values():
            order = term.order.value
            coef = term.coef.value
            columns_data.append([order, coef])

        print(paragraph('Chebyshev polynomial background terms'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=columns_data,
        )


class BackgroundFactory:
    _supported: Dict[str, Type[BackgroundBase]] = {
        'line-segment': LineSegmentBackground,
        'chebyshev polynomial': ChebyshevPolynomialBackground,
    }

    @classmethod
    def create(
        cls,
        background_type: str = DEFAULT_BACKGROUND_TYPE,
    ) -> BackgroundBase:
        if background_type not in cls._supported:
            supported_types = list(cls._supported.keys())

            raise ValueError(
                f"Unsupported background type: '{background_type}'.\n Supported background types: {supported_types}"
            )

        background_class = cls._supported[background_type]
        return background_class()
