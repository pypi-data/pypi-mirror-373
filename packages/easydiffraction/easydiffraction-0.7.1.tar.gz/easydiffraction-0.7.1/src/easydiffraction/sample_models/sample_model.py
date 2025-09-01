# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from easydiffraction.core.objects import Datablock
from easydiffraction.crystallography import crystallography as ecr
from easydiffraction.sample_models.collections.atom_sites import AtomSites
from easydiffraction.sample_models.components.cell import Cell
from easydiffraction.sample_models.components.space_group import SpaceGroup
from easydiffraction.utils.decorators import enforce_type
from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.utils import render_cif


class SampleModel(Datablock):
    """
    Represents an individual structural model of a sample.
    Wraps crystallographic information including space group, cell, and
    atomic sites.
    """

    # TODO: Move cif_path and cif_str out of __init__ and into separate methods
    def __init__(self, name: str, cif_path: str = None, cif_str: str = None):
        super().__init__()
        self._name = name
        self.space_group = SpaceGroup()
        self.cell = Cell()
        self.atom_sites = AtomSites()

        if cif_path:
            self.load_from_cif_file(cif_path)
        elif cif_str:
            self.load_from_cif_string(cif_str)

    # ----------------------
    # Name (ID) of the model
    # ----------------------

    @property
    def name(self):
        return self._name

    @name.setter
    @enforce_type
    def name(self, new_name: str):
        self._name = new_name

    # -----------
    # Space group
    # -----------

    @property
    def space_group(self):
        return self._space_group

    @space_group.setter
    @enforce_type
    def space_group(self, new_space_group: SpaceGroup):
        self._space_group = new_space_group

    # ----
    # Cell
    # ----

    @property
    def cell(self):
        return self._cell

    @cell.setter
    @enforce_type
    def cell(self, new_cell: Cell):
        self._cell = new_cell

    # ----------
    # Atom sites
    # ----------

    @property
    def atom_sites(self):
        return self._atom_sites

    @atom_sites.setter
    @enforce_type
    def atom_sites(self, new_atom_sites: AtomSites):
        self._atom_sites = new_atom_sites

    # --------------------
    # Symmetry constraints
    # --------------------

    def _apply_cell_symmetry_constraints(self):
        dummy_cell = {
            'lattice_a': self.cell.length_a.value,
            'lattice_b': self.cell.length_b.value,
            'lattice_c': self.cell.length_c.value,
            'angle_alpha': self.cell.angle_alpha.value,
            'angle_beta': self.cell.angle_beta.value,
            'angle_gamma': self.cell.angle_gamma.value,
        }
        space_group_name = self.space_group.name_h_m.value
        ecr.apply_cell_symmetry_constraints(cell=dummy_cell, name_hm=space_group_name)
        self.cell.length_a.value = dummy_cell['lattice_a']
        self.cell.length_b.value = dummy_cell['lattice_b']
        self.cell.length_c.value = dummy_cell['lattice_c']
        self.cell.angle_alpha.value = dummy_cell['angle_alpha']
        self.cell.angle_beta.value = dummy_cell['angle_beta']
        self.cell.angle_gamma.value = dummy_cell['angle_gamma']

    def _apply_atomic_coordinates_symmetry_constraints(self):
        space_group_name = self.space_group.name_h_m.value
        space_group_coord_code = self.space_group.it_coordinate_system_code.value
        for atom in self.atom_sites:
            dummy_atom = {
                'fract_x': atom.fract_x.value,
                'fract_y': atom.fract_y.value,
                'fract_z': atom.fract_z.value,
            }
            wl = atom.wyckoff_letter.value
            if not wl:
                # raise ValueError("Wyckoff letter is not defined for atom.")
                continue
            ecr.apply_atom_site_symmetry_constraints(
                atom_site=dummy_atom,
                name_hm=space_group_name,
                coord_code=space_group_coord_code,
                wyckoff_letter=wl,
            )
            atom.fract_x.value = dummy_atom['fract_x']
            atom.fract_y.value = dummy_atom['fract_y']
            atom.fract_z.value = dummy_atom['fract_z']

    def _apply_atomic_displacement_symmetry_constraints(self):
        pass

    def apply_symmetry_constraints(self):
        self._apply_cell_symmetry_constraints()
        self._apply_atomic_coordinates_symmetry_constraints()
        self._apply_atomic_displacement_symmetry_constraints()

    # -----------------
    # Creation from CIF
    # -----------------

    def load_from_cif_file(self, cif_path: str):
        """Load model data from a CIF file."""
        # TODO: Implement CIF parsing here
        print(f'Loading SampleModel from CIF file: {cif_path}')
        # Example: self.id = extract_id_from_cif(cif_path)

    def load_from_cif_string(self, cif_str: str):
        """Load model data from a CIF string."""
        # TODO: Implement CIF parsing from a string
        print('Loading SampleModel from CIF string.')

    # -----------------
    # Convertion to CIF
    # -----------------

    def as_cif(self) -> str:
        """
        Export the sample model to CIF format.
        Returns:
            str: CIF string representation of the sample model.
        """
        # Data block header
        cif_lines = [f'data_{self.name}']

        # Space Group
        cif_lines += ['', self.space_group.as_cif()]

        # Unit Cell
        cif_lines += ['', self.cell.as_cif()]

        # Atom Sites
        cif_lines += ['', self.atom_sites.as_cif()]

        return '\n'.join(cif_lines)

    # ------------
    # Show methods
    # ------------

    def show_structure(self, plane='xy', grid_size=20):
        """
        Show an ASCII projection of the structure on a 2D plane.

        Args:
            plane (str): 'xy', 'xz', or 'yz' plane to project.
            grid_size (int): Size of the ASCII grid (default is 20).
        """

        print(paragraph(f"Sample model 🧩 '{self.name}' structure view"))
        print('Not implemented yet.')

    def show_params(self):
        """Display structural parameters (space group, unit cell, atomic sites)."""
        print(f'\nSampleModel ID: {self.name}')
        print(f'Space group: {self.space_group.name_h_m}')
        print(f'Cell parameters: {self.cell.as_dict()}')
        print('Atom sites:')
        self.atom_sites.show()

    def show_as_cif(self) -> None:
        cif_text: str = self.as_cif()
        paragraph_title: str = paragraph(f"Sample model 🧩 '{self.name}' as cif")
        render_cif(cif_text, paragraph_title)
