# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Type

from easydiffraction.core.objects import Collection
from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Descriptor
from easydiffraction.core.objects import Parameter


class LinkedPhase(Component):
    @property
    def category_key(self) -> str:
        return 'linked_phases'

    @property
    def cif_category_key(self) -> str:
        return 'pd_phase_block'

    def __init__(self, id: str, scale: float):
        super().__init__()

        self.id = Descriptor(
            value=id,
            name='id',
            cif_name='id',
        )
        self.scale = Parameter(
            value=scale,
            name='scale',
            cif_name='scale',
        )

        # Select which of the input parameters is used for the
        # as ID for the whole object
        self._entry_id = id

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked = True


class LinkedPhases(Collection):
    """
    Collection of LinkedPhase instances.
    """

    @property
    def _type(self) -> str:
        return 'category'  # datablock or category

    @property
    def _child_class(self) -> Type[LinkedPhase]:
        return LinkedPhase
