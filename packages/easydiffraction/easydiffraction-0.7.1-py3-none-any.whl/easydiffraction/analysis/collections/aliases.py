# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Type

from easydiffraction.core.objects import Collection
from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Descriptor


class Alias(Component):
    @property
    def category_key(self) -> str:
        return 'alias'

    @property
    def cif_category_key(self) -> str:
        return 'alias'

    def __init__(self, label: str, param_uid: str) -> None:
        super().__init__()

        self.label: Descriptor = Descriptor(
            value=label,
            name='label',
            cif_name='label',
        )
        self.param_uid: Descriptor = Descriptor(
            value=param_uid,
            name='param_uid',
            cif_name='param_uid',
        )

        # Select which of the input parameters is used for the
        # as ID for the whole object
        self._entry_id = label

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked = True


class Aliases(Collection):
    @property
    def _type(self) -> str:
        return 'category'  # datablock or category

    @property
    def _child_class(self) -> Type[Alias]:
        return Alias
