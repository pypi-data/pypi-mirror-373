# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from easydiffraction.core.objects import Collection
from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Descriptor
from easydiffraction.core.objects import Parameter


class AtomSite(Component):
    """
    Represents a single atom site within the crystal structure.
    """

    @property
    def category_key(self):
        return 'atom_sites'

    @property
    def cif_category_key(self):
        return 'atom_site'

    def __init__(
        self,
        label: str,
        type_symbol: str,
        fract_x: float,
        fract_y: float,
        fract_z: float,
        wyckoff_letter: str = None,
        occupancy: float = 1.0,
        b_iso: float = 0.0,
        adp_type: str = 'Biso',
    ):  # TODO: add support for Uiso, Uani and Bani
        super().__init__()

        self.label = Descriptor(
            value=label,
            name='label',
            cif_name='label',
        )
        self.type_symbol = Descriptor(
            value=type_symbol,
            name='type_symbol',
            cif_name='type_symbol',
        )
        self.adp_type = Descriptor(
            value=adp_type,
            name='adp_type',
            cif_name='ADP_type',
        )
        self.wyckoff_letter = Descriptor(
            value=wyckoff_letter,
            name='wyckoff_letter',
            cif_name='Wyckoff_letter',
        )
        self.fract_x = Parameter(
            value=fract_x,
            name='fract_x',
            cif_name='fract_x',
        )
        self.fract_y = Parameter(
            value=fract_y,
            name='fract_y',
            cif_name='fract_y',
        )
        self.fract_z = Parameter(
            value=fract_z,
            name='fract_z',
            cif_name='fract_z',
        )
        self.occupancy = Parameter(
            value=occupancy,
            name='occupancy',
            cif_name='occupancy',
        )
        self.b_iso = Parameter(
            value=b_iso,
            name='b_iso',
            units='Å²',
            cif_name='B_iso_or_equiv',
        )
        # Select which of the input parameters is used for the
        # as ID for the whole object
        self._entry_id = label

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked = True


class AtomSites(Collection):
    """
    Collection of AtomSite instances.
    """

    # TODO: Check, if we can get rid of this property
    #  We could use class name instead
    @property
    def _type(self):
        return 'category'  # datablock or category

    @property
    def _child_class(self):
        return AtomSite
