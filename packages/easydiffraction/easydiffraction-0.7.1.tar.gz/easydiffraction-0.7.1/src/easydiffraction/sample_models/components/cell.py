# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Parameter


class Cell(Component):
    """
    Represents the unit cell parameters of a sample model.
    """

    @property
    def category_key(self) -> str:
        return 'cell'

    @property
    def cif_category_key(self) -> str:
        return 'cell'

    def __init__(
        self,
        length_a: float = 10.0,
        length_b: float = 10.0,
        length_c: float = 10.0,
        angle_alpha: float = 90.0,
        angle_beta: float = 90.0,
        angle_gamma: float = 90.0,
    ) -> None:
        super().__init__()

        self.length_a = Parameter(
            value=length_a,
            name='length_a',
            cif_name='length_a',
            units='Å',
        )
        self.length_b = Parameter(
            value=length_b,
            name='length_b',
            cif_name='length_b',
            units='Å',
        )
        self.length_c = Parameter(
            value=length_c,
            name='length_c',
            cif_name='length_c',
            units='Å',
        )
        self.angle_alpha = Parameter(
            value=angle_alpha,
            name='angle_alpha',
            cif_name='angle_alpha',
            units='deg',
        )
        self.angle_beta = Parameter(
            value=angle_beta,
            name='angle_beta',
            cif_name='angle_beta',
            units='deg',
        )
        self.angle_gamma = Parameter(
            value=angle_gamma,
            name='angle_gamma',
            cif_name='angle_gamma',
            units='deg',
        )

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked: bool = True
