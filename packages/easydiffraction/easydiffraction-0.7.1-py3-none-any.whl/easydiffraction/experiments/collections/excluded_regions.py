# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import List
from typing import Type

from easydiffraction.core.objects import Collection
from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Descriptor
from easydiffraction.core.objects import Parameter
from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.utils import render_table


class ExcludedRegion(Component):
    @property
    def category_key(self) -> str:
        return 'excluded_regions'

    @property
    def cif_category_key(self) -> str:
        return 'excluded_region'

    def __init__(self, start: float, end: float):
        super().__init__()

        self.start = Descriptor(
            value=start,
            name='start',
            cif_name='start',
        )
        self.end = Parameter(
            value=end,
            name='end',
            cif_name='end',
        )

        # Select which of the input parameters is used for the
        # as ID for the whole object
        self._entry_id = f'{start}-{end}'

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked = True


class ExcludedRegions(Collection):
    """
    Collection of ExcludedRegion instances.
    """

    @property
    def _type(self) -> str:
        return 'category'  # datablock or category

    @property
    def _child_class(self) -> Type[ExcludedRegion]:
        return ExcludedRegion

    def on_item_added(self, item: ExcludedRegion) -> None:
        """
        Mark excluded points in the experiment pattern when a new region is added.
        """
        experiment = self._parent
        pattern = experiment.datastore.pattern

        # Boolean mask for points within the new excluded region
        in_region = (pattern.full_x >= item.start.value) & (pattern.full_x <= item.end.value)

        # Update the exclusion mask
        pattern.excluded[in_region] = True

        # Update the excluded points in the datastore
        pattern.x = pattern.full_x[~pattern.excluded]
        pattern.meas = pattern.full_meas[~pattern.excluded]
        pattern.meas_su = pattern.full_meas_su[~pattern.excluded]

    def show(self) -> None:
        # TODO: Consider moving this to the base class
        #  to avoid code duplication with implementations in Background, etc.
        #  Consider using parameter names as column headers
        columns_headers: List[str] = ['start', 'end']
        columns_alignment = ['left', 'left']
        columns_data: List[List[float]] = []
        for region in self._items.values():
            start = region.start.value
            end = region.end.value
            columns_data.append([start, end])

        print(paragraph('Excluded regions'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=columns_data,
        )
