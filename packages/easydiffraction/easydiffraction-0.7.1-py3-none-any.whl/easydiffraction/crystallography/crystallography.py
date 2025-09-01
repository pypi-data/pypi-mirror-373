# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any
from typing import Dict
from typing import List

from cryspy.A_functions_base.function_2_space_group import get_crystal_system_by_it_number
from cryspy.A_functions_base.function_2_space_group import get_it_number_by_name_hm_short
from sympy import Expr
from sympy import Symbol
from sympy import simplify
from sympy import symbols
from sympy import sympify

from easydiffraction.crystallography.space_group_lookup_table import SPACE_GROUP_LOOKUP_DICT


def apply_cell_symmetry_constraints(
    cell: Dict[str, float],
    name_hm: str,
) -> Dict[str, float]:
    """
    Apply symmetry constraints to unit cell parameters based on space group.

    Args:
        cell: Dictionary containing lattice parameters.
        name_hm: Hermann-Mauguin symbol of the space group.

    Returns:
        The cell dictionary with applied symmetry constraints.
    """
    it_number = get_it_number_by_name_hm_short(name_hm)
    if it_number is None:
        error_msg = f"Failed to get IT_number for name_H-M '{name_hm}'"
        print(error_msg)
        return cell

    crystal_system = get_crystal_system_by_it_number(it_number)
    if crystal_system is None:
        error_msg = f"Failed to get crystal system for IT_number '{it_number}'"
        print(error_msg)
        return cell

    if crystal_system == 'cubic':
        a = cell['lattice_a']
        cell['lattice_b'] = a
        cell['lattice_c'] = a
        cell['angle_alpha'] = 90
        cell['angle_beta'] = 90
        cell['angle_gamma'] = 90

    elif crystal_system == 'tetragonal':
        a = cell['lattice_a']
        cell['lattice_b'] = a
        cell['angle_alpha'] = 90
        cell['angle_beta'] = 90
        cell['angle_gamma'] = 90

    elif crystal_system == 'orthorhombic':
        cell['angle_alpha'] = 90
        cell['angle_beta'] = 90
        cell['angle_gamma'] = 90

    elif crystal_system in {'hexagonal', 'trigonal'}:
        a = cell['lattice_a']
        cell['lattice_b'] = a
        cell['angle_alpha'] = 90
        cell['angle_beta'] = 90
        cell['angle_gamma'] = 120

    elif crystal_system == 'monoclinic':
        cell['angle_alpha'] = 90
        cell['angle_gamma'] = 90

    elif crystal_system == 'triclinic':
        pass  # No constraints to apply

    else:
        error_msg = f'Unknown or unsupported crystal system: {crystal_system}'
        print(error_msg)

    return cell


def apply_atom_site_symmetry_constraints(
    atom_site: Dict[str, Any],
    name_hm: str,
    coord_code: int,
    wyckoff_letter: str,
) -> Dict[str, Any]:
    """
    Apply symmetry constraints to atomic coordinates based on site symmetry.

    Args:
        atom_site: Dictionary containing atom position data.
        name_hm: Hermann-Mauguin symbol of the space group.
        coord_code: Coordinate system code.
        wyckoff_letter: Wyckoff position letter.

    Returns:
        The atom_site dictionary with applied symmetry constraints.
    """
    it_number = get_it_number_by_name_hm_short(name_hm)
    if it_number is None:
        error_msg = f"Failed to get IT_number for name_H-M '{name_hm}'"
        print(error_msg)
        return atom_site

    it_coordinate_system_code = coord_code
    if it_coordinate_system_code is None:
        error_msg = 'IT_coordinate_system_code is not set'
        print(error_msg)
        return atom_site

    space_group_entry = SPACE_GROUP_LOOKUP_DICT[(it_number, it_coordinate_system_code)]
    wyckoff_positions = space_group_entry['Wyckoff_positions'][wyckoff_letter]
    coords_xyz = wyckoff_positions['coords_xyz']

    first_position = coords_xyz[0]
    components = first_position.strip('()').split(',')
    parsed_exprs: List[Expr] = [sympify(comp.strip()) for comp in components]

    x_val: Expr = sympify(atom_site['fract_x'])
    y_val: Expr = sympify(atom_site['fract_y'])
    z_val: Expr = sympify(atom_site['fract_z'])

    substitutions: Dict[str, Expr] = {'x': x_val, 'y': y_val, 'z': z_val}

    axes: tuple[str, ...] = ('x', 'y', 'z')
    x, y, z = symbols('x y z')
    symbols_xyz: tuple[Symbol, ...] = (x, y, z)

    for i, axis in enumerate(axes):
        symbol = symbols_xyz[i]
        is_free = any(symbol in expr.free_symbols for expr in parsed_exprs)

        if not is_free:
            evaluated = parsed_exprs[i].subs(substitutions)
            simplified = simplify(evaluated)
            atom_site[f'fract_{axis}'] = float(simplified)

    return atom_site
