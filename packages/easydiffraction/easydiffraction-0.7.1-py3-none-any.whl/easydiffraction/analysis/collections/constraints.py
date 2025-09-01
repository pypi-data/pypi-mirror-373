# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Type

from easydiffraction.core.objects import Collection
from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Descriptor


class Constraint(Component):
    @property
    def category_key(self) -> str:
        return 'constraint'

    @property
    def cif_category_key(self) -> str:
        return 'constraint'

    def __init__(self, lhs_alias: str, rhs_expr: str) -> None:
        super().__init__()

        self.lhs_alias: Descriptor = Descriptor(
            value=lhs_alias,
            name='lhs_alias',
            cif_name='lhs_alias',
        )
        self.rhs_expr: Descriptor = Descriptor(
            value=rhs_expr,
            name='rhs_expr',
            cif_name='rhs_expr',
        )

        # Select which of the input parameters is used for the
        # as ID for the whole object
        self._entry_id = lhs_alias

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked = True


class Constraints(Collection):
    @property
    def _type(self) -> str:
        return 'category'  # datablock or category

    @property
    def _child_class(self) -> Type[Constraint]:
        return Constraint
