# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Type

from easydiffraction.core.objects import Collection
from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Descriptor


class JointFitExperiment(Component):
    @property
    def category_key(self) -> str:
        return 'joint_fit_experiment'

    @property
    def cif_category_key(self) -> str:
        return 'joint_fit_experiment'

    def __init__(self, id: str, weight: float) -> None:
        super().__init__()

        self.id: Descriptor = Descriptor(
            value=id,
            name='id',
            cif_name='id',
        )
        self.weight: Descriptor = Descriptor(
            value=weight,
            name='weight',
            cif_name='weight',
        )

        # Select which of the input parameters is used for the
        # as ID for the whole object
        self._entry_id = id

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked = True


class JointFitExperiments(Collection):
    """
    Collection manager for experiments that are fitted together
    in a `joint` fit.
    """

    @property
    def _type(self) -> str:
        return 'category'  # datablock or category

    @property
    def _child_class(self) -> Type[JointFitExperiment]:
        return JointFitExperiment
